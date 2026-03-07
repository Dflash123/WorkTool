"""
보스 메카닉 복잡도(mechanic_complexity) 계산
LLM 제공 점수 + 규칙 기반 보정으로 최종 1-10 점수 산출
"""
from base.utils import get_logger

logger = get_logger("timeline_extractor")


def calculate_complexity(patterns: list[dict], llm_score: int | None = None) -> int:
    """
    패턴 목록과 LLM 점수를 조합해 최종 mechanic_complexity(1-10) 반환.
    - LLM 점수 있으면: LLM 70% + 규칙 기반 30% 블렌딩
    - LLM 점수 없으면: 규칙 기반 단독 사용
    """
    rule_score = _rule_based_score(patterns)

    if llm_score is not None and 1 <= llm_score <= 10:
        final = round(llm_score * 0.7 + rule_score * 0.3)
        score = max(1, min(10, final))
        logger.info(
            f"복잡도 계산 완료 - LLM: {llm_score}, rule: {rule_score}, final: {score}"
        )
        return score

    logger.info(f"복잡도 계산 완료 (규칙 기반) - score: {rule_score}")
    return rule_score


def _rule_based_score(patterns: list[dict]) -> int:
    """
    패턴 수, 유형 다양성, High 난이도 비율로 복잡도 추정.
    기준:
    1-3: 단순 AOE 수준 (패턴 ≤ 3)
    4-6: 일반 레이드 (패턴 4-7)
    7-8: 복합 메카닉 (패턴 8-11 또는 유형 다양)
    9-10: 퍼즐/협동 메카닉 (패턴 12+)
    """
    if not patterns:
        return 1

    pattern_count = len(patterns)
    unique_types = len({p.get("pattern_type") for p in patterns})
    high_difficulty_count = sum(1 for p in patterns if p.get("difficulty") == "High")
    puzzle_count = sum(
        1 for p in patterns if p.get("pattern_type") in {"Puzzle", "Mechanic"}
    )

    score = (
        pattern_count * 0.5
        + unique_types * 0.8
        + high_difficulty_count * 0.4
        + puzzle_count * 0.8
    )

    return max(1, min(10, round(score)))
