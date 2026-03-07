# collector

YouTube Data API v3를 통해 MMORPG 보스 전투 영상의 텍스트 데이터를 수집하는 모듈.

## 담당: Claude A (data_collection_engine)

## 파일 구성 (개발 예정)

| 파일 | 역할 |
|------|------|
| `youtube_searcher.py` | 키워드 검색, engagement 점수 기반 정렬 |
| `metadata_collector.py` | 영상 메타데이터 + description 수집 |
| `subtitle_collector.py` | 자막 수집 (없으면 None 반환) |
| `comment_sampler.py` | 좋아요 상위 20개 댓글 샘플링 |

## 수집 대상 게임

World of Warcraft, Final Fantasy XIV, Lost Ark, Black Desert Online,
Guild Wars 2, Elder Scrolls Online, Blade and Soul, TERA, Aion,
MapleStory, Lineage, New World, Albion Online, ArcheAge,
Ragnarok Online, Tree of Savior, Dragon Nest, Phantasy Star Online 2,
Tower of Fantasy, Blue Protocol
