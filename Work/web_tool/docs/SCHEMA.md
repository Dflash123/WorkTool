# Data Schema — web_tool

## 파일 소유권

| 파일 | 소유 모듈 | 권한 |
|------|----------|------|
| `data/monsters.json` | data_collection_engine (collector) | 읽기전용 |
| `data/patterns.json` | data_collection_engine (timeline_extractor) | 읽기전용 |
| `data/videos.json` | data_collection_engine (collector) | 읽기전용 |
| `data/comments.json` | web_tool | 읽기+쓰기 |
| `data/votes.json` | web_tool | 읽기+쓰기 |

---

## monsters.json

몬스터 기본 정보 DB. collector 모듈이 생성/갱신한다.

```json
{
  "monsters": [
    {
      "id": "lostark_brelshaza",
      "name": "Brelshaza",
      "game": "Lost Ark",
      "raid": "Phantom Legion Commander",
      "difficulty": "raid",
      "fun_factor_score": 9,
      "mechanic_complexity": 9
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| id | string | 고유 ID (game_name 형식) |
| name | string | 몬스터 이름 |
| game | string | 게임명 |
| raid | string | 레이드/던전 이름 |
| difficulty | string | `normal` / `hard` / `raid` / `ultimate` |
| fun_factor_score | number 1-10 | 재미 점수 |
| mechanic_complexity | number 1-10 | 메카닉 복잡도 |

---

## patterns.json

보스 체력 기반 패턴 타임라인 DB. timeline_extractor 모듈이 생성/갱신한다.

```json
{
  "patterns": [
    {
      "monster_id": "lostark_brelshaza",
      "timeline": [
        {
          "hp_percent": 100,
          "pattern_name": "Opening Laser",
          "pattern_type": "aoe",
          "description": "보스가 전방으로 광역 레이저 공격"
        },
        {
          "hp_percent": 60,
          "pattern_name": "Dimension Shift",
          "pattern_type": "phase_transition",
          "description": "페이즈 전환 패턴"
        }
      ]
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| monster_id | string | monsters.json의 id와 매핑 |
| timeline[].hp_percent | number 0-100 | 패턴 발생 체력 % |
| timeline[].pattern_name | string | 패턴 이름 |
| timeline[].pattern_type | string | `aoe` / `puzzle` / `phase_transition` / `enrage` / `mechanic` 등 |
| timeline[].description | string | 패턴 설명 |

**타임라인 시각화**: x축 = hp_percent (100→0), 각 패턴은 해당 HP% 위치에 마커로 표시

---

## videos.json

YouTube 영상 연결 DB. collector 모듈이 생성/갱신한다.

```json
{
  "videos": [
    {
      "monster_id": "lostark_brelshaza",
      "title": "Lost Ark Brelshaza Gate 6 Clear",
      "youtube_id": "dQw4w9WgXcQ",
      "duration_seconds": 1200,
      "view_count": 150000
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| monster_id | string | monsters.json의 id와 매핑 |
| title | string | 영상 제목 |
| youtube_id | string | YouTube 영상 ID (URL의 `?v=` 값) |
| duration_seconds | number | 영상 길이 (초) |
| view_count | number | 조회수 (collector가 주기적으로 갱신) |

> `view_count`는 Most Viewed Boss 랭킹에 사용된다.
> 동일 monster_id의 영상이 여러 개일 경우 view_count 합산으로 랭킹 계산.

---

## comments.json

팀 댓글 DB. web_tool이 관리한다.

```json
{
  "comments": [
    {
      "id": "uuid",
      "monster_id": "lostark_brelshaza",
      "user_name": "기획자A",
      "comment": "3페이즈 메테오 패턴이 레퍼런스로 좋을 것 같음",
      "date": "2026-03-07T10:00:00"
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| id | string UUID | 고유 ID (서버에서 자동 생성) |
| monster_id | string | 대상 몬스터 ID |
| user_name | string | 작성자 이름 (팀원 식별) |
| comment | string | 댓글 내용 |
| date | string ISO8601 | 작성 일시 |

---

## votes.json

팀 투표 DB. web_tool이 관리한다.

```json
{
  "votes": [
    {
      "id": "uuid",
      "monster_id": "lostark_brelshaza",
      "user_name": "기획자A",
      "vote_type": "design_reference",
      "date": "2026-03-07T10:00:00"
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| id | string UUID | 고유 ID (서버에서 자동 생성) |
| monster_id | string | 대상 몬스터 ID |
| user_name | string | 투표자 이름 |
| vote_type | string | `fun` / `difficulty` / `design_reference` |
| date | string ISO8601 | 투표 일시 |

> 동일 user_name + monster_id + vote_type 조합은 중복 투표 불가 (서버에서 검증).
