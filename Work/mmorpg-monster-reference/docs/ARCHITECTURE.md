# Architecture — MMORPG Monster Reference System

## 시스템 개요

YouTube MMORPG 보스 전투 영상의 텍스트 데이터를 수집하고,
Claude API로 패턴 타임라인을 추출하여 JSON DB를 자동 구축하는 시스템.

## 전체 구조

```
[YouTube Data API v3]
        |
        v
[collector/]                  # 영상 검색 + 텍스트 데이터 수집
  youtube_searcher.py         # 키워드 검색, engagement 점수 기반 정렬
  metadata_collector.py       # 영상 제목/설명/views/comments 수집
  subtitle_collector.py       # 자막 수집 (없으면 스킵)
  comment_sampler.py          # 댓글 상위 N개 샘플링
        |
        v
[timeline_extractor/]         # Claude API로 패턴 타임라인 추출
  llm_extractor.py            # Claude API 호출, 프롬프트 관리
  pattern_parser.py           # LLM 응답 → 구조화된 dict
  complexity_scorer.py        # mechanic_complexity 자동 계산 (LLM)
  db_writer.py                # JSON DB upsert 저장
        |
        v
[data/]                       # JSON 데이터베이스
  monsters.json               # 몬스터 기본 정보 + 평가 데이터
  patterns.json               # HP% 기반 패턴 타임라인
  videos.json                 # YouTube 영상 메타데이터

[scheduler/]                  # 주간 자동 실행
  weekly_update.py

run_collector.py              # 전체 파이프라인 엔트리포인트
```

## 레이어 책임

| 레이어 | 폴더 | 역할 |
|--------|------|------|
| 수집 | `collector/` | YouTube API 호출, 텍스트 추출 |
| 추출 | `timeline_extractor/` | LLM 분석, DB 저장 |
| 데이터 | `data/` | JSON 파일 관리 |
| 스케줄링 | `scheduler/` | 주간 자동 실행 |

## 기술 스택

| 역할 | 기술 |
|------|------|
| 언어 | Python 3.10+ |
| YouTube 수집 | YouTube Data API v3 (`google-api-python-client`) |
| LLM 분석 | Anthropic Claude API (`anthropic`) |
| 환경변수 | python-dotenv |
| 스케줄러 | Windows Task Scheduler → `run_collector.py` |
| 로깅 | Python logging (logs/ 폴더) |

## 모듈 간 의존성

```
collector/  →  timeline_extractor/  →  data/
```

- `collector/` 는 `timeline_extractor/` 를 import하지 않는다
- `timeline_extractor/` 는 `collector/` 를 import하지 않는다
- 데이터 전달은 run_collector.py 에서 조율
- 공통 유틸리티는 `base/utils.py` 에만 위치 (2개 이상 사용 시에만)

## web_tool 모듈과의 인터페이스

`data/monsters.json`, `data/patterns.json`, `data/videos.json` 을 통해
data_collection_engine이 생성한 데이터를 web_tool이 읽어 표시한다.

- data_collection_engine: 쓰기 담당
- web_tool: 읽기 담당
- 동시 쓰기 금지 (스케줄러 실행 중 web_tool은 읽기만)
