# Pipeline — Data Collection Engine

## 담당: Claude A (data_collection_engine)

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
    - 댓글 샘플 (상위 20개)
        |
        v
[4] 수집 가능성 판단
    - description 100자 미만 → skip
    - description + 자막 없음 AND 댓글 5개 미만 → skip
        |
        v
[5] Claude API 패턴 추출
    - 보스 패턴 타임라인 생성 (HP% 기반)
    - mechanic_complexity 점수 계산 (1-10)
        |
        v
[6] JSON DB 업데이트 (upsert)
    - data/monsters.json
    - data/patterns.json
    - data/videos.json
```

## 단계별 상세

### [1] YouTube 검색 (`collector/youtube_searcher.py`)

검색 키워드:
- `MMORPG raid boss fight`
- `MMO boss mechanics guide`
- `raid boss wipe mechanic`
- `hard raid boss`
- `raid boss strategy`
- `{game_name} raid boss guide` (게임별 조합)

### [2] Engagement 점수 계산

```
engagement_score = (view_count * 0.6) + (comment_count * 100 * 0.4)
```
- 조회수 10,000 미만 제외
- 최근 1년 이내 업로드 +10% 가중치

### [3] 텍스트 수집 (`collector/`)

| 수집 항목 | 담당 파일 | 비고 |
|-----------|-----------|------|
| 영상 메타데이터 | `metadata_collector.py` | title, description, views 등 |
| 자막 | `subtitle_collector.py` | 없으면 None 반환 |
| 댓글 샘플 | `comment_sampler.py` | 좋아요 상위 20개 |

### [5] Claude API 패턴 추출 (`timeline_extractor/llm_extractor.py`)

**입력:** 영상 제목 + description + 자막 + 댓글 샘플
**출력:** HP% 기반 패턴 타임라인 + mechanic_complexity 점수

**모델:** claude-3-5-sonnet-20241022 → fallback: gpt-4o

### [6] DB 업데이트 규칙 (`timeline_extractor/db_writer.py`)

- `monster_id` 기준 upsert
- 동일 `hp_percent` + `pattern_name` 조합 → 중복 방지
- `last_updated` 항상 갱신

## 자막 없을 때 처리

```
자막 있음: 자막 + description + 댓글 → LLM 분석
자막 없음: description + 댓글 → LLM 분석
description 짧음 + 댓글 없음: skip (analysis_status = "skipped")
```

## 스케줄러

- 방식: Windows Task Scheduler → `python run_collector.py`
- 주기: 매주
- 로그: `logs/collector_YYYYMMDD.log`
- 에러 발생 시: 해당 영상 skip 후 계속 진행

## 로그 포맷

```
[2026-03-07 10:00:00] [collector] INFO: 검색 시작 - "MMORPG raid boss fight"
[2026-03-07 10:00:05] [collector] INFO: 영상 발견 - video_id: abc123, views: 500000
[2026-03-07 10:00:10] [timeline_extractor] INFO: 패턴 추출 시작 - wow_ragnaros
[2026-03-07 10:00:15] [timeline_extractor] INFO: 패턴 추출 완료 - 8개 패턴
[2026-03-07 10:00:16] [db_writer] INFO: upsert 완료 - monsters/patterns/videos
```
