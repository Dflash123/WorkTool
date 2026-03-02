"""
차트 컴포넌트 - Plotly 기반 재사용 가능한 차트
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

from src.modules.data_models import PlayerFeedback, SkillDefinition
from src.modules.metrics_calculator import MetricsResult


def metrics_gauge(result: MetricsResult):
    """5개 지표 게이지 차트"""
    data = result.to_dict()
    labels = list(data.keys())
    values = list(data.values())

    colors = []
    for label, val in zip(labels, values):
        if label == "억까 가능성":
            colors.append("red" if val > 60 else "orange" if val > 40 else "green")
        else:
            colors.append("green" if val >= 70 else "orange" if val >= 50 else "red")

    fig = go.Figure()
    for i, (label, val, color) in enumerate(zip(labels, values, colors)):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            title={"text": label, "font": {"size": 12}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 40], "color": "#ffcccc"},
                    {"range": [40, 70], "color": "#fff3cc"},
                    {"range": [70, 100], "color": "#ccffcc"},
                ],
            },
            domain={"row": 0, "column": i},
        ))

    fig.update_layout(
        grid={"rows": 1, "columns": 5, "pattern": "independent"},
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def feedback_radar(feedbacks: list[PlayerFeedback], title: str = "체감 평가 레이더"):
    """체감 평가 레이더 차트"""
    if not feedbacks:
        st.info("체감 평가 데이터가 없습니다.")
        return

    categories = ["반응충분성", "납득도", "가이드명확성", "가독성", "학습가능성", "재도전의사"]
    field_keys = [
        "reaction_sufficiency", "hit_acceptance", "guide_clarity",
        "attack_readability", "learnability", "retry_intent"
    ]

    # 전체 평균
    avgs = []
    for key in field_keys:
        avg = sum(getattr(fb, key) for fb in feedbacks) / len(feedbacks)
        avgs.append(round(avg, 2))

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=avgs + [avgs[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="평균",
        line_color="royalblue",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title=title,
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def feedback_distribution(feedbacks: list[PlayerFeedback]):
    """체감 점수 분포 박스플롯"""
    if not feedbacks:
        return

    data = {
        "반응충분성": [fb.reaction_sufficiency for fb in feedbacks],
        "납득도": [fb.hit_acceptance for fb in feedbacks],
        "가이드명확성": [fb.guide_clarity for fb in feedbacks],
        "가독성": [fb.attack_readability for fb in feedbacks],
        "학습가능성": [fb.learnability for fb in feedbacks],
        "스트레스": [fb.stress for fb in feedbacks],
        "재도전의사": [fb.retry_intent for fb in feedbacks],
    }

    df_list = []
    for metric, values in data.items():
        for v in values:
            df_list.append({"지표": metric, "점수": v})

    df = pd.DataFrame(df_list)
    fig = px.box(df, x="지표", y="점수", title="체감 점수 분포", range_y=[0, 6])
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def skill_timing_bar(skill: SkillDefinition):
    """스킬 타이밍 구간 시각화 바 차트"""
    segments = [
        ("선딜", skill.pre_delay_ms, "#FF6B6B"),
        ("판정", skill.active_duration_ms, "#FF0000"),
        ("후딜", skill.post_delay_ms, "#FFA07A"),
    ]

    fig = go.Figure()
    x_start = 0
    for name, duration, color in segments:
        fig.add_trace(go.Bar(
            x=[duration], y=["타이밍"],
            orientation="h",
            name=f"{name} ({duration}ms)",
            marker_color=color,
            base=x_start,
        ))
        x_start += duration

    # 회피 가능 구간 표시
    if skill.dodge_start_ms < skill.dodge_end_ms:
        fig.add_vrect(
            x0=skill.dodge_start_ms, x1=skill.dodge_end_ms,
            fillcolor="rgba(0,200,0,0.15)", line_width=0,
            annotation_text="회피 가능", annotation_position="top left",
        )

    fig.update_layout(
        title=f"{skill.skill_name} - 타이밍 구조 (총 {skill.total_duration_ms}ms)",
        xaxis_title="시간 (ms)",
        barmode="stack",
        height=200,
        margin=dict(l=20, r=20, t=60, b=40),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def version_trend(skills: list[SkillDefinition], metric_name: str = "reaction_window_ms"):
    """버전별 지표 변화 라인 차트"""
    if not skills:
        return

    df = pd.DataFrame([
        {"버전": s.version, "값": getattr(s, metric_name, 0), "스킬": s.skill_name}
        for s in skills
    ])

    fig = px.line(df, x="버전", y="값", color="스킬",
                  title=f"버전별 {metric_name} 변화", markers=True)
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
