"""
monsters.json, patterns.json, videos.json upsert 저장
"""
from datetime import date

from base.utils import DATA_DIR, get_logger, load_json, save_json

logger = get_logger("db_writer")

MONSTERS_PATH = DATA_DIR / "monsters.json"
PATTERNS_PATH = DATA_DIR / "patterns.json"
VIDEOS_PATH = DATA_DIR / "videos.json"

TODAY = date.today().isoformat()


def upsert_monster(monster: dict) -> None:
    """monster_id 기준 upsert"""
    records = load_json(MONSTERS_PATH)
    monster_id = monster["id"]

    idx = next((i for i, r in enumerate(records) if r.get("id") == monster_id), None)

    if idx is not None:
        updated = {**records[idx], **monster, "last_updated": TODAY}
        new_records = records[:idx] + [updated] + records[idx + 1:]
        logger.info(f"몬스터 업데이트 - id: {monster_id}")
    else:
        new_record = {**monster, "last_updated": TODAY}
        new_records = records + [new_record]
        logger.info(f"몬스터 신규 추가 - id: {monster_id}")

    save_json(MONSTERS_PATH, new_records)


def upsert_patterns(patterns_entry: dict) -> None:
    """
    monster_id 기준 upsert.
    기존 타임라인에 새 패턴 추가 (hp_percent + pattern_name 중복 방지).
    """
    records = load_json(PATTERNS_PATH)
    monster_id = patterns_entry["monster_id"]
    new_timeline = patterns_entry.get("timeline", [])

    idx = next((i for i, r in enumerate(records) if r.get("monster_id") == monster_id), None)

    if idx is not None:
        merged_timeline = _merge_timeline(records[idx].get("timeline", []), new_timeline)
        updated = {
            **records[idx],
            "source_video_id": patterns_entry.get("source_video_id", ""),
            "timeline": merged_timeline,
            "last_updated": TODAY,
        }
        new_records = records[:idx] + [updated] + records[idx + 1:]
        logger.info(f"패턴 업데이트 - monster_id: {monster_id}, 총 패턴: {len(merged_timeline)}")
    else:
        new_record = {
            "monster_id": monster_id,
            "source_video_id": patterns_entry.get("source_video_id", ""),
            "timeline": new_timeline,
            "extracted_at": TODAY,
            "last_updated": TODAY,
        }
        new_records = records + [new_record]
        logger.info(f"패턴 신규 추가 - monster_id: {monster_id}, 패턴: {len(new_timeline)}")

    save_json(PATTERNS_PATH, new_records)


def upsert_video(video: dict) -> None:
    """youtube_id 기준 upsert"""
    records = load_json(VIDEOS_PATH)
    youtube_id = video["youtube_id"]

    idx = next((i for i, r in enumerate(records) if r.get("youtube_id") == youtube_id), None)

    if idx is not None:
        updated = {**records[idx], **video, "collected_at": records[idx].get("collected_at", TODAY)}
        new_records = records[:idx] + [updated] + records[idx + 1:]
        logger.info(f"영상 업데이트 - youtube_id: {youtube_id}, status: {video.get('analysis_status')}")
    else:
        new_record = {**video, "collected_at": TODAY}
        new_records = records + [new_record]
        logger.info(f"영상 신규 추가 - youtube_id: {youtube_id}")

    save_json(VIDEOS_PATH, new_records)


def is_video_already_processed(youtube_id: str) -> bool:
    """이미 completed 처리된 영상이면 True"""
    records = load_json(VIDEOS_PATH)
    return any(
        r.get("youtube_id") == youtube_id and r.get("analysis_status") == "completed"
        for r in records
    )


def _merge_timeline(existing: list, new_entries: list) -> list:
    """기존 타임라인에 새 패턴 추가 (hp_percent + pattern_name 중복 방지)"""
    existing_keys = {
        (e.get("hp_percent"), e.get("pattern_name")) for e in existing
    }
    added = [
        e for e in new_entries
        if (e.get("hp_percent"), e.get("pattern_name")) not in existing_keys
    ]
    merged = existing + added
    return sorted(merged, key=lambda x: x.get("hp_percent", 0), reverse=True)
