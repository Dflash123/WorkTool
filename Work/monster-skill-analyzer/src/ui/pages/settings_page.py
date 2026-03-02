"""
설정 페이지 - Google Sheets 계정/시트ID 변경
"""
from __future__ import annotations
import streamlit as st
import yaml
from pathlib import Path

from src.config.settings import settings, ROOT_DIR, CONFIG_PATH


def render():
    st.title("설정")

    tab1, tab2 = st.tabs(["Google Sheets 연결", "앱 설정"])

    with tab1:
        _render_sheets_settings()

    with tab2:
        _render_app_settings()


def _render_sheets_settings():
    st.subheader("Google Sheets 연결 설정")

    # 현재 상태 표시
    if settings.is_configured():
        st.success("Google Sheets 연결 설정 완료")
    else:
        st.error("Google Sheets 설정이 필요합니다.")

    with st.form("sheets_settings_form"):
        st.markdown("**Spreadsheet ID**")
        st.caption("스프레드시트 URL: `https://docs.google.com/spreadsheets/d/[여기]/edit`")
        spreadsheet_id = st.text_input(
            "Spreadsheet ID",
            value=settings.spreadsheet_id,
            label_visibility="collapsed"
        )

        st.markdown("**Service Account JSON 파일명**")
        st.caption(f"파일을 `{ROOT_DIR}/credentials/` 폴더에 넣어주세요.")
        cred_filename = st.text_input(
            "파일명",
            value=settings.credentials_file.name,
            label_visibility="collapsed"
        )

        st.markdown("**시트 이름 (탭 이름)**")
        col1, col2 = st.columns(2)
        sheet_names = settings.sheet_names
        with col1:
            sheet_skills = st.text_input("스킬 정의 시트", value=sheet_names.get("skill_definitions", "SkillDefinitions"))
            sheet_logs = st.text_input("테스트 로그 시트", value=sheet_names.get("test_logs", "TestLogs"))
        with col2:
            sheet_feedback = st.text_input("체감 평가 시트", value=sheet_names.get("player_feedback", "PlayerFeedback"))
            sheet_history = st.text_input("수정 히스토리 시트", value=sheet_names.get("balance_history", "BalanceHistory"))

        saved = st.form_submit_button("설정 저장", type="primary", use_container_width=True)

    if saved:
        # config.yaml 업데이트
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        config["google_sheets"]["spreadsheet_id"] = spreadsheet_id
        config["google_sheets"]["credentials_file"] = f"credentials/{cred_filename}"
        config["google_sheets"]["sheets"] = {
            "skill_definitions": sheet_skills,
            "test_logs": sheet_logs,
            "player_feedback": sheet_feedback,
            "balance_history": sheet_history,
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        settings.reload()
        st.success("설정이 저장되었습니다. 앱을 재시작하면 새 설정이 적용됩니다.")
        st.cache_resource.clear()

    # 연결 테스트
    if st.button("연결 테스트", use_container_width=True):
        from src.services.sheets_service import SheetsService
        svc = SheetsService()
        if svc.connect():
            st.success("Google Sheets 연결 성공!")
        else:
            st.error("연결 실패. 설정을 확인하세요.")

    st.divider()
    st.subheader("설정 가이드")
    with st.expander("Google Service Account 발급 방법"):
        st.markdown("""
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. **API 및 서비스 → 라이브러리** → `Google Sheets API` 활성화
4. **API 및 서비스 → 사용자 인증 정보** → 서비스 계정 생성
5. 서비스 계정 키 (JSON) 다운로드
6. `credentials/` 폴더에 파일 저장
7. Google Spreadsheet를 서비스 계정 이메일과 **공유** (편집자 권한)
        """)


def _render_app_settings():
    st.subheader("앱 설정")

    with st.form("app_settings_form"):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        metrics_cfg = config.get("metrics", {})

        st.markdown("**지표 위험 기준값**")
        c1, c2 = st.columns(2)
        with c1:
            reaction_ref = st.number_input(
                "반응 여유 기준 시간 (ms) - 이 이상이면 만점",
                value=metrics_cfg.get("reaction_reference_ms", 500),
                min_value=100, max_value=2000, step=50
            )
            reaction_danger = st.number_input(
                "반응 여유 위험 기준 (이하 경고)",
                value=metrics_cfg.get("reaction_margin_danger", 50),
                min_value=0, max_value=100
            )
        with c2:
            fairness_danger = st.number_input(
                "공정성 위험 기준 (이하 위험)",
                value=metrics_cfg.get("fairness_score_danger", 40),
                min_value=0, max_value=100
            )
            unfair_danger = st.number_input(
                "억까가능성 위험 기준 (이상 위험)",
                value=metrics_cfg.get("unfair_hit_danger", 60),
                min_value=0, max_value=100
            )

        saved = st.form_submit_button("저장", type="primary", use_container_width=True)

    if saved:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        config["metrics"]["reaction_reference_ms"] = int(reaction_ref)
        config["metrics"]["reaction_margin_danger"] = int(reaction_danger)
        config["metrics"]["fairness_score_danger"] = int(fairness_danger)
        config["metrics"]["unfair_hit_danger"] = int(unfair_danger)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        settings.reload()
        st.success("설정이 저장되었습니다.")
