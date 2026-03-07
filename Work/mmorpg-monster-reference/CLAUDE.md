# CLAUDE.md — 기획 레퍼런스 문서 (Planning Reference)

> **주의:** 이 폴더(`mmorpg-monster-reference/`)는 기획 단계 레퍼런스 문서 모음입니다.
> 실제 구현은 `Work/web_tool/` 안에서 이루어집니다.
> - 수집 모듈: `Work/web_tool/collector/`
> - 추출 모듈: `Work/web_tool/timeline_extractor/`
> - 데이터: `Work/web_tool/data/`

---

# DUAL CLAUDE WARNING — 반드시 먼저 읽을 것

이 프로젝트는 **Claude Code 인스턴스 2개가 동시에 작업 중**입니다.
파일 소유권 경계를 반드시 확인하고, 담당 외 파일은 절대 수정하지 않습니다.
의심스러운 경우 수정하지 말고 사용자에게 먼저 확인합니다.

---

## 모듈 분담

| 모듈 | 담당 | 책임 파일/폴더 |
|------|------|--------------|
| data_collection_engine | Claude A | `collector/`, `timeline_extractor/`, `scheduler/`, `data/monsters.json`, `data/patterns.json`, `data/videos.json`, `run_collector.py`, `.env.example` |
| web_tool | Claude B | `frontend/`, `app.py`, `data/comments.json`, `data/votes.json` |

---

## Claude A — 절대 수정 금지 목록

- `frontend/`
- `app.py`
- `data/comments.json`
- `data/votes.json`

## Claude B — 절대 수정 금지 목록

- `collector/`
- `timeline_extractor/`
- `scheduler/`
- `data/monsters.json`
- `data/patterns.json`
- `data/videos.json`
- `run_collector.py`
- `.env.example`

---

## 공유 파일 규칙

- `requirements.txt` — 변경 전 상대 모듈 의존성 충돌 여부 확인 필수
- `README.md` — 양쪽 편집 가능하나 동시 수정 금지
- `docs/` — 각자 담당 모듈 문서만 편집

---

## Project Overview

MMORPG 보스 몬스터 패턴을 YouTube 영상 텍스트 기반으로 자동 분석하여
게임 디자인 레퍼런스 JSON DB를 구축하는 시스템.

- 수집 파이프라인: YouTube API → 텍스트 수집 → Claude API 패턴 추출 → JSON DB 저장
- 업데이트 주기: 주간 (Windows Task Scheduler)
- 데이터 기준: 보스 HP % 기반 전투 로그 타임라인

## 문서

- [아키텍처](docs/ARCHITECTURE.md)
- [데이터 스키마](docs/DATA_SCHEMA.md)
- [수집 파이프라인](docs/PIPELINE.md)

## 환경 설정

```bash
cp .env.example .env
# .env 파일에 CLAUDE_API_KEY, YOUTUBE_API_KEY 입력
pip install -r requirements.txt
```

## 실행

```bash
python run_collector.py
```

## 개발 규칙 (RULES.md 준수)

- 폴더명: 소문자 하이픈 구분
- 파일명: 소문자 언더스코어 구분
- 모든 하위 폴더에 README.md 포함
- 로그는 `logs/` 폴더에 저장, 툴 이름 태깅 필수
- 시크릿은 `.env`로 관리, 소스코드에 하드코딩 금지
