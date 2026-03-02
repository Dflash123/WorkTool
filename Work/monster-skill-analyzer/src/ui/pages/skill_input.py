"""
스킬 정의 입력 페이지
- 스킬 타이밍, 가이드 이펙트 입력
- 자동 계산 지표 실시간 미리보기
- 스킬 목록 조회/수정/삭제
"""
from __future__ import annotations
import streamlit as st
from datetime import date

from src.modules.data_models import SkillDefinition, BalanceHistory
from src.modules.metrics_calculator import calculator
from src.services.sheets_service import get_sheets_service
from src.ui.components.charts import metrics_gauge, skill_timing_bar


def render():
    st.title("스킬 정의 입력")

    tab1, tab2 = st.tabs(["새 스킬 등록", "스킬 목록 / 수정"])

    with tab1:
        _render_skill_form()

    with tab2:
        _render_skill_list()


def _render_skill_form(edit_skill: SkillDefinition = None):
    """스킬 입력 폼 (신규 or 수정)"""
    is_edit = edit_skill is not None
    prefix = "edit_" if is_edit else "new_"

    with st.form(f"skill_form_{prefix}"):
        st.subheader("기본 정보")
        c1, c2, c3 = st.columns(3)
        with c1:
            monster_name = st.text_input(
                "몬스터 이름 *",
                value=edit_skill.monster_name if is_edit else "",
                key=f"{prefix}monster_name"
            )
        with c2:
            skill_name = st.text_input(
                "스킬 이름 *",
                value=edit_skill.skill_name if is_edit else "",
                key=f"{prefix}skill_name"
            )
        with c3:
            version = st.text_input(
                "버전 *",
                value=edit_skill.version if is_edit else "1.0.0",
                key=f"{prefix}version"
            )

        c4, c5 = st.columns(2)
        with c4:
            skill_type = st.selectbox(
                "스킬 유형",
                ["attack", "aoe", "special", "buff", "debuff"],
                index=["attack", "aoe", "special", "buff", "debuff"].index(
                    edit_skill.skill_type) if is_edit else 0,
                key=f"{prefix}skill_type"
            )
        with c5:
            targeting_type = st.selectbox(
                "타겟팅 방식",
                ["area", "single", "line", "random"],
                index=["area", "single", "line", "random"].index(
                    edit_skill.targeting_type) if is_edit else 0,
                key=f"{prefix}targeting_type"
            )

        st.divider()
        st.subheader("타이밍 설정 (ms)")

        c1, c2, c3 = st.columns(3)
        with c1:
            pre_delay = st.number_input(
                "선딜 (ms)", min_value=0, max_value=10000,
                value=edit_skill.pre_delay_ms if is_edit else 500,
                step=50, key=f"{prefix}pre_delay",
                help="공격 모션 시작 ~ 판정 시작까지"
            )
        with c2:
            active_duration = st.number_input(
                "판정 지속 (ms)", min_value=0, max_value=10000,
                value=edit_skill.active_duration_ms if is_edit else 300,
                step=50, key=f"{prefix}active_duration",
                help="실제 피해 판정이 활성화된 시간"
            )
        with c3:
            post_delay = st.number_input(
                "후딜 (ms)", min_value=0, max_value=10000,
                value=edit_skill.post_delay_ms if is_edit else 400,
                step=50, key=f"{prefix}post_delay",
                help="판정 종료 ~ 다음 행동 가능까지"
            )

        st.caption(f"총 행동 시간: **{pre_delay + active_duration + post_delay}ms**")

        c1, c2 = st.columns(2)
        with c1:
            dodge_start = st.number_input(
                "회피 가능 시작 (ms)", min_value=0, max_value=10000,
                value=edit_skill.dodge_start_ms if is_edit else 200,
                step=50, key=f"{prefix}dodge_start",
                help="플레이어가 회피 입력을 시작해야 하는 시점"
            )
        with c2:
            dodge_end = st.number_input(
                "회피 가능 종료 (ms)", min_value=0, max_value=10000,
                value=edit_skill.dodge_end_ms if is_edit else 600,
                step=50, key=f"{prefix}dodge_end"
            )

        reaction_window = max(0, dodge_end - dodge_start)
        st.caption(f"실제 반응 가능 시간: **{reaction_window}ms**")

        st.divider()
        st.subheader("가이드 이펙트")

        guide_exists = st.toggle(
            "가이드 이펙트 있음",
            value=edit_skill.guide_exists if is_edit else True,
            key=f"{prefix}guide_exists"
        )

        if guide_exists:
            c1, c2, c3 = st.columns(3)
            with c1:
                guide_start = st.number_input(
                    "가이드 시작 (ms)", min_value=0,
                    value=edit_skill.guide_start_ms if is_edit else 0,
                    step=50, key=f"{prefix}guide_start"
                )
                guide_type = st.selectbox(
                    "가이드 유형",
                    ["visual", "sound", "both"],
                    index=["visual", "sound", "both"].index(
                        edit_skill.guide_type) if (is_edit and edit_skill.guide_type in ["visual", "sound", "both"]) else 0,
                    key=f"{prefix}guide_type"
                )
            with c2:
                guide_duration = st.number_input(
                    "가이드 지속 (ms)", min_value=0,
                    value=edit_skill.guide_duration_ms if is_edit else 500,
                    step=50, key=f"{prefix}guide_duration"
                )
                guide_intensity = st.slider(
                    "가이드 강도", 1, 5,
                    value=edit_skill.guide_intensity if is_edit else 3,
                    key=f"{prefix}guide_intensity"
                )
            with c3:
                guide_visibility = st.slider(
                    "시야 가시성", 1, 5,
                    value=edit_skill.guide_visibility if is_edit else 3,
                    key=f"{prefix}guide_visibility"
                )
                guide_match = st.checkbox(
                    "판정과 가이드 일치",
                    value=edit_skill.guide_match if is_edit else True,
                    key=f"{prefix}guide_match"
                )
                guide_offset = st.number_input(
                    "가이드 오차 (ms)", min_value=0,
                    value=edit_skill.guide_offset_ms if is_edit else 0,
                    step=10, key=f"{prefix}guide_offset"
                )
        else:
            guide_start = guide_duration = guide_intensity = guide_visibility = guide_offset = 0
            guide_type = "none"
            guide_match = False

        st.divider()
        design_intent = st.text_area(
            "설계 의도 메모",
            value=edit_skill.design_intent if is_edit else "",
            placeholder="예) 중급자 대상, 패턴 학습 유도. 선딜로 예고 후 좌우 회피 가능.",
            key=f"{prefix}design_intent",
            height=80
        )

        # 실시간 미리보기 (폼 외부에서 보여주기 위해 session_state 활용)
        submitted = st.form_submit_button(
            "수정 저장" if is_edit else "저장",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not monster_name or not skill_name or not version:
            st.error("몬스터 이름, 스킬 이름, 버전은 필수입니다.")
            return

        skill = SkillDefinition(
            monster_name=monster_name,
            skill_name=skill_name,
            skill_type=skill_type,
            version=version,
            pre_delay_ms=int(pre_delay),
            active_duration_ms=int(active_duration),
            post_delay_ms=int(post_delay),
            dodge_start_ms=int(dodge_start),
            dodge_end_ms=int(dodge_end),
            targeting_type=targeting_type,
            guide_exists=guide_exists,
            guide_start_ms=int(guide_start),
            guide_duration_ms=int(guide_duration),
            guide_type=guide_type,
            guide_intensity=int(guide_intensity),
            guide_visibility=int(guide_visibility),
            guide_match=guide_match,
            guide_offset_ms=int(guide_offset),
            design_intent=design_intent,
        )

        svc = get_sheets_service()
        if is_edit:
            skill.skill_id = edit_skill.skill_id
            skill.created_at = edit_skill.created_at
            if svc.update_skill(skill):
                st.success("스킬이 수정되었습니다.")
        else:
            if svc.add_skill(skill):
                st.success(f"'{skill_name}' 스킬이 저장되었습니다.")

        # 저장 후 지표 미리보기
        result = calculator.calculate(skill)
        st.subheader("자동 계산 지표")
        metrics_gauge(result)
        skill_timing_bar(skill)

        if result.danger_flags:
            for flag in result.danger_flags:
                st.error(f"위험: {flag}")
        if result.warnings:
            for w in result.warnings:
                st.warning(f"경고: {w}")


def _render_skill_list():
    """스킬 목록 조회/필터/수정/삭제"""
    svc = get_sheets_service()
    skills = svc.get_all_skills()

    if not skills:
        st.info("등록된 스킬이 없습니다.")
        return

    # 필터
    c1, c2 = st.columns(2)
    with c1:
        monster_filter = st.selectbox(
            "몬스터 필터",
            ["전체"] + sorted(set(s.monster_name for s in skills))
        )
    with c2:
        search = st.text_input("스킬 이름 검색")

    filtered = skills
    if monster_filter != "전체":
        filtered = [s for s in filtered if s.monster_name == monster_filter]
    if search:
        filtered = [s for s in filtered if search.lower() in s.skill_name.lower()]

    st.caption(f"총 {len(filtered)}개 스킬")

    for skill in filtered:
        with st.expander(f"{skill.monster_name} - {skill.skill_name} (v{skill.version})"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("선딜", f"{skill.pre_delay_ms}ms")
            c2.metric("판정", f"{skill.active_duration_ms}ms")
            c3.metric("후딜", f"{skill.post_delay_ms}ms")
            c4.metric("반응 가능", f"{skill.reaction_window_ms}ms")

            result = calculator.calculate(skill)
            st.caption(
                f"공정성: {result.fairness_score:.0f}  |  "
                f"억까가능성: {result.unfair_hit_index:.0f}  |  "
                f"반응여유: {result.reaction_margin:.0f}  |  "
                f"위험도: **{result.overall_risk}**"
            )

            skill_timing_bar(skill)

            col_edit, col_del = st.columns([3, 1])
            with col_del:
                if st.button("삭제", key=f"del_{skill.skill_id}", type="secondary"):
                    if svc.delete_skill(skill.skill_id):
                        st.success("삭제되었습니다.")
                        st.rerun()
