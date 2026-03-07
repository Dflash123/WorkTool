# Architecture — web_tool

## 시스템 전체 구조

```
WorkTool/
├── data_collection_engine/          (Instance A - 별도 Claude Code)
│   ├── collector/                   몬스터/영상 데이터 수집
│   └── timeline_extractor/          패턴 타임라인 추출
│
├── web_tool/                        (Instance B - 이 모듈)
│   ├── app.py                       Flask API 서버
│   ├── frontend/                    HTML/CSS/JS
│   └── data/                        JSON 데이터 파일
│
└── data/                            공유 데이터 디렉토리
    ├── monsters.json   ← Instance A 쓰기, Instance B 읽기
    ├── patterns.json   ← Instance A 쓰기, Instance B 읽기
    ├── videos.json     ← Instance A 쓰기, Instance B 읽기
    ├── comments.json   ← Instance B만 읽기+쓰기
    └── votes.json      ← Instance B만 읽기+쓰기
```

## Flask API 구조

```
app.py
├── GET  /                          → frontend/index.html 서빙
├── GET  /monster                   → frontend/monster.html 서빙
├── GET  /ranking                   → frontend/ranking.html 서빙
├── GET  /dashboard                 → frontend/dashboard.html 서빙
│
├── GET  /api/monsters              → data/monsters.json 전체 반환
├── GET  /api/patterns?id=<id>      → 특정 monster_id의 패턴 반환
├── GET  /api/videos?id=<id>        → 특정 monster_id의 영상 반환
│
├── GET  /api/comments?monster=<id> → 특정 몬스터 댓글 목록
├── POST /api/comments              → 댓글 추가 (monster_id, user_name, comment)
│
├── GET  /api/votes?monster=<id>    → 특정 몬스터 투표 현황
├── POST /api/votes                 → 투표 추가 (monster_id, user_name, vote_type)
│                                     중복 투표 방지 검증 포함
│
└── GET  /api/ranking               → 4개 카테고리 랭킹 집계 반환
```

## API 응답 형식

모든 API는 아래 형식을 사용한다:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

오류 시:
```json
{
  "success": false,
  "data": null,
  "error": "에러 메시지"
}
```

## 프론트엔드 구조

```
frontend/
├── index.html
│   - monsters 목록 테이블
│   - 필터: game, difficulty
│   - 검색: name 검색
│   - 각 행 클릭 → monster.html?id=<id> 이동
│
├── monster.html
│   - 몬스터 기본 정보 헤더
│   - 패턴 타임라인 (Chart.js 라인차트, x축=hp_percent)
│   - YouTube iframe 임베드
│   - 팀 투표 (fun / difficulty / design_reference)
│   - 댓글 목록 + 댓글 작성
│
├── ranking.html
│   - Most Difficult Boss (mechanic_complexity DESC)
│   - Most Fun Boss (fun_factor_score DESC)
│   - Most Unique Mechanic (pattern_type 다양성 DESC)
│   - Most Viewed Boss (view_count 합산 DESC)
│
├── dashboard.html
│   - boss_fun_distribution (Chart.js 바차트)
│   - pattern_type_distribution (Chart.js 파이차트)
│   - mechanic_complexity_chart (Chart.js 바차트)
│   - boss_ranking_chart (Chart.js 수평 바차트)
│
├── style.css          공통 스타일
└── script.js          공통 유틸 (fetchAPI, autoSync, 등)
```

## 자동 동기화

```javascript
// script.js
const AUTO_SYNC_INTERVAL = 60 * 60 * 1000; // 1시간
setInterval(() => {
  fetchAndRenderCurrentPage();
}, AUTO_SYNC_INTERVAL);
```

collector가 monsters.json을 갱신하면, 1시간 내 자동으로 UI에 반영된다.

## 랭킹 집계 로직 (서버사이드)

```python
# /api/ranking 에서 처리
most_difficult = sorted(monsters, key=lambda m: m['mechanic_complexity'], reverse=True)
most_fun       = sorted(monsters, key=lambda m: m['fun_factor_score'], reverse=True)
most_unique    = sorted(monsters, key=lambda m: len(set(p['pattern_type'] for p in patterns[m['id']])), reverse=True)
most_viewed    = sorted(monsters, key=lambda m: sum(v['view_count'] for v in videos[m['id']]), reverse=True)
```

## LAN 접속

```python
# app.py
app.run(host='0.0.0.0', port=5000, debug=False)
```

- 서버 실행자: `http://localhost:5000`
- 팀원 접속: `http://<서버PC IP>:5000`

## v2 예정 기능

- `pattern_similarity` 페이지: `pattern_similarity_index.json` 기반 유사 패턴 추천
  (data_collection_engine 확장 필요)
