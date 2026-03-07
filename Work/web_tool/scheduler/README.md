# scheduler

주간 자동 수집 실행을 관리하는 모듈.

## 담당: Claude A (data_collection_engine)

## 파일 구성 (개발 예정)

| 파일 | 역할 |
|------|------|
| `weekly_update.py` | 전체 파이프라인 주간 실행 로직 |

## Windows Task Scheduler 설정

1. 작업 스케줄러 열기
2. 기본 작업 만들기
3. 트리거: 매주 원하는 요일/시간
4. 동작: `python {프로젝트_경로}/run_collector.py`

## 로그

실행 로그는 `logs/collector_YYYYMMDD.log` 에 저장됩니다.
