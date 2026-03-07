"""
공통 유틸리티 — collector, timeline_extractor 공유 사용
"""
import json
import logging
import os
import tempfile
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"


def get_logger(name: str) -> logging.Logger:
    """툴 이름을 태깅한 로거 생성 (콘솔 + 파일)"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"collector_{date.today().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_env(key: str, default: str = None) -> str:
    """환경변수 로드. default 없으면 없을 때 에러 발생."""
    value = os.getenv(key, default)
    if value is None:
        raise EnvironmentError(
            f"환경변수 {key}가 설정되지 않았습니다. .env 파일을 확인하세요."
        )
    return value


def load_json(path: Path) -> list:
    """JSON 파일 로드. 파일 없거나 비어있으면 빈 리스트 반환."""
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        get_logger("base.utils").warning(f"JSON 로드 실패 - {path}: {e}")
        return []


def save_json(path: Path, data: list) -> None:
    """JSON 파일 원자적 저장 (임시파일 → 이름변경)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
