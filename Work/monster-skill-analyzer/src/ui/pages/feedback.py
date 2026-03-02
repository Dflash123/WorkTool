"""
플레이어 체감 평가 입력 페이지
"""
from __future__ import annotations
import streamlit as st

from src.modules.data_models import PlayerFeedback
from src.services.sheets_service import get_sheets_service


def render():
    st.title("플레이어 체감 평가")

    tab1, tab2 = st.tabs(["체감 평가 입력", "평가 이력 조회"])

    with tab1:
        _render_feedback_form()

    with tab2:
        _render_feedback_list()


def _likert_buttons(label: str, key: str, default: int = 3, help_text: str = "") -> int:
    """리커트 1~5 버튼 UI"""
    labels_map = {
        1: "1 매우 낮음",
        2: "2 낮음",
        3: "3 보통",
        4: "4 높음",
        5: "5 매우 높음",
    }
    st.caption(label + (f" - {help_text}" if help_text else ""))
    cols = st.columns(5)
    selected = st.session_state.get(key, default)
    for i, (val, btn_label) in enumerate(labels_map.items()):
        if cols[i].button(
            btn_label,
            key=f"{key}_btn_{val}",
            type="primary" if selected == val else "secondary",
            use_container_width=True,
        ):
            st.session_state[key] = val
            st.rerun()
    return st.session_state.get(key, default)


def _render_feedback_form():
    svc = get_sheets_service()
    skills = svc.get_all_skills()
    logs = svc.get_all_test_logs()

    if not skills:
        st.warning("먼저 스킬을 등록하세요.")
        return

    skill_options = {f"{s.monster_name} - {s.skill_name} (v{s.version})": s for s in skills}

    st.subheader("연결 정보")
    c1, c2 = st.columns(2)
    with c1:
        selected_label = st.selectbox("대상 스킬 *", list(skill_options.keys()), key="fb_skill_select")
        selected_skill = skill_options[selected_label]
    with c2:
        tester_name = st.text_input("평가자 이름 *", key="fb_tester_name")

    # 해당 스킬의 테스트 로그 필터링
    skill_logs = [l for l in logs if l.skill_id == selected_skill.skill_id]
    log_options = {"없음 (직접 입력)": None}
    for l in skill_logs:
        log_options[f"{l.test_date} | {l.test_type} | {l.tester_name}"] = l

    with c1:
        selected_log_label = st.selectbox("연결할 테스트 로그", list(log_options.keys()), key="fb_log_select")
        selected_log = log_options[selected_log_label]

    st.divider()
    st.subheader("체감 평가 점수")
    st.caption("각 항목을 1~5점으로 평가하세요.")

    # 리커트 점수 입력
    scores = {}
    items = [
        ("reaction_sufficiency", "반응 시간 충분성", "회피/대응을 시도할 시간이 충분했나?"),
        ("hit_acceptance", "피격 납득도", "맞았을 때 납득이 됐나? (억울하지 않았나?)"),
        ("guide_clarity", "가이드 명확성", "어디에 공격이 오는지 명확히 보였나?"),
        ("attack_readability", "공격 가독성", "공격 모션/범위가 잘 읽혔나?"),
        ("learnability", "학습 가능성", "반복하면 패턴을 익힐 수 있을 것 같나?"),
        ("stress", "스트레스", "이 스킬로 인한 스트레스 수준 (높을수록 스트레스 심함)"),
        ("retry_intent", "재도전 의사", "이 스킬에 다시 도전하고 싶은가?"),
    ]

    for key, label, help_text in items:
        scores[key] = _likert_buttons(label, key=f"fb_{key}", help_text=help_text)
        st.write("")

    st.divider()
    opinion = st.text_area(
        "서술형 의견",
        placeholder="예) 선딜은 충분했지만 가이드 범위가 실제 판정보다 좁아서 억까당한 느낌이 들었음.",
        height=100,
        key="fb_opinion"
    )

    if st.button("평가 저장", type="primary", use_container_width=True):
        if not tester_name:
            st.error("평가자 이름을 입력하세요.")
            return

        feedback = PlayerFeedback(
            skill_id=selected_skill.skill_id,
            log_id=selected_log.log_id if selected_log else "none",
            tester_name=tester_name,
            reaction_sufficiency=scores["reaction_sufficiency"],
            hit_acceptance=scores["hit_acceptance"],
            guide_clarity=scores["guide_clarity"],
            attack_readability=scores["attack_readability"],
            learnability=scores["learnability"],
            stress=scores["stress"],
            retry_intent=scores["retry_intent"],
            opinion=opinion,
        )

        if svc.add_feedback(feedback):
            st.success("체감 평가가 저장되었습니다.")
            # 세션 초기화
            for key, _, _ in items:
                if f"fb_{key}" in st.session_state:
                    del st.session_state[f"fb_{key}"]


def _render_feedback_list():
    svc = get_sheets_service()
    feedbacks = svc.get_all_feedbacks()

    if not feedbacks:
        st.info("기록된 체감 평가가 없습니다.")
        return

    # 스킬별 그룹 표시
    skills = svc.get_all_skills()
    skill_map = {s.skill_id: f"{s.monster_name} - {s.skill_name}" for s in skills}

    import pandas as pd
    rows = []
    for fb in feedbacks:
        rows.append({
            "스킬": skill_map.get(fb.skill_id, fb.skill_id[:8]),
            "평가자": fb.tester_name,
            "반응충분성": fb.reaction_sufficiency,
            "납득도": fb.hit_acceptance,
            "가이드명확성": fb.guide_clarity,
            "가독성": fb.attack_readability,
            "학습가능성": fb.learnability,
            "스트레스": fb.stress,
            "재도전의사": fb.retry_intent,
            "기록일시": fb.created_at,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
