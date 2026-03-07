# timeline_extractor

수집된 텍스트 데이터를 Claude API로 분석하여 HP% 기반 패턴 타임라인을 추출하고
JSON DB에 저장하는 모듈.

## 담당: Claude A (data_collection_engine)

## 파일 구성 (개발 예정)

| 파일 | 역할 |
|------|------|
| `llm_extractor.py` | Claude API 호출, 프롬프트 관리 |
| `pattern_parser.py` | LLM 응답 → 구조화된 dict 변환 |
| `complexity_scorer.py` | mechanic_complexity 1-10 자동 계산 |
| `db_writer.py` | monsters.json, patterns.json, videos.json upsert 저장 |

## LLM 설정

- 기본 모델: claude-3-5-sonnet-20241022
- Fallback: gpt-4o
- 환경변수: CLAUDE_API_KEY, OPENAI_API_KEY
