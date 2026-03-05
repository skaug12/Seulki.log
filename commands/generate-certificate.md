# HFK 수강확인증 생성

수강생 정보를 입력받아 Google Sheets 수강확인증 템플릿을 수정하고 PDF로 다운로드합니다.
아임웹 상품 상세페이지에서 수강 내용(회차별 세션 정보)을 자동으로 가져옵니다.

## 사용법

```
/generate-certificate [수강생명] [과정명]
```

예시:
```
/generate-certificate 황성빈 AI부사수
```

## 실행

$ARGUMENTS를 파싱하여 수강확인증을 생성합니다.

### 1단계: 사용자 입력

인자가 부족하면 AskUserQuestion으로 아래 정보를 입력받습니다:

- **수강생명**: 수강생 이름
- **과정명**: 아임웹 상품명과 매칭되는 과정명 (예: AI부사수)
- **기간**: 수강 기간 (예: "2025. 9. ~ 2025. 11.")
- **발급일**: 수강확인증 발급일 (예: "2025. 12. 5.")

### 2단계: 아임웹 상품 검색 & 수강 내용 자동 생성

MCP Imweb 도구로 과정 상세 정보를 가져옵니다:

1. `imweb_get_products`로 과정명에 해당하는 상품을 검색합니다
2. `imweb_get_product`로 상세 정보(content HTML)를 가져옵니다
3. content HTML에서 회차별 세션 정보를 파싱합니다:
   - 회차 번호, 날짜, 세션 주제, 설명을 추출
   - HTML 패턴: `<strong style="color:#980000;">N회차</strong>` + `<strong>날짜</strong>` + `<strong>주제</strong><br>설명`
4. 상품 가격 정보도 함께 가져옵니다

#### 수강 내용 텍스트 형식

파싱한 세션 정보를 아래 형식으로 변환합니다:

```
1회차. 3월 13일 (금) 자기 소개
자기 소개와 함께 멤버들의 AI 활용 사례를 공유합니다.

2회차. 3월 27일 (금) 데이터 분석
Claude Code로 예제 데이터를 분석하고 인사이트를 도출합니다.

...
```

#### 출석률 계산

- 총 회차 수는 파싱된 세션 수로 결정합니다
- 기본값: 100% (총 N회 중 N회 출석)
- 사용자가 별도 지정 가능

### 3단계: 사용자 확인

수정될 내용을 테이블 형태로 사용자에게 보여주고 확인을 받습니다:

| 필드 | 값 |
|------|-----|
| 과정명 | (입력값) |
| 수강생 | (입력값) |
| 기간 | (입력값) |
| 수강료 | (아임웹에서 가져온 가격) |
| 출석률 | 100% (총 N회 중 N회 출석) |
| 수강 내용 | (파싱된 회차별 내용 미리보기) |
| 발급일 | (입력값) |

### 4단계: Google Sheets 수정

Python 스크립트로 Google Sheets를 수정합니다:

```python
import gspread
from google.oauth2.service_account import Credentials

scopes = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(
    '/Users/sklee/google_sheet_search/credentials.json', scopes=scopes
)
gc = gspread.authorize(creds)

SPREADSHEET_ID = '1i2OHkPy3G1UR3GO-mANSjQ2EKtJ1eeZPkjvVQXVIB4c'
SHEET_GID = 648764598

sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.get_worksheet_by_id(SHEET_GID)

# 셀 업데이트
ws.update('E6', 과정명)
ws.update('C7', 수강생명)
ws.update('E7', 기간)
ws.update('C8', 수강료)      # 예: "₩590,000"
ws.update('C9', 수강_내용)   # 회차별 텍스트
ws.update('B12', 발급일)
```

#### 셀 매핑

| 셀 | 필드 | 예시 |
|-----|------|------|
| E6 | 과정명 | AI부사수 |
| C7 | 수강생 | 황성빈 |
| E7 | 기간 | 2025. 9. ~ 2025. 11. |
| C8 | 수강료 | ₩590,000 |
| C9 | 수강 내용 | (회차별 텍스트) |
| B12 | 발급일 | 2025. 12. 5. |

### 5단계: PDF 다운로드

Google Sheets의 PDF export URL로 다운로드합니다:

```bash
curl -L "https://docs.google.com/spreadsheets/d/1i2OHkPy3G1UR3GO-mANSjQ2EKtJ1eeZPkjvVQXVIB4c/export?format=pdf&gid=648764598&size=A4&portrait=true&gridlines=false&printtitle=false&sheetnames=false&pagenum=UNDEFINED&fzr=false" \
  -o ~/Downloads/수강확인증_{수강생명}.pdf
```

다운로드 완료 후 파일 경로를 사용자에게 알려줍니다.

---

## 상수

- **스프레드시트 ID**: `1i2OHkPy3G1UR3GO-mANSjQ2EKtJ1eeZPkjvVQXVIB4c`
- **시트 GID**: `648764598`
- **서비스 계정 키**: `/Users/sklee/google_sheet_search/credentials.json`
- **기관명**: HFK (고정)
- **공급자**: 위어드벤처 (WeAdventure) (고정)

---

## 주의사항

- 스프레드시트 수정 전 반드시 사용자 확인을 받을 것
- 아임웹에서 상품을 찾지 못할 경우 사용자에게 수강 내용을 직접 입력받을 것
- PDF 다운로드는 스프레드시트가 공개 설정되어 있어야 동작함
- 수강료는 아임웹 상품 가격을 기본으로 하되, 사용자가 수정 가능
