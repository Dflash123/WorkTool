"""
데이터 모델 정의 - 모든 DB 구조의 기준
Google Sheets 행 ↔ Python 객체 변환 담당
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import uuid


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _new_id() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────
# Sheet 1: 스킬 정의
# ─────────────────────────────────────────
@dataclass
class SkillDefinition:
    monster_name: str
    skill_name: str
    skill_type: str          # attack / aoe / special / buff
    version: str
    pre_delay_ms: int        # 선딜 (ms)
    active_duration_ms: int  # 판정 지속 (ms)
    post_delay_ms: int       # 후딜 (ms)
    dodge_start_ms: int      # 회피 가능 시작 (ms)
    dodge_end_ms: int        # 회피 가능 종료 (ms)
    targeting_type: str      # area / single / line / random

    # 가이드 이펙트
    guide_exists: bool = False
    guide_start_ms: int = 0
    guide_duration_ms: int = 0
    guide_type: str = "none"      # visual / sound / both / none
    guide_intensity: int = 0      # 1~5
    guide_visibility: int = 0     # 1~5
    guide_match: bool = True
    guide_offset_ms: int = 0

    design_intent: str = ""

    # 자동 계산 (저장 전 compute() 호출)
    total_duration_ms: int = 0
    reaction_window_ms: int = 0

    # 메타
    monster_id: str = ""
    skill_id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def compute(self) -> "SkillDefinition":
        """자동 계산 필드 갱신 후 자신을 반환"""
        self.total_duration_ms = self.pre_delay_ms + self.active_duration_ms + self.post_delay_ms
        self.reaction_window_ms = max(0, self.dodge_end_ms - self.dodge_start_ms)
        self.updated_at = _now()
        return self

    def to_row(self) -> list:
        """Google Sheets 행 순서로 변환"""
        return [
            self.skill_id, self.monster_id, self.monster_name,
            self.skill_name, self.skill_type, self.version,
            self.pre_delay_ms, self.active_duration_ms, self.post_delay_ms,
            self.total_duration_ms, self.dodge_start_ms, self.dodge_end_ms,
            self.reaction_window_ms, self.targeting_type,
            str(self.guide_exists), self.guide_start_ms, self.guide_duration_ms,
            self.guide_type, self.guide_intensity, self.guide_visibility,
            str(self.guide_match), self.guide_offset_ms,
            self.design_intent, self.created_at, self.updated_at,
        ]

    @staticmethod
    def headers() -> list[str]:
        return [
            "skill_id", "monster_id", "monster_name",
            "skill_name", "skill_type", "version",
            "pre_delay_ms", "active_duration_ms", "post_delay_ms",
            "total_duration_ms", "dodge_start_ms", "dodge_end_ms",
            "reaction_window_ms", "targeting_type",
            "guide_exists", "guide_start_ms", "guide_duration_ms",
            "guide_type", "guide_intensity", "guide_visibility",
            "guide_match", "guide_offset_ms",
            "design_intent", "created_at", "updated_at",
        ]

    @staticmethod
    def from_row(row: list) -> "SkillDefinition":
        """Google Sheets 행 → 객체 변환"""
        def safe_int(v): return int(v) if v else 0
        def safe_bool(v): return str(v).upper() == "TRUE"

        return SkillDefinition(
            skill_id=row[0], monster_id=row[1], monster_name=row[2],
            skill_name=row[3], skill_type=row[4], version=row[5],
            pre_delay_ms=safe_int(row[6]), active_duration_ms=safe_int(row[7]),
            post_delay_ms=safe_int(row[8]), total_duration_ms=safe_int(row[9]),
            dodge_start_ms=safe_int(row[10]), dodge_end_ms=safe_int(row[11]),
            reaction_window_ms=safe_int(row[12]), targeting_type=row[13],
            guide_exists=safe_bool(row[14]), guide_start_ms=safe_int(row[15]),
            guide_duration_ms=safe_int(row[16]), guide_type=row[17],
            guide_intensity=safe_int(row[18]), guide_visibility=safe_int(row[19]),
            guide_match=safe_bool(row[20]), guide_offset_ms=safe_int(row[21]),
            design_intent=row[22] if len(row) > 22 else "",
            created_at=row[23] if len(row) > 23 else _now(),
            updated_at=row[24] if len(row) > 24 else _now(),
        )


# ─────────────────────────────────────────
# Sheet 2: 테스트 로그
# ─────────────────────────────────────────
@dataclass
class TestLog:
    skill_id: str
    monster_name: str
    skill_name: str
    test_type: str        # internal / live
    test_date: str
    tester_name: str
    test_version: str
    test_environment: str  # 로컬 / QA서버 / 라이브
    participant_count: int = 1
    notes: str = ""

    log_id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)

    def to_row(self) -> list:
        return [
            self.log_id, self.skill_id, self.monster_name, self.skill_name,
            self.test_type, self.test_date, self.tester_name,
            self.test_version, self.test_environment, self.participant_count,
            self.notes, self.created_at,
        ]

    @staticmethod
    def headers() -> list[str]:
        return [
            "log_id", "skill_id", "monster_name", "skill_name",
            "test_type", "test_date", "tester_name",
            "test_version", "test_environment", "participant_count",
            "notes", "created_at",
        ]

    @staticmethod
    def from_row(row: list) -> "TestLog":
        def safe_int(v): return int(v) if v else 0
        return TestLog(
            log_id=row[0], skill_id=row[1], monster_name=row[2],
            skill_name=row[3], test_type=row[4], test_date=row[5],
            tester_name=row[6], test_version=row[7], test_environment=row[8],
            participant_count=safe_int(row[9]),
            notes=row[10] if len(row) > 10 else "",
            created_at=row[11] if len(row) > 11 else _now(),
        )


# ─────────────────────────────────────────
# Sheet 3: 플레이어 체감 평가
# ─────────────────────────────────────────
@dataclass
class PlayerFeedback:
    skill_id: str
    log_id: str
    tester_name: str

    # 리커트 1~5
    reaction_sufficiency: int = 3   # 반응 시간 충분성
    hit_acceptance: int = 3         # 피격 납득도
    guide_clarity: int = 3          # 가이드 명확성
    attack_readability: int = 3     # 공격 가독성
    learnability: int = 3           # 학습 가능성
    stress: int = 3                 # 스트레스 (높을수록 나쁨)
    retry_intent: int = 3           # 재도전 의사

    opinion: str = ""

    feedback_id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)

    def to_row(self) -> list:
        return [
            self.feedback_id, self.skill_id, self.log_id, self.tester_name,
            self.reaction_sufficiency, self.hit_acceptance, self.guide_clarity,
            self.attack_readability, self.learnability, self.stress, self.retry_intent,
            self.opinion, self.created_at,
        ]

    @staticmethod
    def headers() -> list[str]:
        return [
            "feedback_id", "skill_id", "log_id", "tester_name",
            "reaction_sufficiency", "hit_acceptance", "guide_clarity",
            "attack_readability", "learnability", "stress", "retry_intent",
            "opinion", "created_at",
        ]

    @staticmethod
    def from_row(row: list) -> "PlayerFeedback":
        def safe_int(v): return int(v) if v else 3
        return PlayerFeedback(
            feedback_id=row[0], skill_id=row[1], log_id=row[2],
            tester_name=row[3],
            reaction_sufficiency=safe_int(row[4]), hit_acceptance=safe_int(row[5]),
            guide_clarity=safe_int(row[6]), attack_readability=safe_int(row[7]),
            learnability=safe_int(row[8]), stress=safe_int(row[9]),
            retry_intent=safe_int(row[10]),
            opinion=row[11] if len(row) > 11 else "",
            created_at=row[12] if len(row) > 12 else _now(),
        )


# ─────────────────────────────────────────
# Sheet 4: 밸런스 수정 히스토리
# ─────────────────────────────────────────
@dataclass
class BalanceHistory:
    skill_id: str
    monster_name: str
    skill_name: str
    version_from: str
    version_to: str
    field_changed: str
    value_before: str
    value_after: str
    change_reason: str
    changed_by: str

    history_id: str = field(default_factory=_new_id)
    changed_at: str = field(default_factory=_now)

    def to_row(self) -> list:
        return [
            self.history_id, self.skill_id, self.monster_name, self.skill_name,
            self.version_from, self.version_to, self.field_changed,
            self.value_before, self.value_after, self.change_reason,
            self.changed_by, self.changed_at,
        ]

    @staticmethod
    def headers() -> list[str]:
        return [
            "history_id", "skill_id", "monster_name", "skill_name",
            "version_from", "version_to", "field_changed",
            "value_before", "value_after", "change_reason",
            "changed_by", "changed_at",
        ]

    @staticmethod
    def from_row(row: list) -> "BalanceHistory":
        return BalanceHistory(
            history_id=row[0], skill_id=row[1], monster_name=row[2],
            skill_name=row[3], version_from=row[4], version_to=row[5],
            field_changed=row[6], value_before=row[7], value_after=row[8],
            change_reason=row[9], changed_by=row[10],
            changed_at=row[11] if len(row) > 11 else _now(),
        )
