"""
Google OAuth2 인증 서비스
- 버튼 한 번 클릭 → 브라우저에서 구글 로그인 → 자동 저장
- 이후 재실행 시 자동 로그인
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Optional

import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TOKEN_PATH = settings.credentials_file.parent / "token.json"


class AuthService:
    """Google OAuth2 인증 관리"""

    def __init__(self):
        self._creds: Optional[Credentials] = None
        self._client: Optional[gspread.Client] = None

    def is_authenticated(self) -> bool:
        return self._creds is not None and self._creds.valid

    def has_saved_token(self) -> bool:
        return TOKEN_PATH.exists()

    def has_client_secret(self) -> bool:
        return settings.credentials_file.exists()

    def auto_login(self) -> bool:
        """저장된 토큰으로 자동 로그인 시도"""
        if not TOKEN_PATH.exists():
            return False
        try:
            self._creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            if self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
                self._save_token()
            self._client = gspread.authorize(self._creds)
            return self._creds.valid
        except Exception:
            return False

    def login_with_browser(self) -> tuple[bool, str]:
        """
        브라우저를 열어 구글 로그인 수행
        반환: (성공여부, 메시지)
        """
        if not self.has_client_secret():
            return False, (
                f"client_secret.json 파일이 없습니다.\n"
                f"경로: {settings.credentials_file}\n\n"
                "Google Cloud Console에서 OAuth 자격증명을 다운로드하세요."
            )
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.credentials_file), SCOPES
            )
            self._creds = flow.run_local_server(port=0, open_browser=True)
            self._save_token()
            self._client = gspread.authorize(self._creds)
            return True, "Google 로그인 성공!"
        except Exception as e:
            return False, f"로그인 실패: {e}"

    def logout(self):
        self._creds = None
        self._client = None
        if TOKEN_PATH.exists():
            TOKEN_PATH.unlink()

    def get_client(self) -> Optional[gspread.Client]:
        return self._client

    def _save_token(self):
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(self._creds.to_json())


# 전역 싱글톤
auth_service = AuthService()
