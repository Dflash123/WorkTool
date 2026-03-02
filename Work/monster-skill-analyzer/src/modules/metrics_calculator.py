"""
자동 지표 계산기
- 스킬 데이터 + 체감 평가 → 5개 지표 자동 계산
- 위험 패턴 자동 탐지
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from src.modules.data_models import SkillDefinition, PlayerFeedback
from src.config.settings import settings


@dataclass
class MetricsResult:
    """계산된 지표 결과"""
    reaction_margin: float        # 반응 여유 지수 (0~100)
    fairness_score: float         # 타이밍 공정성 점수 (0~100)
    unfair_hit_index: float       # 억까 가능성 지수 (0~100)
    design_intent_rate: float     # 설계 의도 적중률 (0~100) - 체감 있을 때만
    learnability_score: float     # 학습 가능성 점수 (0~100) - 체감 있을 때만

    warnings: list[str]           # 위험 패턴 경고 메시지
    danger_flags: list[str]       # 즉시 검토 필요 항목

    @property
    def overall_risk(self) -> str:
        """종합 위험도: LOW / MEDIUM / HIGH"""
        if self.danger_flags:
            return "HIGH"
        if self.warnings:
            return "MEDIUM"
        return "LOW"

    def to_dict(self) -> dict:
        return {
            "반응 여유 지수": round(self.reaction_margin, 1),
            "타이밍 공정성": round(self.fairness_score, 1),
            "억까 가능성": round(self.unfair_hit_index, 1),
            "설계 의도 적중률": round(self.design_intent_rate, 1),
            "학습 가능성": round(self.learnability_score, 1),
        }


class MetricsCalculator:
    """지표 계산기"""

    def __init__(self):
        self._thresholds = settings.danger_thresholds
        self._ref_ms = settings.reaction_reference_ms

    def calculate(
        self,
        skill: SkillDefinition,
        feedbacks: Optional[list[PlayerFeedback]] = None,
    ) -> MetricsResult:
        """스킬 + 체감 평가로 모든 지표 계산"""

        reaction_margin = self._reaction_margin(skill)
        fairness_score = self._fairness_score(skill, reaction_margin)
        unfair_hit = 100.0 - fairness_score

        # 체감 기반 지표
        design_intent = self._design_intent_rate(feedbacks) if feedbacks else 0.0
        learnability = self._learnability_score(skill, feedbacks) if feedbacks else 0.0

        warnings, danger_flags = self._detect_risks(
            skill, reaction_margin, fairness_score, unfair_hit,
            design_intent, feedbacks
        )

        return MetricsResult(
            reaction_margin=reaction_margin,
            fairness_score=fairness_score,
            unfair_hit_index=unfair_hit,
            design_intent_rate=design_intent,
            learnability_score=learnability,
            warnings=warnings,
            danger_flags=danger_flags,
        )

    # ─────────────────────────────────────────
    # 개별 지표 계산
    # ─────────────────────────────────────────

    def _reaction_margin(self, skill: SkillDefinition) -> float:
        """
        반응 여유 지수 (0~100)
        = min(reaction_window / ref_ms, 1.0) * 100
        """
        if skill.reaction_window_ms <= 0:
            return 0.0
        return min(skill.reaction_window_ms / self._ref_ms, 1.0) * 100.0

    def _fairness_score(self, skill: SkillDefinition, reaction_margin: float) -> float:
        """
        타이밍 공정성 점수 (0~100)
        = 반응여유(50%) + 가이드 품질(30%) + 판정일치(20%)
        """
        # 가이드 점수
        if skill.guide_exists:
            guide_score = (skill.guide_intensity / 5.0) * 100.0
        else:
            guide_score = 0.0

        # 판정 일치 보너스
        match_bonus = 20.0 if skill.guide_match else 0.0

        score = (reaction_margin * 0.5) + (guide_score * 0.3) + match_bonus
        return min(score, 100.0)

    def _design_intent_rate(self, feedbacks: list[PlayerFeedback]) -> float:
        """
        설계 의도 적중률 (0~100)
        = (반응충분성 + 납득도 + 가이드명확성 + 학습가능성) 평균 / 5 * 100
        """
        if not feedbacks:
            return 0.0

        total = 0.0
        for fb in feedbacks:
            score = (fb.reaction_sufficiency + fb.hit_acceptance +
                     fb.guide_clarity + fb.learnability) / 4.0
            total += score

        avg = total / len(feedbacks)
        return (avg / 5.0) * 100.0

    def _learnability_score(
        self,
        skill: SkillDefinition,
        feedbacks: Optional[list[PlayerFeedback]],
    ) -> float:
        """
        학습 가능성 점수 (0~100)
        = (체감 학습가능성 * 0.6 + 체감 가이드명확성 * 0.4) / 5 * 100
        """
        if not feedbacks:
            return 0.0

        total = 0.0
        for fb in feedbacks:
            score = fb.learnability * 0.6 + fb.guide_clarity * 0.4
            total += score

        avg = total / len(feedbacks)
        return (avg / 5.0) * 100.0

    # ─────────────────────────────────────────
    # 위험 패턴 탐지
    # ─────────────────────────────────────────

    def _detect_risks(
        self,
        skill: SkillDefinition,
        reaction_margin: float,
        fairness_score: float,
        unfair_hit: float,
        design_intent: float,
        feedbacks: Optional[list[PlayerFeedback]],
    ) -> tuple[list[str], list[str]]:
        warnings = []
        danger_flags = []

        t = self._thresholds

        # 즉시 위험
        if skill.reaction_window_ms < 250:
            danger_flags.append("인간 반응속도(250ms) 미만 - 회피 물리적 불가능")

        if not skill.guide_exists and unfair_hit > t["unfair_hit"]:
            danger_flags.append("가이드 없는 고위험 스킬 - 즉시 가이드 추가 필요")

        if not skill.guide_match:
            danger_flags.append("판정 범위와 가이드 불일치 - 억까 직접 원인")

        if fairness_score < t["fairness_score"]:
            danger_flags.append(f"타이밍 공정성 {fairness_score:.0f}점 - 재설계 필요")

        # 경고
        if reaction_margin < t["reaction_margin"]:
            warnings.append(f"반응 여유 {reaction_margin:.0f}점 - 선딜 증가 또는 회피 구간 확대 검토")

        if feedbacks:
            avg_stress = sum(f.stress for f in feedbacks) / len(feedbacks)
            avg_retry = sum(f.retry_intent for f in feedbacks) / len(feedbacks)

            if avg_stress > 4.0 and avg_retry < 2.0:
                danger_flags.append(f"스트레스 과다(평균 {avg_stress:.1f}) + 재도전 의사 낮음 - 이탈 위험")

            if design_intent < t["design_intent"]:
                warnings.append(f"설계 의도 적중률 {design_intent:.0f}점 - 기획 재검토 권고")

        return warnings, danger_flags


# 전역 싱글톤
calculator = MetricsCalculator()
