"""
YouTube 영상 검색 및 engagement 점수 기반 정렬
"""
import os
from datetime import datetime, timezone

from googleapiclient.discovery import build

from base.utils import get_env, get_logger

logger = get_logger("collector")

SEARCH_KEYWORDS = [
    "MMORPG raid boss fight",
    "MMO boss mechanics guide",
    "raid boss wipe mechanic",
    "hard raid boss",
    "raid boss strategy",
]

MAX_RESULTS_PER_KEYWORD = 10


def build_youtube_client():
    """YouTube Data API 클라이언트 생성"""
    api_key = get_env("YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=api_key)


def search_boss_videos(youtube_client, max_per_keyword: int = MAX_RESULTS_PER_KEYWORD) -> list[str]:
    """
    키워드 검색 후 engagement 점수 기준 정렬된 video_id 목록 반환.
    중복 제거 후 상위 결과 반환.
    """
    min_views = int(os.getenv("YOUTUBE_MIN_VIEWS", "10000"))
    seen_ids = set()
    candidates = []

    for keyword in SEARCH_KEYWORDS:
        try:
            video_ids = _search_keyword(youtube_client, keyword, max_per_keyword)
            for vid in video_ids:
                if vid not in seen_ids:
                    seen_ids.add(vid)
                    candidates.append(vid)
        except Exception as e:
            logger.error(f"키워드 검색 실패 - keyword: '{keyword}', error: {e}")

    logger.info(f"검색 완료 - 총 {len(candidates)}개 영상 후보")
    return candidates


def _search_keyword(youtube_client, keyword: str, max_results: int) -> list[str]:
    """단일 키워드로 YouTube 검색 → video_id 목록"""
    logger.info(f"검색 시작 - keyword: '{keyword}'")
    response = youtube_client.search().list(
        part="id",
        q=keyword,
        type="video",
        videoCategoryId="20",  # Gaming
        order="relevance",
        maxResults=max_results,
        relevanceLanguage="en",
    ).execute()

    video_ids = [
        item["id"]["videoId"]
        for item in response.get("items", [])
        if item["id"].get("kind") == "youtube#video"
    ]
    logger.info(f"검색 결과 - keyword: '{keyword}', 영상: {len(video_ids)}개")
    return video_ids


def rank_by_engagement(videos_metadata: list[dict]) -> list[dict]:
    """
    영상 메타데이터 목록을 engagement 점수 기준 내림차순 정렬.
    score = (view_count * 0.6) + (comment_count * 100 * 0.4)
    최근 1년 이내 업로드: +10% 가중치
    """
    def score(video: dict) -> float:
        view_count = video.get("view_count", 0)
        comment_count = video.get("comment_count", 0)
        base = (view_count * 0.6) + (comment_count * 100 * 0.4)

        upload_date = video.get("upload_date", "")
        if upload_date:
            try:
                uploaded = datetime.fromisoformat(upload_date.replace("Z", "+00:00"))
                now = datetime.now(tz=timezone.utc)
                days_ago = (now - uploaded).days
                if days_ago < 365:
                    base *= 1.1
            except ValueError:
                pass

        return base

    return sorted(videos_metadata, key=score, reverse=True)
