"""
설정 로더 - config.yaml을 읽어 전체 앱에 제공
"""
import os
import yaml
from pathlib import Path
from typing import Any


# 프로젝트 루트 경로
ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT_DIR / "src" / "config" / "config.yaml"


class Settings:
    """config.yaml 기반 설정 관리자"""

    def __init__(self):
        self._config = self._load()

    def _load(self) -> dict:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"config.yaml을 찾을 수 없습니다: {CONFIG_PATH}")
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, *keys: str, default: Any = None) -> Any:
        """중첩 키 접근: get('google_sheets', 'spreadsheet_id')"""
        value = self._config
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key, default)
        return value

    # --- Google Sheets ---
    @property
    def credentials_file(self) -> Path:
        rel_path = self.get("google_sheets", "credentials_file", default="credentials/service_account.json")
        return ROOT_DIR / rel_path

    @property
    def spreadsheet_id(self) -> str:
        return self.get("google_sheets", "spreadsheet_id", default="")

    @property
    def sheet_names(self) -> dict:
        return self.get("google_sheets", "sheets", default={
            "skill_definitions": "SkillDefinitions",
            "test_logs": "TestLogs",
            "player_feedback": "PlayerFeedback",
            "balance_history": "BalanceHistory",
        })

    # --- App ---
    @property
    def app_title(self) -> str:
        return self.get("app", "title", default="Monster Skill Analyzer")

    @property
    def app_version(self) -> str:
        return self.get("app", "version", default="1.0.0")

    @property
    def datetime_format(self) -> str:
        return self.get("app", "datetime_format", default="%Y-%m-%d %H:%M:%S")

    # --- Metrics 기준값 ---
    @property
    def reaction_reference_ms(self) -> int:
        return self.get("metrics", "reaction_reference_ms", default=500)

    @property
    def danger_thresholds(self) -> dict:
        return {
            "reaction_margin": self.get("metrics", "reaction_margin_danger", default=50),
            "fairness_score": self.get("metrics", "fairness_score_danger", default=40),
            "unfair_hit": self.get("metrics", "unfair_hit_danger", default=60),
            "design_intent": self.get("metrics", "design_intent_warning", default=70),
            "learnability": self.get("metrics", "learnability_warning", default=60),
        }

    def is_configured(self) -> bool:
        """Google Sheets 설정이 완료되었는지 확인"""
        return (
            self.spreadsheet_id != "YOUR_SPREADSHEET_ID_HERE"
            and self.spreadsheet_id != ""
            and self.credentials_file.exists()
        )

    def reload(self):
        """설정 파일 재로드 (설정 화면에서 저장 후 호출)"""
        self._config = self._load()


# 전역 싱글톤
settings = Settings()
