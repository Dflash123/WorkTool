"""
YouTube 영상 메타데이터 및 description 수집
"""
import re

from base.utils import get_logger

logger = get_logger("collector")


def collect_metadata(youtube_client, video_id: str) -> dict | None:
    """
    YouTube video_id → 메타데이터 dict 반환.
    조회 실패 시 None 반환.
    """
    try:
        response = youtube_client.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id,
        ).execute()

        items = response.get("items", [])
        if not items:
            logger.warning(f"영상 없음 - video_id: {video_id}")
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        metadata = {
            "youtube_id": video_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description": snippet.get("description", ""),
            "view_count": int(statistics.get("viewCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
            "duration_seconds": _parse_duration(content_details.get("duration", "")),
            "upload_date": snippet.get("publishedAt", "")[:10],
        }
        logger.info(
            f"메타데이터 수집 완료 - video_id: {video_id}, "
            f"views: {metadata['view_count']:,}, title: {metadata['title'][:50]}"
        )
        return metadata

    except Exception as e:
        logger.error(f"메타데이터 수집 실패 - video_id: {video_id}, error: {e}")
        return None


def is_min_views_met(metadata: dict, min_views: int) -> bool:
    """조회수 최소 기준 충족 여부"""
    return metadata.get("view_count", 0) >= min_views


def _parse_duration(duration: str) -> int:
    """ISO 8601 duration (PT10M30S) → seconds"""
    if not duration:
        return 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds
