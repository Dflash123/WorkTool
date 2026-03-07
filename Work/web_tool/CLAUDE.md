# CLAUDE.md — web_tool 모듈

## !! DUAL CLAUDE CODE INSTANCE 경고 !!

**이 레포지토리에는 현재 Claude Code 인스턴스가 2개 동시에 실행 중이다.**

| 인스턴스 | 담당 모듈 | 소유 파일 |
|----------|----------|----------|
| Instance A (data_collection_engine) | `collector/`, `timeline_extractor/`, `scheduler/` | `data/monsters.json`, `data/patterns.json`, `data/videos.json`, `run_collector.py` |
| Instance B (web_tool) | `frontend/`, `app.py` | `data/comments.json`, `data/votes.json` |

### 절대 금지 사항

이 인스턴스(web_tool)는 아래 파일/폴더를 **절대 수정하지 않는다**:

```
collector/                    # Instance A 소유
timeline_extractor/           # Instance A 소유
scheduler/                    # Instance A 소유
run_collector.py              # Instance A 소유
data/monsters.json            # Instance A가 생성/관리
data/patterns.json            # Instance A가 생성/관리
data/videos.json              # Instance A가 생성/관리
../mmorpg-monster-reference/  # Instance A의 기획 레퍼런스 문서 (읽기 참고만 가능)
```

### 이 인스턴스의 소유 파일

```
frontend/               # 모든 HTML/CSS/JS
app.py                  # Flask API 서버
data/comments.json      # 댓글 데이터
data/votes.json         # 투표 데이터
```

---

## 프로젝트 개요

MMORPG 몬스터 패턴 분석 데이터를 시각화하고 팀 협업이 가능한 웹 기반 분석 툴.

- **Backend**: Python Flask
- **Frontend**: HTML + CSS + Vanilla JS
- **Chart**: Chart.js (CDN)
- **데이터**: JSON 파일 기반
- **협업 범위**: 로컬 네트워크 (LAN)

---

## 아키텍처

```
data_collection_engine (Instance A)
  └── collector/ + timeline_extractor/
        → data/monsters.json (읽기전용)
        → data/patterns.json (읽기전용)
        → data/videos.json   (읽기전용)

web_tool (Instance B = 이 인스턴스)
  └── app.py (Flask API)
        GET  /api/monsters
        GET  /api/patterns?id=
        GET  /api/videos?id=
        GET  /api/comments?monster=
        POST /api/comments
        GET  /api/votes?monster=
        POST /api/votes
        GET  /api/ranking
        → data/comments.json (읽기+쓰기)
        → data/votes.json    (읽기+쓰기)

  └── frontend/
        index.html     → 몬스터 DB 목록 + 필터
        monster.html   → 패턴 타임라인 + YouTube
        ranking.html   → 보스 랭킹 4종
        dashboard.html → 분석 차트 4종
        style.css
        script.js
```

---

## 페이지 구성

| 페이지 | 데이터 소스 | 주요 기능 |
|--------|------------|----------|
| `index.html` | monsters.json | 목록 테이블, 필터(game/difficulty), 검색 |
| `monster.html` | monsters + patterns + videos + comments + votes | HP% 타임라인, YouTube iframe, 댓글, 투표 |
| `ranking.html` | monsters + patterns + videos + votes | 4개 카테고리 랭킹 |
| `dashboard.html` | monsters + patterns | Chart.js 차트 4종 |

---

## 랭킹 로직

| 카테고리 | 소스 | 기준 |
|----------|------|------|
| Most Difficult Boss | monsters.json | `mechanic_complexity` DESC |
| Most Fun Boss | monsters.json | `fun_factor_score` 6개 항목 평균 DESC (null 제외) |
| Most Unique Mechanic | patterns.json | `distinct(pattern_type)` 개수 DESC |
| Most Viewed Boss | videos.json | `view_count` 합산 DESC (같은 monster_id 영상 합산) |

---

## 데이터 스키마 요약

```
monsters.json  (배열 루트)
  id, name, game, raid, monster_type, release_patch
  boss_fun_type[], design_reference_tags[]
  fun_factor_score { reaction, teamplay, mechanic_uniqueness, visual_spectacle, difficulty, punishment }
  mechanic_complexity, boss_ranking { difficulty_rank, fun_rank, composite_score }
  last_updated

patterns.json  (배열 루트)
  monster_id, source_video_id, extracted_at, last_updated
  timeline[hp_percent, pattern_name, pattern_type, difficulty,
           reaction_window_sec, failure_penalty, success_reward, notes]

videos.json  (배열 루트)
  youtube_id, monster_id, title, channel
  view_count, comment_count, duration_seconds
  upload_date, subtitle_available, analysis_status, collected_at

comments.json  (web_tool 소유, 객체 루트)
  comments[id, monster_id, user_name, comment, date]

votes.json  (web_tool 소유, 객체 루트)
  votes[id, monster_id, user_name, vote_type(fun|difficulty|design_reference), date]
```

상세 스키마: `docs/SCHEMA.md` 참고

---

## 자동 동기화

- 방식: 프론트엔드에서 1시간마다 `/api/monsters` 등 재호출
- 구현: `setInterval(fetchData, 3600000)` in `script.js`
- 목적: collector가 갱신한 monsters.json을 자동 반영

---

## 개발 규칙

1. `frontend/` 파일은 200-400줄 이내 유지
2. JS는 Vanilla JS만 사용 (라이브러리 추가 금지, Chart.js CDN 제외)
3. Flask API는 항상 `{"success": bool, "data": ..., "error": ...}` 형식 반환
4. 모든 POST 엔드포인트는 입력 검증 필수
5. `data/monsters.json`, `data/patterns.json`, `data/videos.json` 절대 수정 금지

---

## 실행 방법

```bash
cd web_tool
pip install flask
python app.py
# → http://localhost:5000
# → LAN 접속: http://<서버IP>:5000
```

---

## v1 범위 (현재 버전)

- [x] 몬스터 DB 뷰어 (index.html)
- [x] 패턴 타임라인 시각화 (monster.html)
- [x] YouTube 영상 임베드 (monster.html)
- [x] 댓글 시스템 (monster.html)
- [x] 팀 투표 시스템 (monster.html)
- [x] 보스 랭킹 (ranking.html)
- [x] 분석 대시보드 (dashboard.html)
- [ ] pattern_similarity → v2 (data_collection_engine 확장 필요)
