"""
Claude API를 사용한 보스 패턴 타임라인 추출
"""
import json
import os

import anthropic

from base.utils import get_env, get_logger

logger = get_logger("timeline_extractor")

EXTRACTION_PROMPT = """You are an expert MMORPG game analyst specializing in boss fight mechanics.
Analyze the following YouTube video content about an MMORPG boss fight.

Video Title: {title}

Description:
{description}

Subtitles:
{subtitle}

Top Comments:
{comments}

Extract and return ONLY valid JSON with this exact structure:
{{
  "game": "exact game name (e.g. Lost Ark, Final Fantasy XIV, World of Warcraft)",
  "boss_name": "exact boss name",
  "raid": "raid or dungeon name if mentioned, else empty string",
  "monster_type": "Raid or Dungeon or Field or Elite",
  "boss_fun_type": ["one or more from: Reaction Boss, Puzzle Boss, Team Coordination Boss, Bullet Hell Boss, Punishment Boss, Spectacle Boss"],
  "design_reference_tags": ["zero or more from: dark_souls_style, monster_hunter_style, bullet_hell, cinematic_boss, reaction_test"],
  "timeline": [
    {{
      "hp_percent": 100,
      "pattern_name": "pattern name",
      "pattern_type": "AOE or Target or Wipe or Puzzle or Movement or Mechanic",
      "difficulty": "Low or Medium or High",
      "reaction_window_sec": 2.0,
      "failure_penalty": "what happens on failure",
      "success_reward": "what happens on success",
      "notes": "additional notes or empty string"
    }}
  ],
  "mechanic_complexity": 5,
  "mechanic_complexity_reasoning": "brief one-line explanation"
}}

Rules:
- Sort timeline by hp_percent DESCENDING (100 first, lower last)
- Infer hp_percent from context: "phase 2" ≈ 70%, "half hp" = 50%, "enrage" ≈ 10-20%
- mechanic_complexity scale: 1-3=simple AOE, 4-6=standard raid, 7-8=complex mechanics, 9-10=puzzle/coordination
- Return null if there is not enough information to identify the game and boss

Return ONLY the JSON object or null. No markdown, no explanation."""


def extract_pattern_timeline(video_data: dict) -> dict | None:
    """
    수집된 영상 텍스트 데이터 → 구조화된 패턴 타임라인.
    추출 실패 시 None 반환.
    """
    prompt = _build_prompt(video_data)
    model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")

    result = _call_claude(prompt, model)
    if result is None:
        logger.warning(
            f"LLM 추출 실패 - video_id: {video_data.get('youtube_id')}"
        )
    else:
        logger.info(
            f"패턴 추출 완료 - video_id: {video_data.get('youtube_id')}, "
            f"game: {result.get('game')}, boss: {result.get('boss_name')}, "
            f"패턴 수: {len(result.get('timeline', []))}"
        )
    return result


def _build_prompt(video_data: dict) -> str:
    subtitle_text = video_data.get("subtitle") or "(자막 없음)"
    comments = video_data.get("comments", [])
    comments_text = "\n".join(f"- {c}" for c in comments[:20]) if comments else "(댓글 없음)"

    description = video_data.get("description", "")[:3000]

    return EXTRACTION_PROMPT.format(
        title=video_data.get("title", ""),
        description=description,
        subtitle=subtitle_text[:4000] if subtitle_text else "(자막 없음)",
        comments=comments_text,
    )


def _call_claude(prompt: str, model: str) -> dict | None:
    """Claude API 호출 → 파싱된 dict 또는 None"""
    try:
        api_key = get_env("CLAUDE_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        if raw.lower() == "null":
            return None

        return json.loads(raw)

    except json.JSONDecodeError as e:
        logger.error(f"Claude 응답 JSON 파싱 실패: {e}")
        return None
    except Exception as e:
        logger.error(f"Claude API 호출 실패: {e}")
        return None
