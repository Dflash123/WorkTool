# DB Schema - Google Sheets 구조

## 시트 구성

Google Spreadsheet 1개에 4개 시트(탭)로 구성.

---

## Sheet 1: SkillDefinitions (스킬 정의)

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| skill_id | UUID | 고유 ID (자동생성) | `550e8400-e29b-41d4-a716` |
| monster_id | string | 몬스터 ID | `MON_001` |
| monster_name | string | 몬스터 이름 | `불꽃 드래곤` |
| skill_name | string | 스킬 이름 | `화염 브레스` |
| skill_type | string | 스킬 유형 | `attack` / `aoe` / `special` |
| version | string | 버전 | `1.0.0` |
| pre_delay_ms | int | 선딜 시간(ms) | `800` |
| active_duration_ms | int | 판정 지속 시간(ms) | `400` |
| post_delay_ms | int | 후딜 시간(ms) | `600` |
| total_duration_ms | int | 총 행동 시간(ms) - 자동계산 | `1800` |
| dodge_start_ms | int | 회피 가능 시작(ms) | `300` |
| dodge_end_ms | int | 회피 가능 종료(ms) | `700` |
| reaction_window_ms | int | 실제 반응 가능 시간(ms) - 자동계산 | `400` |
| targeting_type | string | 타겟팅 방식 | `area` / `single` / `line` / `random` |
| guide_exists | bool | 가이드 이펙트 존재 여부 | `TRUE` |
| guide_start_ms | int | 가이드 시작 시점(ms) | `0` |
| guide_duration_ms | int | 가이드 지속 시간(ms) | `800` |
| guide_type | string | 가이드 유형 | `visual` / `sound` / `both` / `none` |
| guide_intensity | int | 가이드 강도 (1~5) | `4` |
| guide_visibility | int | 시야 가시성 (1~5) | `3` |
| guide_match | bool | 판정과 가이드 일치 여부 | `TRUE` |
| guide_offset_ms | int | 가이드 오차(ms) | `50` |
| design_intent | string | 설계 의도 메모 | `중급자 대상, 패턴 학습 유도` |
| created_at | datetime | 생성일시 | `2024-03-01 10:00:00` |
| updated_at | datetime | 수정일시 | `2024-03-02 15:30:00` |

---

## Sheet 2: TestLogs (테스트 로그)

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| log_id | UUID | 고유 ID (자동생성) | |
| skill_id | UUID | 연결된 스킬 ID | |
| monster_name | string | 몬스터 이름 (참조용) | `불꽃 드래곤` |
| skill_name | string | 스킬 이름 (참조용) | `화염 브레스` |
| test_type | string | 테스트 유형 | `internal` / `live` |
| test_date | date | 테스트 날짜 | `2024-03-01` |
| tester_name | string | 테스터 이름 | `김기획` |
| test_version | string | 테스트 버전 | `1.0.0` |
| test_environment | string | 테스트 환경 | `로컬` / `QA서버` / `라이브` |
| participant_count | int | 참여 인원 수 | `5` |
| notes | string | 테스트 메모 | `신규 유저 대상 테스트` |
| created_at | datetime | 기록 일시 | |

---

## Sheet 3: PlayerFeedback (플레이어 체감 평가)

| 컬럼 | 타입 | 설명 | 범위 |
|------|------|------|------|
| feedback_id | UUID | 고유 ID | |
| skill_id | UUID | 연결된 스킬 ID | |
| log_id | UUID | 연결된 테스트 로그 ID | |
| tester_name | string | 평가자 이름 | |
| reaction_sufficiency | int | 반응 시간 충분성 | 1~5 |
| hit_acceptance | int | 피격 납득도 | 1~5 |
| guide_clarity | int | 가이드 명확성 | 1~5 |
| attack_readability | int | 공격 가독성 | 1~5 |
| learnability | int | 학습 가능성 | 1~5 |
| stress | int | 스트레스 | 1~5 |
| retry_intent | int | 재도전 의사 | 1~5 |
| opinion | string | 서술형 의견 | |
| created_at | datetime | 기록 일시 | |

---

## Sheet 4: BalanceHistory (밸런스 수정 히스토리)

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| history_id | UUID | 고유 ID | |
| skill_id | UUID | 연결된 스킬 ID | |
| monster_name | string | 몬스터 이름 (참조용) | |
| skill_name | string | 스킬 이름 (참조용) | |
| version_from | string | 수정 전 버전 | `1.0.0` |
| version_to | string | 수정 후 버전 | `1.1.0` |
| field_changed | string | 변경된 필드명 | `pre_delay_ms` |
| value_before | string | 변경 전 값 | `600` |
| value_after | string | 변경 후 값 | `800` |
| change_reason | string | 변경 이유 | `억까 가능성 높음, 선딜 증가` |
| changed_by | string | 수정자 | `김기획` |
| changed_at | datetime | 수정 일시 | |

---

## 시트 탭 색상 규칙 (Google Sheets)

| 시트 | 색상 |
|------|------|
| SkillDefinitions | 파란색 |
| TestLogs | 초록색 |
| PlayerFeedback | 주황색 |
| BalanceHistory | 빨간색 |
