"""
LLM 응답 → 정규화된 구조체 변환 및 유효성 검증
"""
from base.utils import get_logger

logger = get_logger("timeline_extractor")

VALID_PATTERN_TYPES = {"AOE", "Target", "Wipe", "Puzzle", "Movement", "Mechanic"}
VALID_DIFFICULTIES = {"Low", "Medium", "High"}
VALID_MONSTER_TYPES = {"Raid", "Dungeon", "Field", "Elite"}


def parse_extraction(raw: dict) -> dict | None:
    """
    LLM 추출 결과를 검증하고 정규화.
    필수 필드 누락 시 None 반환.
    """
    if not raw:
        return None

    game = raw.get("game", "").strip()
    boss_name = raw.get("boss_name", "").strip()

    if not game or not boss_name:
        logger.warning("필수 필드 누락 - game 또는 boss_name이 없음")
        return None

    timeline = _parse_timeline(raw.get("timeline", []))
    if not timeline:
        logger.warning(f"타임라인 없음 - game: {game}, boss: {boss_name}")
        return None

    return {
        "game": game,
        "boss_name": boss_name,
        "raid": raw.get("raid", ""),
        "monster_type": _normalize_enum(raw.get("monster_type", "Raid"), VALID_MONSTER_TYPES, "Raid"),
        "boss_fun_type": raw.get("boss_fun_type", []),
        "design_reference_tags": raw.get("design_reference_tags", []),
        "timeline": timeline,
        "mechanic_complexity": _clamp_score(raw.get("mechanic_complexity")),
        "mechanic_complexity_reasoning": raw.get("mechanic_complexity_reasoning", ""),
    }


def _parse_timeline(raw_timeline: list) -> list[dict]:
    """타임라인 배열 정규화 및 정렬"""
    if not isinstance(raw_timeline, list):
        return []

    parsed = []
    for entry in raw_timeline:
        if not isinstance(entry, dict):
            continue
        hp = entry.get("hp_percent")
        name = entry.get("pattern_name", "").strip()
        if hp is None or not name:
            continue

        parsed.append({
            "hp_percent": _clamp_hp(hp),
            "pattern_name": name,
            "pattern_type": _normalize_enum(
                entry.get("pattern_type", "AOE"), VALID_PATTERN_TYPES, "AOE"
            ),
            "difficulty": _normalize_enum(
                entry.get("difficulty", "Medium"), VALID_DIFFICULTIES, "Medium"
            ),
            "reaction_window_sec": _safe_float(entry.get("reaction_window_sec"), 2.0),
            "failure_penalty": entry.get("failure_penalty", ""),
            "success_reward": entry.get("success_reward", ""),
            "notes": entry.get("notes", ""),
        })

    return sorted(parsed, key=lambda x: x["hp_percent"], reverse=True)


def _normalize_enum(value: str, valid_set: set, default: str) -> str:
    if isinstance(value, str) and value in valid_set:
        return value
    return default


def _clamp_hp(value) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 100


def _clamp_score(value) -> int | None:
    if value is None:
        return None
    try:
        return max(1, min(10, int(value)))
    except (TypeError, ValueError):
        return None


def _safe_float(value, default: float) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return default
