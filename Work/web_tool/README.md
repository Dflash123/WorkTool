# web_tool — MMORPG Monster Design Web Tool

MMORPG 몬스터 패턴 분석 데이터를 시각화하고 팀이 협업할 수 있는 로컬 웹 분석 툴.

## 빠른 시작

```bash
cd web_tool
pip install flask
python app.py
```

브라우저에서 `http://localhost:5000` 접속.
팀원 접속: `http://<서버IP>:5000` (같은 LAN)

## 페이지

| URL | 설명 |
|-----|------|
| `/` | 몬스터 DB 목록 (필터/검색) |
| `/monster?id=xxx` | 패턴 타임라인 + YouTube 영상 + 댓글/투표 |
| `/ranking` | 보스 랭킹 4종 |
| `/dashboard` | 분석 차트 대시보드 |

## 구조

```
web_tool/
├── app.py              Flask API 서버
├── data/
│   ├── monsters.json   [읽기전용] collector 관리
│   ├── patterns.json   [읽기전용] timeline_extractor 관리
│   ├── videos.json     [읽기전용] collector 관리
│   ├── comments.json   [읽기+쓰기] web_tool 관리
│   └── votes.json      [읽기+쓰기] web_tool 관리
├── frontend/
│   ├── index.html
│   ├── monster.html
│   ├── ranking.html
│   ├── dashboard.html
│   ├── style.css
│   └── script.js
└── docs/
    ├── SCHEMA.md
    └── ARCHITECTURE.md
```

## 기술 스택

- **Backend**: Python Flask
- **Frontend**: HTML5 + CSS3 + Vanilla JS
- **Chart**: Chart.js (CDN)
- **데이터**: JSON 파일

## 주의사항

`data/monsters.json`, `data/patterns.json`, `data/videos.json`은 `data_collection_engine` 모듈이 관리한다.
이 파일들을 직접 수정하면 데이터 파이프라인 충돌이 발생한다.

상세 내용: `CLAUDE.md`, `docs/ARCHITECTURE.md`
