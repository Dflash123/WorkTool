# Monster Skill Analyzer - Architecture

## 개요

게임 몬스터 스킬 타이밍·체감·밸런스를 기록·분석하는 기획자용 툴.
Python + Streamlit 기반 웹앱, Google Sheets를 데이터 저장소로 사용.

## 실행 흐름

```
run.bat 더블클릭
→ Streamlit 로컬 서버 실행 (localhost:8501)
→ 브라우저 자동 오픈
→ Google Sheets API 연결
→ 데이터 읽기/쓰기
```

## 레이어 구조

```
UI Layer (src/ui/)
    → Streamlit pages/components
    → 사용자 입력 수집, 결과 표시

Module Layer (src/modules/)
    → data_models.py    : 데이터 구조 정의 (dataclass)
    → metrics_calculator.py : 자동 지표 계산

Service Layer (src/services/)
    → sheets_service.py : Google Sheets CRUD
    → 인터페이스 기반 → 나중에 DB/다른 백엔드로 교체 가능

Config Layer (src/config/)
    → config.yaml       : 사용자가 직접 편집 (계정, 시트ID 등)
    → settings.py       : config.yaml 로더
```

## 확장 포인트

- `SheetsService`를 `DatabaseService`로 교체 가능 (동일 인터페이스)
- 새 페이지 추가: `src/ui/pages/` 에 파일 추가 후 `app.py` 메뉴 등록
- 새 지표 추가: `metrics_calculator.py`의 `calculate()` 메서드 확장
- 새 데이터 필드: `data_models.py` dataclass 필드 추가 + 시트 컬럼 추가

## 기술 스택

| 역할 | 기술 |
|------|------|
| UI | Streamlit |
| 차트 | Plotly |
| 데이터 저장 | Google Sheets (gspread) |
| 인증 | Google Service Account JSON |
| 설정 | YAML |
| 패키징 | PyInstaller (.exe) |

## 디렉토리 구조

```
monster-skill-analyzer/
├── src/
│   ├── app.py
│   ├── config/
│   │   ├── settings.py
│   │   └── config.yaml
│   ├── services/
│   │   └── sheets_service.py
│   ├── modules/
│   │   ├── data_models.py
│   │   └── metrics_calculator.py
│   ├── ui/
│   │   ├── pages/
│   │   │   ├── skill_input.py
│   │   │   ├── test_log.py
│   │   │   ├── feedback.py
│   │   │   ├── analysis.py
│   │   │   └── settings_page.py
│   │   └── components/
│   │       └── charts.py
│   └── utils/
│       └── validators.py
├── credentials/
│   └── (service_account.json 여기에 배치)
├── docs/
│   ├── ARCHITECTURE.md  ← 이 파일
│   ├── DB_SCHEMA.md
│   ├── METRICS.md
│   └── SETUP.md
├── tests/
├── run.bat
├── build.bat
└── requirements.txt
```
