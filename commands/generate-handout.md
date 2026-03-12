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

`slack_sdk`의 `conversations.history`로 해당 날짜에 진행되는 팀 세션을 검색합니다.

- Bot Token: `$HFK_VAULT/.env`의 `SLACK_BOT_TOKEN` (`xoxb-...`)
- 팀 채널(`1--팀명`) 목록을 `conversations.list`로 조회
- 각 채널의 최근 메시지에서 해당 날짜 세션 공지를 탐색
- 추출 정보: **시즌**, **팀 이름**, **회차**, **주제(세부 주제)**, **다음 회차 일정**, **장소**, **시간**

**참고**: `search.messages` API는 Bot Token에서 사용 불가 (`not_allowed_token_type`). 반드시 `conversations.history`를 사용합니다.

해당 날짜에 여러 팀이 세션을 진행할 수 있으므로, 모든 팀을 수집합니다.

```python
# Python venv 경로: /Users/sklee/hfk-slack-venv/
# Bot Token은 $HFK_VAULT/.env 파일에서 로드
from slack_sdk import WebClient
import os
# .env 로드 후
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# 채널 목록 조회
channels = client.conversations_list(types="public_channel", limit=1000)
team_channels = [ch for ch in channels['channels'] if ch['name'].startswith('1--')]

# 각 채널 히스토리 검색
for ch in team_channels:
    history = client.conversations_history(channel=ch['id'], limit=20)
    # 메시지에서 날짜 매칭
```

### 2단계: 파트너 & 멤버 리스트 조회 (Google Sheets)

1단계에서 확인된 각 팀에 대해 **HFK사람들** 구글시트에서 파트너와 멤버를 조회합니다.

- Spreadsheet ID: `1EcMzh2s3pe_ejwZ9eXO1GLviOR8a0DNVNtpXm291Oxo`
- 현재 시즌 시트 탭 (예: `26봄`)
- 구조: HFK 팀 | 멤버십 | 이름 | 회사
- A열: 팀명(숫자로 시작하면 인원수이므로 무시), B열: '파트너'/'첫등록'/'재등록'
- 팀명 행에서 파트너 정보, 이후 행('첫등록'/'재등록')에서 멤버 리스트 추출

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

### 5단계: 다가오는 이벤트 조회 (Google Calendar API)

`fetch_calendar.py` 스크립트로 입력 날짜부터 3주 후까지의 캘린더 이벤트를 조회합니다.

- 스크립트 경로: `$HFK_VAULT/scripts/fetch_calendar.py`
- API Key: `$HFK_VAULT/.env`의 `GOOGLE_API_KEY`
- Calendar ID: `$HFK_VAULT/.env`의 `HFK_CALENDAR_ID`
- 필터: 이벤트 제목에 `[이벤트]` 포함하는 항목만 추출
- 추출: 날짜, 요일, 시간, 장소, 이벤트명

```bash
cd "$HFK_VAULT"
/Users/sklee/hfk-slack-venv/bin/python scripts/fetch_calendar.py --weeks 3 --json
```

또는 Python에서 직접 호출:
```python
import sys
sys.path.insert(0, '$HFK_VAULT/scripts')
from fetch_calendar import fetch_calendar_events, parse_event
from datetime import datetime, timedelta

start = datetime(2026, 3, 12)
end = start + timedelta(weeks=3)
raw_events = fetch_calendar_events(start, end)
events = [parse_event(e) for e in raw_events]
# [이벤트] 필터링
events = [e for e in events if '[이벤트]' in e['title']]
```

### 6단계: Quick Info 설정 (장소 기반)

장소에 따라 Wi-Fi 정보를 자동 설정합니다:

| 장소 | Wi-Fi ID | Wi-Fi PW |
|------|----------|----------|
| 오아시스 덕수궁 | 501_oasisdsg | oasis00000 |
| 소정동 | 301_sojungdong | sojungdong00000 |

화장실 정보:
- 오아시스 덕수궁: W 4F (비번없음) · M 5F (0000)
- 소정동: W 4F (비번없음) · M 5F (0000)

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
3. Playwright로 HTML → PDF 변환 (A4, 여백 없음)
4. PDF를 `~/Downloads/세션세션핸드아웃_{팀명}_{날짜}.pdf`로 저장

```bash
cd /Users/sklee/Projects/session-guide
npm run build
# dist/index.html → PDF 변환
```

PDF 변환 (Playwright 사용):
```python
# Python venv: /Users/sklee/hfk-slack-venv/bin/python
from playwright.sync_api import sync_playwright
output_path = f'/Users/sklee/Downloads/세션핸드아웃_{팀명}_{날짜}.pdf'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///Users/sklee/Projects/session-guide/dist/index.html')
    page.wait_for_load_state('networkidle')
    page.pdf(path=output_path, width='794px', height='1123px', print_background=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
    browser.close()
```

### 9단계: 결과 보고

생성된 PDF 파일 목록을 출력합니다:

```
핸드아웃 생성 완료!

  ~/Downloads/세션핸드아웃_소통의기술_2026-03-14.pdf
  ~/Downloads/세션핸드아웃_넘버앤센스_2026-03-14.pdf
```

---

## 데이터 소스 요약

| 정보 | 소스 | 방법 |
|------|------|------|
| 팀/세션/주제/회차 | Slack 팀 채널 공지 | `slack_sdk` → `conversations.history` (Bot Token) |
| 파트너/멤버 | HFK사람들 구글시트 | `gspread` + Service Account |
| 주요 공지 | 사용자 입력 | — |
| 타임테이블 | 기본값 + 사용자 수정 | — |
| 다가오는 이벤트 | 구글 캘린더 | `fetch_calendar.py` (Google Calendar API Key) |
| Wi-Fi/화장실 | 장소별 고정값 | — |

## 경로 요약

| 항목 | 경로 |
|------|------|
| Python venv | `/Users/sklee/hfk-slack-venv/` |
| Google 인증 | `/Users/sklee/google_sheet_search/credentials.json` |
| 캘린더 스크립트 | `$HFK_VAULT/scripts/fetch_calendar.py` |
| 캘린더 .env | `$HFK_VAULT/.env` (API_KEY, CALENDAR_ID) |
| 소스 프로젝트 | `/Users/sklee/Projects/session-guide/` |
| 컴포넌트 | `src/app/components/A4Guide.tsx` |
| 빌드 출력 | `dist/index.html` |
| GitHub Pages | `https://skaug12.github.io/session-guide/` |

## 주의사항

- A4Guide.tsx의 **데이터 영역만** 수정 (디자인/레이아웃 코드는 건드리지 않음)
- 여러 팀이 있으면 **순차적으로** 데이터 교체 → 빌드 → PDF 저장
- 빌드 후 원본 데이터로 복원하지 않음 (마지막 팀 데이터가 남음)
- Slack `search.messages`는 Bot Token 불가 → `conversations.history` 사용
- Playwright 미설치 시: `pip install playwright && playwright install chromium`

$ARGUMENTS
