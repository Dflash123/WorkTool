"""
Monster Skill Analyzer - 메인 진입점
Streamlit 멀티페이지 앱
"""
import sys
import os

# 프로젝트 루트를 Python path에 추가 (PyInstaller .exe 환경 포함)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

import streamlit as st

from src.config.settings import settings


def main():
    st.set_page_config(
        page_title=settings.app_title,
        page_icon="🐉",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 사이드바 네비게이션
    with st.sidebar:
        st.title("🐉 Monster Skill\nAnalyzer")
        st.caption(f"v{settings.app_version}")
        st.divider()

        # 연결 상태 표시
        if settings.is_configured():
            st.success("Sheets 연결됨", icon="✅")
        else:
            st.warning("Google Sheets 설정 필요", icon="⚠️")

        st.divider()

        page = st.radio(
            "메뉴",
            ["📝 스킬 입력", "🧪 테스트 로그", "⭐ 체감 평가", "📊 분석 대시보드", "⚙️ 설정"],
            label_visibility="collapsed"
        )

        st.divider()
        st.caption("사용 순서")
        st.caption("① 스킬 입력\n② 테스트 로그\n③ 체감 평가\n④ 분석 대시보드")

    # Google Sheets 미설정 시 설정 안내 배너
    if not settings.is_configured():
        st.warning(
            "Google Sheets가 설정되지 않았습니다. "
            "**⚙️ 설정** 메뉴에서 연결 정보를 입력하세요.",
            icon="⚠️"
        )
        # 설정 페이지가 아닐 때만 배너 표시 후 기능 제한
        if page != "⚙️ 설정":
            with st.expander("설정 가이드 보기"):
                st.markdown("""
1. **⚙️ 설정** 메뉴 클릭
2. Google Spreadsheet ID 입력
3. `credentials/` 폴더에 서비스 계정 JSON 파일 넣기
4. 연결 테스트 클릭
""")
            st.stop()

    # Google Sheets 연결 시도
    if settings.is_configured():
        from src.services.sheets_service import get_sheets_service
        svc = get_sheets_service()
        if not svc.is_connected:
            st.error(
                "Google Sheets 연결에 실패했습니다. "
                "**⚙️ 설정** 메뉴에서 설정을 확인하세요.",
                icon="🔴"
            )
            if page != "⚙️ 설정":
                st.stop()

    # 페이지 라우팅
    if page == "📝 스킬 입력":
        from src.ui.pages.skill_input import render
        render()

    elif page == "🧪 테스트 로그":
        from src.ui.pages.test_log import render
        render()

    elif page == "⭐ 체감 평가":
        from src.ui.pages.feedback import render
        render()

    elif page == "📊 분석 대시보드":
        from src.ui.pages.analysis import render
        render()

    elif page == "⚙️ 설정":
        from src.ui.pages.settings_page import render
        render()


main()
