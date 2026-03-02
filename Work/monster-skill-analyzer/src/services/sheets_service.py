"""
Google Sheets 서비스 레이어
- gspread 라이브러리 사용
- 인터페이스 기반: 나중에 DB로 교체 시 이 파일만 교체
- 헤더 자동 생성, 행 추가/조회/수정/삭제
"""
from __future__ import annotations
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional
import streamlit as st

from src.config.settings import settings
from src.modules.data_models import (
    SkillDefinition, TestLog, PlayerFeedback, BalanceHistory
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsService:
    """Google Sheets CRUD 서비스"""

    def __init__(self):
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None

    def connect(self) -> bool:
        """Google Sheets 연결. 성공 시 True 반환."""
        try:
            creds = Credentials.from_service_account_file(
                str(settings.credentials_file), scopes=SCOPES
            )
            self._client = gspread.authorize(creds)
            self._spreadsheet = self._client.open_by_key(settings.spreadsheet_id)
            self._ensure_sheets()
            return True
        except FileNotFoundError:
            st.error(f"인증 파일을 찾을 수 없습니다: {settings.credentials_file}")
            return False
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("Spreadsheet ID가 잘못되었습니다. config.yaml을 확인하세요.")
            return False
        except Exception as e:
            st.error(f"Google Sheets 연결 실패: {e}")
            return False

    def _ensure_sheets(self):
        """필요한 시트가 없으면 자동 생성 + 헤더 추가"""
        sheet_names = settings.sheet_names
        existing = [ws.title for ws in self._spreadsheet.worksheets()]

        configs = [
            (sheet_names["skill_definitions"], SkillDefinition.headers()),
            (sheet_names["test_logs"], TestLog.headers()),
            (sheet_names["player_feedback"], PlayerFeedback.headers()),
            (sheet_names["balance_history"], BalanceHistory.headers()),
        ]

        for name, headers in configs:
            if name not in existing:
                ws = self._spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
                ws.append_row(headers)

    def _get_sheet(self, sheet_key: str) -> gspread.Worksheet:
        name = settings.sheet_names[sheet_key]
        return self._spreadsheet.worksheet(name)

    # ─────────────────────────────────────────
    # SkillDefinitions
    # ─────────────────────────────────────────
    def add_skill(self, skill: SkillDefinition) -> bool:
        try:
            skill.compute()
            self._get_sheet("skill_definitions").append_row(skill.to_row())
            return True
        except Exception as e:
            st.error(f"스킬 저장 실패: {e}")
            return False

    def get_all_skills(self) -> list[SkillDefinition]:
        try:
            rows = self._get_sheet("skill_definitions").get_all_values()
            return [SkillDefinition.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception as e:
            st.error(f"스킬 조회 실패: {e}")
            return []

    def update_skill(self, skill: SkillDefinition) -> bool:
        try:
            ws = self._get_sheet("skill_definitions")
            rows = ws.get_all_values()
            for idx, row in enumerate(rows[1:], start=2):
                if row and row[0] == skill.skill_id:
                    skill.compute()
                    ws.update(f"A{idx}:Y{idx}", [skill.to_row()])
                    return True
            st.warning("수정할 스킬을 찾을 수 없습니다.")
            return False
        except Exception as e:
            st.error(f"스킬 수정 실패: {e}")
            return False

    def delete_skill(self, skill_id: str) -> bool:
        try:
            ws = self._get_sheet("skill_definitions")
            rows = ws.get_all_values()
            for idx, row in enumerate(rows[1:], start=2):
                if row and row[0] == skill_id:
                    ws.delete_rows(idx)
                    return True
            return False
        except Exception as e:
            st.error(f"스킬 삭제 실패: {e}")
            return False

    # ─────────────────────────────────────────
    # TestLogs
    # ─────────────────────────────────────────
    def add_test_log(self, log: TestLog) -> bool:
        try:
            self._get_sheet("test_logs").append_row(log.to_row())
            return True
        except Exception as e:
            st.error(f"테스트 로그 저장 실패: {e}")
            return False

    def get_all_test_logs(self) -> list[TestLog]:
        try:
            rows = self._get_sheet("test_logs").get_all_values()
            return [TestLog.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception as e:
            st.error(f"테스트 로그 조회 실패: {e}")
            return []

    def get_logs_by_skill(self, skill_id: str) -> list[TestLog]:
        return [log for log in self.get_all_test_logs() if log.skill_id == skill_id]

    # ─────────────────────────────────────────
    # PlayerFeedback
    # ─────────────────────────────────────────
    def add_feedback(self, feedback: PlayerFeedback) -> bool:
        try:
            self._get_sheet("player_feedback").append_row(feedback.to_row())
            return True
        except Exception as e:
            st.error(f"체감 평가 저장 실패: {e}")
            return False

    def get_all_feedbacks(self) -> list[PlayerFeedback]:
        try:
            rows = self._get_sheet("player_feedback").get_all_values()
            return [PlayerFeedback.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception as e:
            st.error(f"체감 평가 조회 실패: {e}")
            return []

    def get_feedbacks_by_skill(self, skill_id: str) -> list[PlayerFeedback]:
        return [f for f in self.get_all_feedbacks() if f.skill_id == skill_id]

    # ─────────────────────────────────────────
    # BalanceHistory
    # ─────────────────────────────────────────
    def add_history(self, history: BalanceHistory) -> bool:
        try:
            self._get_sheet("balance_history").append_row(history.to_row())
            return True
        except Exception as e:
            st.error(f"히스토리 저장 실패: {e}")
            return False

    def get_history_by_skill(self, skill_id: str) -> list[BalanceHistory]:
        try:
            rows = self._get_sheet("balance_history").get_all_values()
            all_history = [BalanceHistory.from_row(r) for r in rows[1:] if r and r[0]]
            return [h for h in all_history if h.skill_id == skill_id]
        except Exception as e:
            st.error(f"히스토리 조회 실패: {e}")
            return []

    def get_all_history(self) -> list[BalanceHistory]:
        try:
            rows = self._get_sheet("balance_history").get_all_values()
            return [BalanceHistory.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception as e:
            st.error(f"히스토리 조회 실패: {e}")
            return []

    @property
    def is_connected(self) -> bool:
        return self._spreadsheet is not None


@st.cache_resource
def get_sheets_service() -> SheetsService:
    """Streamlit 세션 내 싱글톤 서비스"""
    svc = SheetsService()
    svc.connect()
    return svc
