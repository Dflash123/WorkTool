# Monster Skill Analyzer

게임 몬스터 스킬 타이밍·체감·밸런스를 기록·분석하는 기획자용 툴.

## 주요 기능

| 기능 | 설명 |
|------|------|
| 스킬 입력 | 선딜/판정/후딜/회피구간/가이드 이펙트 기록 |
| 테스트 로그 | 내부/라이브 테스트 이력 관리 |
| 체감 평가 | 리커트 1~5점 7개 항목 + 서술형 |
| 분석 대시보드 | 자동 지표 계산, 위험 패턴 탐지, 버전 비교 |
| Google Sheets | 팀 전체가 동일 데이터 공유 |

## 자동 계산 지표

- **반응 여유 지수** - 회피 가능 시간의 여유
- **타이밍 공정성 점수** - 종합 공정성
- **억까 가능성 지수** - 억울한 피격 위험도
- **설계 의도 적중률** - 기획 의도 달성률
- **학습 가능성 점수** - 패턴 학습 가능성

## 빠른 시작

```
1. Python 3.10+ 설치
2. pip install -r requirements.txt
3. credentials/ 에 service_account.json 배치
4. config.yaml 에 spreadsheet_id 입력
5. run.bat 더블클릭
```

자세한 설정: [docs/SETUP.md](docs/SETUP.md)

## 문서

- [아키텍처](docs/ARCHITECTURE.md)
- [DB 스키마](docs/DB_SCHEMA.md)
- [지표 계산 공식](docs/METRICS.md)
- [설치 가이드](docs/SETUP.md)
