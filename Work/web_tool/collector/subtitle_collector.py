"""
YouTube 영상 자막 수집 (없으면 None 반환)
"""
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from base.utils import get_logger

logger = get_logger("collector")

PREFERRED_LANGUAGES = ["en", "ko", "ja"]


def collect_subtitle(video_id: str) -> str | None:
    """
    YouTube video_id → 자막 텍스트 반환.
    자막 없거나 비활성화된 경우 None 반환.
    youtube-transcript-api 1.x: 인스턴스 메서드 사용
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list_transcripts(video_id)

        transcript = _find_best_transcript(transcript_list)
        if transcript is None:
            logger.info(f"자막 없음 - video_id: {video_id}")
            return None

        entries = transcript.fetch()
        text = " ".join(
            entry.get("text", "") if isinstance(entry, dict) else str(entry)
            for entry in entries
        )
        logger.info(f"자막 수집 완료 - video_id: {video_id}, 길이: {len(text)}자")
        return text

    except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound):
        logger.info(f"자막 불가 - video_id: {video_id}")
        return None
    except Exception as e:
        logger.warning(f"자막 수집 오류 - video_id: {video_id}, error: {e}")
        return None


def _find_best_transcript(transcript_list):
    """선호 언어 순서로 자막 탐색 (수동 > 자동생성 순)"""
    for lang in PREFERRED_LANGUAGES:
        try:
            return transcript_list.find_manually_created_transcript([lang])
        except NoTranscriptFound:
            pass

    for lang in PREFERRED_LANGUAGES:
        try:
            return transcript_list.find_generated_transcript([lang])
        except NoTranscriptFound:
            pass

    return None
