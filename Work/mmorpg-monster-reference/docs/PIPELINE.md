# Pipeline — Data Collection Engine

## 전체 파이프라인

```
[1] YouTube 검색
        |
        v
[2] 영상 필터링 (조회수 10,000+, engagement 점수 계산)
        |
        v
[3] 텍스트 데이터 수집
    - 영상 description
    - 자막 (있는 경우)
    - 댓글 샘플 (상위 N개)
        |
        v
[4] 수집 가능성 판단
    - description 너무 짧으면 → skip
    - description + comments 모두 없으면 → skip
        |
        v
[5] Claude API 패턴 추출
    - 보스 패턴 타임라인 생성 (HP% 기반)
    - mechanic_complexity 점수 계산
        |
        v
[6] JSON DB 업데이트 (upsert)
    - monsters.json
    - patterns.json
    - videos.json
```

---

## 단계별 상세

### [1] YouTube 검색 (`collector/youtube_searcher.py`)

검색 키워드:
- `MMORPG raid boss fight`
- `MMO boss mechanics guide`
- `raid boss wipe mechanic`
- `hard raid boss`
- `raid boss strategy`

게임별 키워드도 조합:
- `{game_name} raid boss guide`
- `{game_name} boss mechanics`

### [2] 영상 필터링

Engagement 점수 계산:
```
engagement_score = (view_count * 0.6) + (comment_count * 100 * 0.4)
```
- 조회수 10,000 미만 제외
- engagement_score 기준 내림차순 정렬
- 최근 업로드 영상 가중치 부여 (1년 이내 +10%)

### [3] 텍스트 데이터 수집 (`collector/`)

| 수집 항목 | 담당 파일 | 비고 |
|-----------|-----------|------|
| 영상 메타데이터 | `metadata_collector.py` | title, description, views 등 |
| 자막 | `subtitle_collector.py` | 없으면 None 반환 |
| 댓글 샘플 | `comment_sampler.py` | 좋아요 상위 20개 |

### [4] 수집 가능성 판단

Skip 조건:
- description이 100자 미만
- description + 자막 없음 AND 댓글 5개 미만

### [5] Claude API 패턴 추출 (`timeline_extractor/llm_extractor.py`)

**입력 데이터:**
- 영상 제목
- description
- 자막 전문 (있는 경우)
- 댓글 샘플

**프롬프트 목표:**
- 보스 패턴을 HP% 구간별로 추출
- 각 패턴의 type, difficulty, reaction_window 추정
- mechanic_complexity 1-10 점수 평가

**모델:** claude-3-5-sonnet-20241022
**Fallback:** gpt-4o (Claude API 실패 시)

### [6] DB 업데이트 (`timeline_extractor/db_writer.py`)

Upsert 규칙:
- `monster_id` 기준으로 기존 레코드 확인
- 존재 → 업데이트 (패턴은 중복 방지 후 추가)
- 미존재 → 새 레코드 삽입
- `last_updated` 항상 갱신

---

## 자막 없을 때 처리 전략

```
자막 있음: 자막 + description + 댓글 → LLM 분석
자막 없음: description + 댓글 → LLM 분석
description 짧음 + 댓글 없음: 해당 영상 skip (analysis_status = "skipped")
```

---

## 스케줄러 (`scheduler/weekly_update.py`)

- 실행 방식: Windows Task Scheduler → `python run_collector.py`
- 실행 주기: 매주
- 로그 위치: `logs/collector_YYYYMMDD.log`
- 에러 발생 시: 해당 영상 skip 후 계속 진행 (전체 중단 없음)

---

## 로그 포맷

```
[2026-03-07 10:00:00] [collector] INFO: 검색 시작 - keyword: "MMORPG raid boss fight"
[2026-03-07 10:00:05] [collector] INFO: 영상 발견 - video_id: abc123, views: 500000
[2026-03-07 10:00:10] [timeline_extractor] INFO: 패턴 추출 시작 - monster: wow_ragnaros
[2026-03-07 10:00:15] [timeline_extractor] INFO: 패턴 추출 완료 - 8개 패턴
[2026-03-07 10:00:16] [db_writer] INFO: upsert 완료 - monsters.json, patterns.json, videos.json
```
