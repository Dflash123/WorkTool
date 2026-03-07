# MMORPG Monster Reference System

MMORPG 보스 몬스터 패턴을 YouTube 영상 텍스트 기반으로 자동 분석하여
게임 디자인 레퍼런스 JSON DB를 구축하는 시스템.

## 모듈 구성

| 모듈 | 설명 | 담당 |
|------|------|------|
| data_collection_engine | YouTube 수집 + Claude API 패턴 추출 | Claude A |
| web_tool | 데이터 조회/시각화 웹 인터페이스 | Claude B |

## 빠른 시작

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 수집 실행
python run_collector.py
```

## 데이터 흐름

```
YouTube API → 텍스트 수집 → Claude API 분석 → JSON DB → Web UI
```

## 문서

- [아키텍처](docs/ARCHITECTURE.md)
- [데이터 스키마](docs/DATA_SCHEMA.md)
- [수집 파이프라인](docs/PIPELINE.md)

## 디렉토리 구조

```
mmorpg-monster-reference/
├── collector/              # YouTube 수집 모듈
├── timeline_extractor/     # LLM 패턴 추출 모듈
├── scheduler/              # 주간 자동 실행
├── data/
│   ├── monsters.json       # 몬스터 기본 정보 + 평가
│   ├── patterns.json       # HP% 기반 패턴 타임라인
│   └── videos.json         # YouTube 영상 메타데이터
├── docs/
├── logs/
├── run_collector.py        # 파이프라인 엔트리포인트
└── .env.example
```
