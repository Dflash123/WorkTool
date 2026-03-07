"""
data_collection_engine 메인 파이프라인 엔트리포인트
실행: python run_collector.py (web_tool/ 디렉토리에서)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base.utils import get_env, get_logger
from collector.comment_sampler import sample_comments
from collector.metadata_collector import collect_metadata, is_min_views_met
from collector.subtitle_collector import collect_subtitle
from collector.youtube_searcher import build_youtube_client, rank_by_engagement, search_boss_videos
from timeline_extractor.complexity_scorer import calculate_complexity
from timeline_extractor.db_writer import is_video_already_processed, upsert_monster, upsert_patterns, upsert_video
from timeline_extractor.llm_extractor import extract_pattern_timeline
from timeline_extractor.pattern_parser import parse_extraction

logger = get_logger("run_collector")


def generate_monster_id(game: str, boss_name: str) -> str:
    """게임명 + 보스명 → snake_case monster_id"""
    game_short_map = {
        "World of Warcraft": "wow",
        "Final Fantasy XIV": "ff14",
        "Lost Ark": "lostark",
        "Black Desert Online": "bdo",
        "Guild Wars 2": "gw2",
        "Elder Scrolls Online": "eso",
        "Blade and Soul": "bns",
        "TERA": "tera",
        "Aion": "aion",
        "MapleStory": "maplestory",
        "Lineage": "lineage",
        "New World": "newworld",
        "Albion Online": "albion",
        "ArcheAge": "archeage",
        "Ragnarok Online": "ragnarok",
        "Tree of Savior": "tos",
        "Dragon Nest": "dn",
        "Phantasy Star Online 2": "pso2",
        "Tower of Fantasy": "tof",
        "Blue Protocol": "blueprotocol",
    }
    short = game_short_map.get(game, game.lower().replace(" ", "_")[:10])
    boss_slug = (
        boss_name.lower()
        .replace(" ", "_")
        .replace("'", "")
        .replace("-", "_")
        .replace(":", "")
    )
    return f"{short}_{boss_slug}"


def is_analyzable(metadata: dict, subtitle: str | None, comments: list[str]) -> bool:
    """텍스트 데이터가 패턴 추출에 충분한지 판단"""
    description = metadata.get("description", "")
    if subtitle:
        return True
    if len(description) >= 100:
        return True
    if len(comments) >= 5:
        return True
    return False


def process_video(youtube_client, video_id: str, min_views: int) -> None:
    """단일 영상 처리 파이프라인"""
    if is_video_already_processed(video_id):
        logger.info(f"이미 처리된 영상 스킵 - video_id: {video_id}")
        return

    metadata = collect_metadata(youtube_client, video_id)
    if metadata is None:
        return

    if not is_min_views_met(metadata, min_views):
        logger.info(
            f"조회수 미달 스킵 - video_id: {video_id}, "
            f"views: {metadata.get('view_count', 0):,} (최소 {min_views:,})"
        )
        return

    subtitle = collect_subtitle(video_id)
    comments = sample_comments(youtube_client, video_id)

    if not is_analyzable(metadata, subtitle, comments):
        logger.info(f"텍스트 데이터 부족 스킵 - video_id: {video_id}")
        upsert_video({
            **metadata,
            "monster_id": "",
            "subtitle_available": False,
            "analysis_status": "skipped",
        })
        return

    video_data = {
        **metadata,
        "subtitle": subtitle,
        "comments": comments,
    }

    raw_extraction = extract_pattern_timeline(video_data)
    parsed = parse_extraction(raw_extraction) if raw_extraction else None

    if parsed is None:
        logger.warning(f"패턴 추출 실패 - video_id: {video_id}")
        upsert_video({
            **metadata,
            "monster_id": "",
            "subtitle_available": subtitle is not None,
            "analysis_status": "skipped",
        })
        return

    monster_id = generate_monster_id(parsed["game"], parsed["boss_name"])
    complexity = calculate_complexity(
        parsed["timeline"],
        llm_score=parsed.get("mechanic_complexity"),
    )

    upsert_monster({
        "id": monster_id,
        "name": parsed["boss_name"],
        "game": parsed["game"],
        "raid": parsed["raid"],
        "monster_type": parsed["monster_type"],
        "boss_fun_type": parsed["boss_fun_type"],
        "design_reference_tags": parsed["design_reference_tags"],
        "fun_factor_score": {
            "reaction": None,
            "teamplay": None,
            "mechanic_uniqueness": None,
            "visual_spectacle": None,
            "difficulty": None,
            "punishment": None,
        },
        "mechanic_complexity": complexity,
        "boss_ranking": {
            "difficulty_rank": None,
            "fun_rank": None,
            "composite_score": None,
        },
    })

    upsert_patterns({
        "monster_id": monster_id,
        "source_video_id": video_id,
        "timeline": parsed["timeline"],
    })

    upsert_video({
        **metadata,
        "monster_id": monster_id,
        "subtitle_available": subtitle is not None,
        "analysis_status": "completed",
    })

    logger.info(f"처리 완료 - video_id: {video_id}, monster: {monster_id}")


def main() -> None:
    logger.info("=== data_collection_engine 시작 ===")
    min_views = int(os.getenv("YOUTUBE_MIN_VIEWS", "10000"))

    try:
        youtube_client = build_youtube_client()
    except Exception as e:
        logger.error(f"YouTube 클라이언트 초기화 실패: {e}")
        sys.exit(1)

    video_ids = search_boss_videos(youtube_client)
    if not video_ids:
        logger.warning("검색 결과 없음 - 종료")
        return

    metadata_list = []
    for vid in video_ids:
        m = collect_metadata(youtube_client, vid)
        if m:
            metadata_list.append(m)

    ranked = rank_by_engagement(metadata_list)
    logger.info(f"engagement 점수 정렬 완료 - {len(ranked)}개 영상 처리 예정")

    success = 0
    failed = 0
    for meta in ranked:
        video_id = meta["youtube_id"]
        try:
            process_video(youtube_client, video_id, min_views)
            success += 1
        except Exception as e:
            logger.error(f"영상 처리 중 예외 - video_id: {video_id}, error: {e}")
            failed += 1

    logger.info(
        f"=== 수집 완료 - 성공: {success}, 실패: {failed}, 전체: {len(ranked)} ==="
    )


if __name__ == "__main__":
    main()
