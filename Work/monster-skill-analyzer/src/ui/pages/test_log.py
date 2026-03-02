"""
테스트 로그 기록 페이지
"""
from __future__ import annotations
import streamlit as st
from datetime import date

from src.modules.data_models import TestLog
from src.services.sheets_service import get_sheets_service


def render():
    st.title("테스트 로그 기록")

    tab1, tab2 = st.tabs(["새 테스트 기록", "테스트 이력 조회"])

    with tab1:
        _render_log_form()

    with tab2:
        _render_log_list()


def _render_log_form():
    svc = get_sheets_service()
    skills = svc.get_all_skills()

    if not skills:
        st.warning("먼저 스킬을 등록하세요.")
        return

    skill_options = {f"{s.monster_name} - {s.skill_name} (v{s.version})": s for s in skills}

    with st.form("test_log_form"):
        st.subheader("테스트 정보")

        selected_label = st.selectbox("대상 스킬 *", list(skill_options.keys()))
        selected_skill = skill_options[selected_label]

        c1, c2, c3 = st.columns(3)
        with c1:
            test_type = st.selectbox("테스트 유형", ["internal", "live"])
            test_date = st.date_input("테스트 날짜", value=date.today())
        with c2:
            tester_name = st.text_input("담당자 이름 *")
            test_version = st.text_input("테스트 버전", value=selected_skill.version)
        with c3:
            test_environment = st.selectbox(
                "테스트 환경", ["로컬", "QA서버", "스테이징", "라이브"]
            )
            participant_count = st.number_input(
                "참여 인원", min_value=1, max_value=100, value=1
            )

        notes = st.text_area(
            "테스트 메모",
            placeholder="예) 신규 유저 5명 대상. 첫 시도 회피율 20%.",
            height=80
        )

        submitted = st.form_submit_button("테스트 기록 저장", type="primary", use_container_width=True)

    if submitted:
        if not tester_name:
            st.error("담당자 이름을 입력하세요.")
            return

        log = TestLog(
            skill_id=selected_skill.skill_id,
            monster_name=selected_skill.monster_name,
            skill_name=selected_skill.skill_name,
            test_type=test_type,
            test_date=str(test_date),
            tester_name=tester_name,
            test_version=test_version,
            test_environment=test_environment,
            participant_count=int(participant_count),
            notes=notes,
        )

        if svc.add_test_log(log):
            st.success(f"테스트 로그가 저장되었습니다. (log_id: {log.log_id[:8]}...)")
            st.info("이 log_id로 체감 평가를 연결할 수 있습니다.")


def _render_log_list():
    svc = get_sheets_service()
    logs = svc.get_all_test_logs()

    if not logs:
        st.info("기록된 테스트 로그가 없습니다.")
        return

    # 필터
    c1, c2 = st.columns(2)
    with c1:
        monster_filter = st.selectbox(
            "몬스터 필터",
            ["전체"] + sorted(set(l.monster_name for l in logs)),
            key="log_monster_filter"
        )
    with c2:
        type_filter = st.selectbox(
            "테스트 유형",
            ["전체", "internal", "live"],
            key="log_type_filter"
        )

    filtered = logs
    if monster_filter != "전체":
        filtered = [l for l in filtered if l.monster_name == monster_filter]
    if type_filter != "전체":
        filtered = [l for l in filtered if l.test_type == type_filter]

    st.caption(f"총 {len(filtered)}건")

    for log in reversed(filtered):
        badge = "🔬 내부" if log.test_type == "internal" else "🌐 라이브"
        with st.expander(
            f"{badge} | {log.test_date} | {log.monster_name} - {log.skill_name} | {log.tester_name}"
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("버전", log.test_version)
            c2.metric("환경", log.test_environment)
            c3.metric("참여 인원", log.participant_count)
            if log.notes:
                st.caption(f"메모: {log.notes}")
            st.code(f"log_id: {log.log_id}", language=None)
