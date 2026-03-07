"""
YouTube 영상 댓글 샘플링 (좋아요 상위 N개)
"""
import os

from base.utils import get_logger

logger = get_logger("collector")


def sample_comments(youtube_client, video_id: str) -> list[str]:
    """
    YouTube video_id → 좋아요 상위 댓글 텍스트 목록 반환.
    댓글 비활성화 또는 수집 실패 시 빈 리스트 반환.
    """
    max_results = int(os.getenv("YOUTUBE_COMMENT_SAMPLE_SIZE", "20"))

    try:
        response = youtube_client.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=max_results,
            textFormat="plainText",
        ).execute()

        comments = [
            item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            for item in response.get("items", [])
        ]
        logger.info(f"댓글 수집 완료 - video_id: {video_id}, {len(comments)}개")
        return comments

    except Exception as e:
        logger.warning(f"댓글 수집 실패 - video_id: {video_id}, error: {e}")
        return []
