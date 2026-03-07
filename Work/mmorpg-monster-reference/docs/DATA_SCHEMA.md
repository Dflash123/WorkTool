# Data Schema — MMORPG Monster Reference System

## 파일 목록

| 파일 | 소유 | 설명 |
|------|------|------|
| `data/monsters.json` | Claude A | 몬스터 기본 정보 + 평가 데이터 |
| `data/patterns.json` | Claude A | HP% 기반 패턴 타임라인 |
| `data/videos.json` | Claude A | YouTube 영상 메타데이터 |
| `data/comments.json` | Claude B | 커뮤니티 댓글 (web_tool 담당) |
| `data/votes.json` | Claude B | 투표 데이터 (web_tool 담당) |

---

## monsters.json

몬스터 기본 정보와 평가 지표를 담는 배열.

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

### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | `{game_short}_{boss_name}` 형식, 고유 키 |
| `name` | string | 보스 이름 |
| `game` | string | 게임명 |
| `raid` | string | 레이드/던전명 |
| `monster_type` | string | Raid / Dungeon / Field / Elite |
| `release_patch` | string | 출시 패치 버전 |
| `boss_fun_type` | array | 재미 유형 태그 |
| `design_reference_tags` | array | 디자인 레퍼런스 태그 |
| `fun_factor_score` | object | 6개 항목 1-10 점수 (디자이너 수동 입력) |
| `mechanic_complexity` | int\|null | 1-10 자동 계산 (LLM) |
| `boss_ranking.composite_score` | float\|null | difficulty*0.4 + fun*0.4 + complexity*0.2 |
| `last_updated` | date | 마지막 업데이트 날짜 |

### fun_factor_score 입력 방식
- 디자이너가 수동으로 입력 후 저장
- 미입력 상태는 `null`로 유지
- 범위: 1-10 정수

### mechanic_complexity 계산 방식
- patterns.json에서 해당 보스 패턴 목록 로드
- 패턴 수 + 패턴 유형 다양성 분석
- Claude API에 보스 메카닉 복잡도 평가 요청 (1-10)
- 기준: 1-3(단순 AOE), 4-6(일반 레이드), 7-8(복합 메카닉), 9-10(퍼즐/협동)

---

## patterns.json

보스별 HP% 기반 패턴 타임라인 배열.

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

### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `monster_id` | string | monsters.json의 id와 매칭 |
| `source_video_id` | string | videos.json의 youtube_id 참조 |
| `timeline` | array | HP% 기반 패턴 목록 (내림차순 정렬) |
| `timeline[].hp_percent` | int | 패턴 발동 시점 보스 체력 % |
| `timeline[].pattern_type` | string | AOE / Target / Wipe / Puzzle / Movement |
| `timeline[].difficulty` | string | Low / Medium / High |
| `timeline[].reaction_window_sec` | float | 반응 가능 시간 (초) |

### 업데이트 규칙
- 동일 `monster_id` 존재 시: timeline 배열에 새 패턴 추가 (중복 방지)
- 새 보스: 새 레코드 추가
- 동일 `hp_percent` + `pattern_name` 조합은 중복으로 판단

---

## videos.json

YouTube 영상 메타데이터 및 수집 상태.

```json
[
  {
    "youtube_id": "abc123xyz",
    "monster_id": "wow_ragnaros",
    "title": "Ragnaros Boss Fight Full Guide - World of Warcraft",
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

### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `youtube_id` | string | YouTube 영상 ID (고유 키) |
| `monster_id` | string | monsters.json의 id와 매칭 |
| `view_count` | int | 조회수 (engagement 점수 기준) |
| `comment_count` | int | 댓글 수 (engagement 점수 기준) |
| `subtitle_available` | bool | 자막 존재 여부 |
| `analysis_status` | string | pending / completed / skipped |

### analysis_status 값
- `pending`: 수집했으나 LLM 분석 미완료
- `completed`: 패턴 타임라인 추출 완료
- `skipped`: description/comments 부족으로 분석 불가

---

## ID 규칙

### monster_id 형식
```
{game_short}_{boss_name_snake_case}
```
예시:
- `wow_ragnaros`
- `ffxiv_ultima_weapon`
- `lost_ark_valtan`
- `maplestory_lotus`
