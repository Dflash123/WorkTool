# Data Schema — web_tool

> Instance A(data_collection_engine)의 `mmorpg-monster-reference/docs/DATA_SCHEMA.md`를
> 기준으로 작성된 문서입니다. 스키마 변경 시 Instance A와 반드시 협의합니다.

## 파일 소유권 및 형식

| 파일 | 소유 | 루트 형식 | 권한 |
|------|------|----------|------|
| `data/monsters.json` | Instance A (collector) | 배열 `[]` | 읽기전용 |
| `data/patterns.json` | Instance A (timeline_extractor) | 배열 `[]` | 읽기전용 |
| `data/videos.json` | Instance A (collector) | 배열 `[]` | 읽기전용 |
| `data/comments.json` | Instance B (web_tool) | 객체 `{}` | 읽기+쓰기 |
| `data/votes.json` | Instance B (web_tool) | 객체 `{}` | 읽기+쓰기 |

---

## monsters.json

몬스터 기본 정보 + 평가 데이터. collector가 생성, 디자이너가 점수 수동 입력.

```json
[
  {
    "id": "wow_ragnaros",
    "name": "Ragnaros",
    "game": "World of Warcraft",
    "raid": "Molten Core",
    "monster_type": "Raid",
    "release_patch": "1.0",
    "boss_fun_type": ["Reaction Boss", "Spectacle Boss"],
    "design_reference_tags": ["cinematic_boss", "reaction_test"],
    "fun_factor_score": {
      "reaction": null,
      "teamplay": null,
      "mechanic_uniqueness": null,
      "visual_spectacle": null,
      "difficulty": null,
      "punishment": null
    },
    "mechanic_complexity": null,
    "boss_ranking": {
      "difficulty_rank": null,
      "fun_rank": null,
      "composite_score": null
    },
    "last_updated": "2026-03-07"
  }
]
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | `{game_short}_{boss_name_snake_case}` 고유 키 |
| `name` | string | 보스 이름 |
| `game` | string | 게임명 |
| `raid` | string | 레이드/던전명 |
| `monster_type` | string | `Raid` / `Dungeon` / `Field` / `Elite` |
| `release_patch` | string | 출시 패치 버전 |
| `boss_fun_type` | array | 재미 유형 태그 목록 |
| `design_reference_tags` | array | 디자인 레퍼런스 태그 목록 |
| `fun_factor_score` | object | 6개 항목 점수 (1-10, 디자이너 수동 입력, 미입력 시 null) |
| `fun_factor_score.reaction` | int\|null | 반응형 패턴 재미도 |
| `fun_factor_score.teamplay` | int\|null | 팀플레이 요소 |
| `fun_factor_score.mechanic_uniqueness` | int\|null | 메카닉 독창성 |
| `fun_factor_score.visual_spectacle` | int\|null | 시각적 연출 |
| `fun_factor_score.difficulty` | int\|null | 난이도 만족도 |
| `fun_factor_score.punishment` | int\|null | 실패 패널티 적절성 |
| `mechanic_complexity` | int\|null | LLM 자동 계산 (1-10) |
| `boss_ranking.composite_score` | float\|null | difficulty×0.4 + fun×0.4 + complexity×0.2 |
| `last_updated` | string | 마지막 업데이트 날짜 |

### web_tool 랭킹 사용 방식

- **Most Difficult Boss**: `mechanic_complexity` DESC
- **Most Fun Boss**: `fun_factor_score` 6개 항목의 non-null 평균 DESC

---

## patterns.json

보스 HP% 기반 패턴 타임라인. timeline_extractor가 LLM으로 추출하여 저장.

```json
[
  {
    "monster_id": "wow_ragnaros",
    "source_video_id": "youtube_abc123",
    "timeline": [
      {
        "hp_percent": 100,
        "pattern_name": "Opening Smash",
        "pattern_type": "AOE",
        "difficulty": "Medium",
        "reaction_window_sec": 2.0,
        "failure_penalty": "Heavy damage to raid",
        "success_reward": "Safe DPS window",
        "notes": ""
      },
      {
        "hp_percent": 75,
        "pattern_name": "Sons of Flame",
        "pattern_type": "Movement",
        "difficulty": "High",
        "reaction_window_sec": 3.5,
        "failure_penalty": "Wipe",
        "success_reward": "Phase progression",
        "notes": "킬 우선 대상"
      }
    ],
    "extracted_at": "2026-03-07",
    "last_updated": "2026-03-07"
  }
]
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `monster_id` | string | monsters.json의 id와 매칭 |
| `source_video_id` | string | videos.json의 youtube_id 참조 |
| `timeline[].hp_percent` | int 0-100 | 패턴 발동 시점 보스 체력 % |
| `timeline[].pattern_name` | string | 패턴 이름 |
| `timeline[].pattern_type` | string | `AOE` / `Target` / `Wipe` / `Puzzle` / `Movement` / `Mechanic` |
| `timeline[].difficulty` | string | `Low` / `Medium` / `High` |
| `timeline[].reaction_window_sec` | float | 반응 가능 시간 (초) |
| `timeline[].failure_penalty` | string | 실패 시 결과 |
| `timeline[].success_reward` | string | 성공 시 보상/결과 |
| `timeline[].notes` | string | 추가 메모 |
| `extracted_at` | string | LLM 추출 일시 |
| `last_updated` | string | 마지막 업데이트 날짜 |

### web_tool 타임라인 시각화

```
HP 100% ──[Opening Smash / AOE]──────────────────────
HP  75% ────────────────[Sons of Flame / Movement]───
HP   0% ──────────────────────────────────────────────
         x축: hp_percent 100→0
```

### web_tool 랭킹 사용 방식

- **Most Unique Mechanic**: `distinct(pattern_type)` 개수 DESC

---

## videos.json

YouTube 영상 메타데이터. collector가 YouTube API로 수집.

```json
[
  {
    "youtube_id": "abc123xyz",
    "monster_id": "wow_ragnaros",
    "title": "Ragnaros Boss Fight Full Guide - WoW",
    "channel": "WoW Guide Channel",
    "view_count": 500000,
    "comment_count": 1200,
    "duration_seconds": 623,
    "upload_date": "2023-05-15",
    "subtitle_available": true,
    "analysis_status": "completed",
    "collected_at": "2026-03-07"
  }
]
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `youtube_id` | string | YouTube 영상 ID (고유 키, iframe embed에 사용) |
| `monster_id` | string | monsters.json의 id와 매칭 |
| `title` | string | 영상 제목 |
| `channel` | string | 채널명 |
| `view_count` | int | 조회수 |
| `comment_count` | int | 댓글 수 |
| `duration_seconds` | int | 영상 길이 (초) |
| `upload_date` | string | 업로드 날짜 |
| `subtitle_available` | bool | 자막 존재 여부 |
| `analysis_status` | string | `pending` / `completed` / `skipped` |
| `collected_at` | string | 수집 일시 |

### web_tool 사용 방식

- YouTube iframe embed: `https://www.youtube.com/embed/{youtube_id}`
- **Most Viewed Boss**: 같은 `monster_id`의 `view_count` 합산 DESC

---

## comments.json

팀 댓글 DB. web_tool이 생성 및 관리.

```json
{
  "comments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "monster_id": "wow_ragnaros",
      "user_name": "기획자A",
      "comment": "Sons of Flame 패턴이 레퍼런스로 좋을 것 같음",
      "date": "2026-03-07T10:00:00"
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string UUID | 서버 자동 생성 |
| `monster_id` | string | 대상 몬스터 ID |
| `user_name` | string | 작성자 이름 |
| `comment` | string | 댓글 내용 |
| `date` | string ISO8601 | 작성 일시 |

---

## votes.json

팀 투표 DB. web_tool이 생성 및 관리.

```json
{
  "votes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "monster_id": "wow_ragnaros",
      "user_name": "기획자A",
      "vote_type": "design_reference",
      "date": "2026-03-07T10:00:00"
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string UUID | 서버 자동 생성 |
| `monster_id` | string | 대상 몬스터 ID |
| `user_name` | string | 투표자 이름 |
| `vote_type` | string | `fun` / `difficulty` / `design_reference` |
| `date` | string ISO8601 | 투표 일시 |

> 동일 `user_name` + `monster_id` + `vote_type` 조합 중복 투표 불가 (서버 검증).

---

## ID 명명 규칙 (Instance A 정의, 준수 필수)

```
monster_id 형식: {game_short}_{boss_name_snake_case}

예시:
  wow_ragnaros
  ffxiv_ultima_weapon
  lost_ark_valtan
  maplestory_lotus
```
