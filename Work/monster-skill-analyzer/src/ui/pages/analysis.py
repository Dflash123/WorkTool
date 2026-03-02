"""
분석 대시보드 페이지
- 스킬별 지표 요약
- 체감 평가 시각화
- 위험 패턴 자동 탐지
- 버전별 비교
"""
from __future__ import annotations
import streamlit as st
import pandas as pd

from src.modules.metrics_calculator import calculator
from src.services.sheets_service import get_sheets_service
from src.ui.components.charts import (
    metrics_gauge, feedback_radar, feedback_distribution,
    skill_timing_bar, version_trend
)


def render():
    st.title("분석 대시보드")

    svc = get_sheets_service()
    skills = svc.get_all_skills()

    if not skills:
        st.info("분석할 스킬 데이터가 없습니다.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["스킬별 분석", "위험 패턴", "버전 비교", "전체 요약"])

    with tab1:
        _render_skill_analysis(svc, skills)

    with tab2:
        _render_risk_detection(svc, skills)

    with tab3:
        _render_version_comparison(svc, skills)

    with tab4:
        _render_summary(svc, skills)


def _render_skill_analysis(svc, skills):
    """특정 스킬 상세 분석"""
    skill_options = {f"{s.monster_name} - {s.skill_name} (v{s.version})": s for s in skills}
    selected_label = st.selectbox("분석할 스킬 선택", list(skill_options.keys()), key="analysis_skill")
    skill = skill_options[selected_label]

    feedbacks = svc.get_feedbacks_by_skill(skill.skill_id)
    result = calculator.calculate(skill, feedbacks if feedbacks else None)

    # 위험도 배지
    risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
    st.subheader(f"{risk_color[result.overall_risk]} 종합 위험도: {result.overall_risk}")

    # 지표 게이지
    st.caption("자동 계산 지표")
    metrics_gauge(result)

    # 타이밍 바
    skill_timing_bar(skill)

    # 경고/위험 표시
    if result.danger_flags:
        st.error("**즉시 검토 필요**")
        for flag in result.danger_flags:
            st.error(f"위험: {flag}")

    if result.warnings:
        for w in result.warnings:
            st.warning(f"경고: {w}")

    # 체감 평가 시각화
    if feedbacks:
        st.subheader(f"체감 평가 ({len(feedbacks)}명)")
        c1, c2 = st.columns(2)
        with c1:
            feedback_radar(feedbacks, title=f"{skill.skill_name} 체감 레이더")
        with c2:
            feedback_distribution(feedbacks)

        # 서술형 의견
        opinions = [fb.opinion for fb in feedbacks if fb.opinion.strip()]
        if opinions:
            st.subheader("서술형 의견")
            for i, op in enumerate(opinions, 1):
                st.markdown(f"**{i}.** {op}")
    else:
        st.info("체감 평가 데이터가 없습니다. 체감 평가를 먼저 입력하세요.")

    # 밸런스 히스토리
    history = svc.get_history_by_skill(skill.skill_id)
    if history:
        st.subheader("밸런스 수정 히스토리")
        history_data = [{
            "날짜": h.changed_at[:10],
            "변경 필드": h.field_changed,
            "이전": h.value_before,
            "이후": h.value_after,
            "이유": h.change_reason,
            "수정자": h.changed_by,
        } for h in history]
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)


def _render_risk_detection(svc, skills):
    """위험 패턴 자동 탐지 전체 목록"""
    st.subheader("전체 스킬 위험 패턴 스캔")

    high_risk = []
    medium_risk = []
    low_risk = []

    for skill in skills:
        feedbacks = svc.get_feedbacks_by_skill(skill.skill_id)
        result = calculator.calculate(skill, feedbacks if feedbacks else None)

        entry = {
            "몬스터": skill.monster_name,
            "스킬": skill.skill_name,
            "버전": skill.version,
            "반응여유": f"{result.reaction_margin:.0f}",
            "공정성": f"{result.fairness_score:.0f}",
            "억까가능성": f"{result.unfair_hit_index:.0f}",
            "위험도": result.overall_risk,
            "이슈": " | ".join(result.danger_flags + result.warnings),
        }

        if result.overall_risk == "HIGH":
            high_risk.append(entry)
        elif result.overall_risk == "MEDIUM":
            medium_risk.append(entry)
        else:
            low_risk.append(entry)

    if high_risk:
        st.error(f"즉시 검토 필요 ({len(high_risk)}개)")
        st.dataframe(pd.DataFrame(high_risk), use_container_width=True)

    if medium_risk:
        st.warning(f"주의 필요 ({len(medium_risk)}개)")
        st.dataframe(pd.DataFrame(medium_risk), use_container_width=True)

    if low_risk:
        with st.expander(f"정상 ({len(low_risk)}개)"):
            st.dataframe(pd.DataFrame(low_risk), use_container_width=True)


def _render_version_comparison(svc, skills):
    """버전별 스킬 변화 비교"""
    st.subheader("버전별 타이밍 변화")

    # 몬스터별로 그룹
    monster_names = sorted(set(s.monster_name for s in skills))
    selected_monster = st.selectbox("몬스터 선택", monster_names, key="vc_monster")

    monster_skills = [s for s in skills if s.monster_name == selected_monster]
    skill_names = sorted(set(s.skill_name for s in monster_skills))
    selected_skill_name = st.selectbox("스킬 선택", skill_names, key="vc_skill")

    target_skills = [s for s in monster_skills if s.skill_name == selected_skill_name]

    if len(target_skills) < 2:
        st.info("버전 비교를 위해 동일 스킬의 버전이 2개 이상 필요합니다.")
    else:
        metric_options = {
            "선딜 (ms)": "pre_delay_ms",
            "판정 지속 (ms)": "active_duration_ms",
            "후딜 (ms)": "post_delay_ms",
            "반응 가능 시간 (ms)": "reaction_window_ms",
            "총 행동 시간 (ms)": "total_duration_ms",
        }
        selected_metric_label = st.selectbox("비교 지표", list(metric_options.keys()), key="vc_metric")
        version_trend(target_skills, metric_options[selected_metric_label])

        # 버전별 상세 비교 테이블
        comparison_data = [{
            "버전": s.version,
            "선딜(ms)": s.pre_delay_ms,
            "판정(ms)": s.active_duration_ms,
            "후딜(ms)": s.post_delay_ms,
            "반응가능(ms)": s.reaction_window_ms,
            "총시간(ms)": s.total_duration_ms,
            "가이드": "있음" if s.guide_exists else "없음",
        } for s in sorted(target_skills, key=lambda x: x.version)]

        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)


def _render_summary(svc, skills):
    """전체 스킬 요약 테이블"""
    st.subheader("전체 스킬 지표 요약")

    rows = []
    for skill in skills:
        feedbacks = svc.get_feedbacks_by_skill(skill.skill_id)
        result = calculator.calculate(skill, feedbacks if feedbacks else None)
        rows.append({
            "몬스터": skill.monster_name,
            "스킬": skill.skill_name,
            "버전": skill.version,
            "반응여유": round(result.reaction_margin, 1),
            "공정성": round(result.fairness_score, 1),
            "억까가능성": round(result.unfair_hit_index, 1),
            "설계적중률": round(result.design_intent_rate, 1),
            "학습가능성": round(result.learnability_score, 1),
            "위험도": result.overall_risk,
            "체감수": len(feedbacks),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.map(
            lambda v: "background-color: #ffcccc" if v == "HIGH"
            else "background-color: #fff3cc" if v == "MEDIUM" else "",
            subset=["위험도"]
        ),
        use_container_width=True,
    )

    # CSV 다운로드
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "CSV 내보내기",
        data=csv,
        file_name="skill_analysis_summary.csv",
        mime="text/csv",
    )
