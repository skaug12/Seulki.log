# HFK 세션 핸드아웃 생성

세션 날짜를 입력하면 해당 날짜에 진행되는 모든 팀 세션의 A4 핸드아웃 PDF를 생성하여 다운로드 폴더에 저장합니다.

## 사용법

```
/generate-handout <세션날짜>
```

예시:
```
/generate-handout 2026-03-14
```

## 실행 절차

$ARGUMENTS를 파싱하여 세션 핸드아웃을 생성합니다.

### 1단계: 세션 일정 조회 (Slack)

MCP Slack `search-messages` 도구로 해당 날짜에 진행되는 팀 세션을 검색합니다.

검색 쿼리 예시: `회차 {날짜}` 또는 `{날짜}` in HFK 슬랙
- 팀 채널(`1--팀명`)의 공지 메시지에서 추출
- 추출 정보: **시즌**, **팀 이름**, **회차**, **주제(세부 주제)**, **다음 회차 일정**, **장소**, **시간**

해당 날짜에 여러 팀이 세션을 진행할 수 있으므로, 모든 팀을 수집합니다.

### 2단계: 파트너 & 멤버 리스트 조회 (Google Sheets)

1단계에서 확인된 각 팀에 대해 **HFK사람들** 구글시트에서 파트너와 멤버를 조회합니다.

- Spreadsheet ID: `1EcMzh2s3pe_ejwZ9eXO1GLviOR8a0DNVNtpXm291Oxo`
- 현재 시즌 시트 탭 (예: `26봄`)
- 구조: HFK 팀 | 멤버십 | 이름 | 회사
- 팀명 행에서 파트너 정보, 이후 행에서 멤버 리스트 추출

```python
import gspread
from google.oauth2.service_account import Credentials

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('/Users/sklee/google_sheet_search/credentials.json', scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key('1EcMzh2s3pe_ejwZ9eXO1GLviOR8a0DNVNtpXm291Oxo')
ws = sh.worksheet('26봄')  # 시즌에 맞게 변경
```

### 3단계: 주요 공지 입력 받기

사용자에게 주요 공지 사항을 질문합니다:

```
이번 세션의 주요 공지 사항을 입력해주세요.
(여러 줄 가능, 빈 줄로 구분)
```

### 4단계: 타임테이블 확인

현재 기본 타임테이블을 보여주고 수정 여부를 질문합니다:

```
현재 타임테이블:
  10:30 – 10:40  스몰토크
  10:40 – 11:40  멤버 및 파트너 소개
  11:40 – 11:50  쉬는 시간
  11:50 – 12:50  파트너의 발표 진행
  12:50 – 13:00  4L 리뷰 작성

타임테이블을 수정하시겠습니까? (y/n)
```

### 5단계: 다가오는 이벤트 조회 (Google Calendar)

MCP Google Calendar `list-events` 도구로 입력 날짜부터 3주 후까지 `[이벤트]` 키워드로 검색합니다.

- 검색 범위: 세션 날짜 ~ 세션 날짜 + 21일
- 필터: 이벤트 제목에 `[이벤트]` 포함
- 추출: 날짜, 요일, 시간, 장소, 이벤트명

### 6단계: Quick Info 설정 (장소 기반)

장소에 따라 Wi-Fi 정보를 자동 설정합니다:

| 장소 | Wi-Fi ID | Wi-Fi PW |
|------|----------|----------|
| 오아시스 덕수궁 | 501_oasisdsg | oasis00000 |
| 소정동 | 301_sojungdong | sojungdong00000 |

화장실 정보:
- 오아시스 덕수궁: W 4F (비번없음) · M 5F (0000)
- 소정동: 3F (비번없음)

### 7단계: A4Guide.tsx 데이터 업데이트

수집된 정보로 `/Users/sklee/Projects/session-guide/src/app/components/A4Guide.tsx`의 데이터 섹션을 업데이트합니다.

업데이트 대상 (파일 상단 Data 영역):
- `timetable` — 타임테이블 배열
- `partner` — 파트너 이름, 소속
- `members` — 멤버 이름, 소속 배열
- `notices` — 주요 공지 배열
- `events` — 다가오는 이벤트 배열
- Title 영역: 시즌, 팀명, 날짜, 회차, 주제
- Quick info: Wi-Fi, 화장실 정보
- 다음 회차 안내 텍스트

**각 팀별로 별도의 데이터 세트를 생성합니다.**

### 8단계: 빌드 & PDF 생성

각 팀별로:
1. A4Guide.tsx 데이터를 해당 팀 정보로 업데이트
2. `npm run build` 실행 (single-file HTML 빌드)
3. Puppeteer/Playwright로 HTML → PDF 변환 (A4, 여백 없음)
4. PDF를 `~/Downloads/핸드아웃_{팀명}_{날짜}.pdf`로 저장

```bash
cd /Users/sklee/Projects/session-guide
npm run build
# dist/index.html → PDF 변환
```

PDF 변환 (Playwright 사용):
```bash
cd "$HFK_SKLEE"
venv/bin/python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///Users/sklee/Projects/session-guide/dist/index.html')
    page.pdf(path=output_path, width='794px', height='1123px', print_background=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
    browser.close()
"
```

### 9단계: 결과 보고

생성된 PDF 파일 목록을 출력합니다:

```
✓ 핸드아웃 생성 완료!

  ~/Downloads/핸드아웃_소통의기술_2026-03-14.pdf
  ~/Downloads/핸드아웃_넘버앤센스_2026-03-14.pdf
  ~/Downloads/핸드아웃_마케팅디깅_2026-03-14.pdf
```

---

## 데이터 소스 요약

| 정보 | 소스 | MCP |
|------|------|-----|
| 팀/세션/주제/회차 | Slack 팀 채널 공지 | Slack |
| 파트너/멤버 | HFK사람들 구글시트 | - (gspread) |
| 주요 공지 | 사용자 입력 | - |
| 타임테이블 | 기본값 + 사용자 수정 | - |
| 다가오는 이벤트 | 구글 캘린더 [이벤트] | Calendar |
| Wi-Fi/화장실 | 장소별 고정값 | - |

## 프로젝트 경로

- 소스: `/Users/sklee/Projects/session-guide/`
- 컴포넌트: `src/app/components/A4Guide.tsx`
- 빌드 출력: `dist/index.html`
- GitHub Pages: `https://skaug12.github.io/session-guide/`

## 주의사항

- A4Guide.tsx의 **데이터 영역만** 수정 (디자인/레이아웃 코드는 건드리지 않음)
- 여러 팀이 있으면 **순차적으로** 데이터 교체 → 빌드 → PDF 저장
- 빌드 후 원본 데이터로 복원하지 않음 (마지막 팀 데이터가 남음)
- Playwright가 없으면 `pip install playwright && playwright install chromium` 설치 안내

$ARGUMENTS
