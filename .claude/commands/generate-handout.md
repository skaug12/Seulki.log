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
# Python venv 경로: $HOME/hfk-slack-venv/
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
creds = Credentials.from_service_account_file('$HOME/google_sheet_search/credentials.json', scopes=scopes)
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
$HOME/hfk-slack-venv/bin/python scripts/fetch_calendar.py --weeks 3 --json
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

### 7단계: JSON 데이터 저장 (웹 배포용)

수집된 정보를 `HandoutData` 형식의 JSON으로 저장합니다. 이 데이터는 GitHub Pages에서 핸드아웃을 렌더링하는 데 사용됩니다.

각 팀별로 JSON 파일을 생성합니다:
- 경로: `$HOME/Projects/session-guide/public/data/handouts/{팀명}_{날짜}.json`
- 형식:

```json
{
  "season": "2026 봄시즌",
  "team": "소통의기술",
  "date": "2026. 03. 14 토요일",
  "sessionNumber": "01",
  "topic": "정보-전달 시각화 1",
  "nextSession": "다음 <strong>2회차</strong>는 <strong>3월 28일 (토) 10:30</strong> 오아시스 덕수궁입니다.",
  "venue": "오아시스 덕수궁",
  "timetable": [
    { "time": "10:30 – 10:40", "label": "스몰토크", "main": false },
    { "time": "10:40 – 11:40", "label": "멤버 및 파트너 소개", "main": true },
    { "time": "11:40 – 11:50", "label": "쉬는 시간", "main": false },
    { "time": "11:50 – 12:50", "label": "파트너의 발표 진행", "main": true },
    { "time": "12:50 – 13:00", "label": "4L 리뷰 작성", "main": false }
  ],
  "partner": { "name": "파트너명", "org": "소속" },
  "members": [
    { "name": "멤버명", "org": "소속" }
  ],
  "notices": ["공지 1", "공지 2"],
  "events": [
    { "day": "03.18", "dow": "수", "time": "19:30–21:00", "venue": "오아시스 덕수궁", "title": "이벤트명" }
  ],
  "wifi": { "id": "501_oasisdsg", "pw": "oasis00000" },
  "restroom": "W 4F (비번없음) · M 5F (0000)"
}
```

그리고 `$HOME/Projects/session-guide/public/data/index.json`에 새 핸드아웃 엔트리를 추가합니다:

```json
{
  "handouts": [
    {
      "team": "소통의기술",
      "date": "2026-03-14",
      "sessionNumber": "01",
      "topic": "정보-전달 시각화 1",
      "file": "소통의기술_2026-03-14.json"
    }
  ]
}
```

**기존 index.json을 읽어서 중복 없이 추가합니다** (같은 team+date가 있으면 덮어쓰기).

### 8단계: A4Guide.tsx 데이터 업데이트 & PDF 생성

수집된 정보로 `$HOME/Projects/session-guide/src/app/components/A4Guide.tsx`의 `defaultData` 객체를 업데이트합니다.

업데이트 대상:
- `defaultData` 객체의 모든 필드 (season, team, date, sessionNumber, topic, nextSession, venue, timetable, partner, members, notices, events, wifi, restroom)

**각 팀별로 순차적으로:**
1. `defaultData` 객체를 해당 팀 정보로 업데이트
2. `npm run build` 실행 (single-file HTML 빌드)
3. Playwright로 HTML → PDF 변환 (A4, 여백 없음)
4. PDF를 `~/Downloads/세션핸드아웃_{팀명}_{날짜}.pdf`로 저장

```bash
cd $HOME/Projects/session-guide
npm run build
# dist/index.html → PDF 변환
```

PDF 변환 (Playwright 사용):
```python
# Python venv: $HOME/hfk-slack-venv/bin/python
from playwright.sync_api import sync_playwright
output_path = f'$HOME/Downloads/세션핸드아웃_{팀명}_{날짜}.pdf'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file://$HOME/Projects/session-guide/dist/index.html')
    page.wait_for_load_state('networkidle')
    page.pdf(path=output_path, width='794px', height='1123px', print_background=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
    browser.close()
```

### 9단계: 웹 빌드 & GitHub Pages 배포

모든 팀의 PDF 생성이 완료된 후, GitHub Pages에 배포합니다:

```bash
cd $HOME/Projects/session-guide
bash scripts/deploy-web.sh
```

이 스크립트는:
1. `npm run build:web` → `dist-web/`에 웹 빌드 생성 (singlefile 없이)
2. `dist-web/`을 `gh-pages` 브랜치에 force push
3. GitHub Pages URL: `https://skaug12.github.io/session-guide/`

배포 후 핸드아웃 URL 형식:
- 인덱스: `https://skaug12.github.io/session-guide/`
- 개별 핸드아웃: `https://skaug12.github.io/session-guide/?team=소통의기술&date=2026-03-14`

### 10단계: 결과 보고

생성된 PDF 파일 목록과 웹 URL을 출력합니다:

```
핸드아웃 생성 완료!

📄 PDF:
  ~/Downloads/세션핸드아웃_소통의기술_2026-03-14.pdf
  ~/Downloads/세션핸드아웃_넘버앤센스_2026-03-14.pdf

🌐 웹 (GitHub Pages):
  https://skaug12.github.io/session-guide/?team=소통의기술&date=2026-03-14
  https://skaug12.github.io/session-guide/?team=넘버앤센스&date=2026-03-14
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
| Python venv | `$HOME/hfk-slack-venv/` |
| Google 인증 | `$HOME/google_sheet_search/credentials.json` |
| 캘린더 스크립트 | `$HFK_VAULT/scripts/fetch_calendar.py` |
| 캘린더 .env | `$HFK_VAULT/.env` (API_KEY, CALENDAR_ID) |
| 소스 프로젝트 | `$HOME/Projects/session-guide/` |
| 컴포넌트 | `src/app/components/A4Guide.tsx` |
| PDF 빌드 출력 | `dist/index.html` |
| 웹 빌드 출력 | `dist-web/` |
| 핸드아웃 데이터 | `public/data/handouts/{팀명}_{날짜}.json` |
| 핸드아웃 인덱스 | `public/data/index.json` |
| 배포 스크립트 | `scripts/deploy-web.sh` |
| GitHub Pages | `https://skaug12.github.io/session-guide/` |

## 주의사항

- A4Guide.tsx의 **`defaultData` 객체만** 수정 (디자인/레이아웃 코드는 건드리지 않음)
- 여러 팀이 있으면 **순차적으로** 데이터 교체 → 빌드 → PDF 저장
- 빌드 후 원본 데이터로 복원하지 않음 (마지막 팀 데이터가 남음)
- **JSON 데이터 저장은 PDF 생성 전에 수행** (7단계 → 8단계 순서)
- **웹 배포는 모든 PDF 생성 후 1회만 수행** (9단계)
- Slack `search.messages`는 Bot Token 불가 → `conversations.history` 사용
- Playwright 미설치 시: `pip install playwright && playwright install chromium`

$ARGUMENTS
