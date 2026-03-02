# 설치 및 실행 가이드

## 빠른 시작

### 1. Python 설치
- Python 3.10 이상 필요
- https://python.org 에서 다운로드 (PATH 추가 체크 필수)

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. Google Sheets 설정

#### 3-1. Google Cloud 설정
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성
3. **API 및 서비스 → 라이브러리** → `Google Sheets API` 검색 → 사용 설정
4. `Google Drive API` 도 사용 설정
5. **사용자 인증 정보 → 서비스 계정 만들기**
6. 서비스 계정 생성 후 **키 → JSON 키 추가** → 다운로드

#### 3-2. 파일 배치
```
credentials/
└── service_account.json   ← 다운받은 파일을 여기에
```

#### 3-3. Google Spreadsheet 준비
1. Google Drive에서 새 스프레드시트 생성
2. URL에서 ID 복사:
   `https://docs.google.com/spreadsheets/d/[이 부분이 ID]/edit`
3. **공유** → 서비스 계정 이메일 추가 (편집자 권한)
   - 이메일은 service_account.json 안의 `client_email` 값

#### 3-4. config.yaml 설정
```yaml
google_sheets:
  credentials_file: "credentials/service_account.json"
  spreadsheet_id: "복사한-ID-여기에-붙여넣기"
```

### 4. 실행
```
run.bat 더블클릭
```
또는
```bash
streamlit run src/app.py
```

---

## 팀원 공유 방법

1. 팀원도 동일하게 Python + 패키지 설치
2. `credentials/service_account.json` 파일 공유 (보안 채널 이용)
3. 같은 `config.yaml`의 `spreadsheet_id` 사용
4. 모두 같은 Google Spreadsheet에 접근

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| Spreadsheet ID 오류 | config.yaml의 spreadsheet_id 확인 |
| 인증 파일 없음 | credentials/ 폴더에 JSON 파일 확인 |
| 권한 오류 | 스프레드시트 공유 설정에서 서비스 계정 이메일 추가 |
| 모듈 없음 | `pip install -r requirements.txt` 재실행 |

---

## 업데이트 시

코드만 교체하면 됩니다. 데이터는 Google Sheets에 안전하게 보관됩니다.
