"""
Google Sheets 서비스 (PyQt6 버전 - OAuth 기반)
"""
from __future__ import annotations
from typing import Optional
import gspread

from src.config.settings import settings
from src.modules.data_models import (
    SkillDefinition, TestLog, PlayerFeedback, BalanceHistory
)
from src.services.auth_service import auth_service


class SheetsServiceQt:
    """Google Sheets CRUD - OAuth 인증 기반"""

    def __init__(self):
        self._spreadsheet: Optional[gspread.Spreadsheet] = None

    def connect(self) -> tuple[bool, str]:
        client = auth_service.get_client()
        if client is None:
            return False, "먼저 Google 로그인을 해주세요."
        if not settings.spreadsheet_id or settings.spreadsheet_id == "YOUR_SPREADSHEET_ID_HERE":
            return False, "Spreadsheet ID를 설정하세요."
        try:
            self._spreadsheet = client.open_by_key(settings.spreadsheet_id)
            self._ensure_sheets()
            return True, "연결 성공"
        except gspread.exceptions.SpreadsheetNotFound:
            return False, "Spreadsheet ID가 잘못되었습니다."
        except Exception as e:
            return False, f"연결 실패: {e}"

    def _ensure_sheets(self):
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

    def _sheet(self, key: str) -> gspread.Worksheet:
        return self._spreadsheet.worksheet(settings.sheet_names[key])

    @property
    def is_connected(self) -> bool:
        return self._spreadsheet is not None

    # ── SkillDefinitions ──────────────────────────
    def add_skill(self, skill: SkillDefinition) -> tuple[bool, str]:
        try:
            skill.compute()
            self._sheet("skill_definitions").append_row(skill.to_row())
            return True, "저장 완료"
        except Exception as e:
            return False, str(e)

    def get_all_skills(self) -> list[SkillDefinition]:
        try:
            rows = self._sheet("skill_definitions").get_all_values()
            return [SkillDefinition.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception:
            return []

    def update_skill(self, skill: SkillDefinition) -> tuple[bool, str]:
        try:
            ws = self._sheet("skill_definitions")
            rows = ws.get_all_values()
            for idx, row in enumerate(rows[1:], start=2):
                if row and row[0] == skill.skill_id:
                    skill.compute()
                    ws.update(f"A{idx}:Y{idx}", [skill.to_row()])
                    return True, "수정 완료"
            return False, "스킬을 찾을 수 없습니다."
        except Exception as e:
            return False, str(e)

    def delete_skill(self, skill_id: str) -> tuple[bool, str]:
        try:
            ws = self._sheet("skill_definitions")
            rows = ws.get_all_values()
            for idx, row in enumerate(rows[1:], start=2):
                if row and row[0] == skill_id:
                    ws.delete_rows(idx)
                    return True, "삭제 완료"
            return False, "스킬을 찾을 수 없습니다."
        except Exception as e:
            return False, str(e)

    # ── TestLogs ──────────────────────────────────
    def add_test_log(self, log: TestLog) -> tuple[bool, str]:
        try:
            self._sheet("test_logs").append_row(log.to_row())
            return True, "저장 완료"
        except Exception as e:
            return False, str(e)

    def get_all_test_logs(self) -> list[TestLog]:
        try:
            rows = self._sheet("test_logs").get_all_values()
            return [TestLog.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception:
            return []

    # ── PlayerFeedback ────────────────────────────
    def add_feedback(self, fb: PlayerFeedback) -> tuple[bool, str]:
        try:
            self._sheet("player_feedback").append_row(fb.to_row())
            return True, "저장 완료"
        except Exception as e:
            return False, str(e)

    def get_all_feedbacks(self) -> list[PlayerFeedback]:
        try:
            rows = self._sheet("player_feedback").get_all_values()
            return [PlayerFeedback.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception:
            return []

    def get_feedbacks_by_skill(self, skill_id: str) -> list[PlayerFeedback]:
        return [f for f in self.get_all_feedbacks() if f.skill_id == skill_id]

    # ── BalanceHistory ────────────────────────────
    def add_history(self, h: BalanceHistory) -> tuple[bool, str]:
        try:
            self._sheet("balance_history").append_row(h.to_row())
            return True, "저장 완료"
        except Exception as e:
            return False, str(e)

    def get_all_history(self) -> list[BalanceHistory]:
        try:
            rows = self._sheet("balance_history").get_all_values()
            return [BalanceHistory.from_row(r) for r in rows[1:] if r and r[0]]
        except Exception:
            return []

    def get_history_by_skill(self, skill_id: str) -> list[BalanceHistory]:
        return [h for h in self.get_all_history() if h.skill_id == skill_id]


# 전역 싱글톤
sheets_service = SheetsServiceQt()
