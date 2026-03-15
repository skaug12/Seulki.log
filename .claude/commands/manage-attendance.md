# HFK 출석 관리

HFK 2026 봄시즌 출석 스프레드시트를 관리합니다.

## 사용법

```
/manage-attendance <명령> <인자>
```

### 명령어

| 명령 | 설명 | 예시 |
|------|------|------|
| 불참 | 특정 회차 불참자 기록 | `/manage-attendance 불참 소통의기술 2회차 이승원, 전소영` |
| 참석 | 특정 회차 전원 출석 또는 특정인 출석 | `/manage-attendance 참석 전략가의일 2회차` |
| 출석률 | 팀 또는 전체 출석률 조회 | `/manage-attendance 출석률` |
| 현황 | 특정 팀의 출석 현황 조회 | `/manage-attendance 현황 소통의기술` |

**자연어도 가능:**
```
/manage-attendance 소통의기술 2회차 이승원 전소영 불참
/manage-attendance 전략가의일 2회차 전원 출석
/manage-attendance AI핸즈온 1회차 김혜림만 불참
```

## 스프레드시트 정보

- **Spreadsheet ID**: `1Lqem8RwJmoXQp1xXbblAmJoRA_BWN56asR823g3CJyM`
- **출석 시트**: `26봄 출석`
- **일정 시트**: `26봄 일정`

## 시트 구조

출석 시트는 팀별 섹션으로 구성됩니다:

```
Row: 팀 헤더 (팀명 + 스케줄)
Row: 컬럼 헤더 (이름 | 회사 | 1회차 | 2회차 | ... | 6회차 | 출석률)
Row: 파트너
Row: 멤버1
Row: 멤버2
...
Row: 팀 평균 출석률
Row: (빈 행)
```

- 출석: `O`, 불참: `X`
- 1회차~6회차 → C~H열 (columnIndex 2~7)
- 출석률 → I열 (수식 자동 계산)

## 실행 절차

### 1단계: 인자 파싱

$ARGUMENTS에서 다음을 추출합니다:
- **명령**: 불참, 참석, 출석률, 현황
- **팀명**: HFK 팀 이름
- **회차**: 1~6회차 (숫자 추출)
- **이름 목록**: 쉼표 또는 공백으로 구분된 멤버 이름

자연어 입력도 지원합니다. 핵심 정보(팀명, 회차, 이름, 불참/참석)를 추출합니다.

### 2단계: 스프레드시트 연결

```python
import gspread
from google.oauth2.service_account import Credentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(
    '$HOME/google_sheet_search/credentials.json', scopes=scopes
)
gc = gspread.authorize(creds)
sh = gc.open_by_key('1Lqem8RwJmoXQp1xXbblAmJoRA_BWN56asR823g3CJyM')
ws = sh.worksheet('26봄 출석')
```

### 3단계: 명령별 처리

#### 불참 처리

1. 시트 전체 데이터를 `ws.get_all_values()`로 가져옵니다
2. 팀 헤더 행을 찾습니다 (A열에 팀명이 포함된 행)
3. 해당 팀의 멤버 행들을 순회합니다
4. 회차 번호로 열을 결정합니다 (1회차=C열=col 3, 2회차=D열=col 4, ...)
5. 불참자 이름에 해당하는 행에 `X`를 기록합니다
6. 나머지 멤버(해당 회차가 빈칸인 경우)에는 `O`를 기록합니다

```python
# 회차 → 열 매핑 (1-indexed for gspread)
session_col = session_number + 2  # 1회차=3, 2회차=4, ...

# 팀 섹션 찾기
all_data = ws.get_all_values()
team_header_row = None
for i, row in enumerate(all_data):
    if row[0] and team_name in row[0]:
        team_header_row = i
        break

# 멤버 행 범위: 팀 헤더 + 2 (컬럼헤더, 파트너 건너뜀) ~ 다음 빈 행 또는 통계 행
member_start = team_header_row + 3  # 파트너 다음 행
member_end = member_start
for i in range(member_start, len(all_data)):
    if all_data[i][0] == '팀 평균 출석률' or all_data[i][0] == '':
        member_end = i
        break

# 업데이트할 셀 목록
cells_to_update = []
for i in range(member_start, member_end):
    member_name = all_data[i][0]
    row_num = i + 1  # gspread 1-indexed
    if member_name in absent_names:
        cells_to_update.append(gspread.Cell(row_num, session_col, 'X'))
    else:
        # 빈칸이면 O로 채움
        if not all_data[i][session_col - 1]:
            cells_to_update.append(gspread.Cell(row_num, session_col, 'O'))

ws.update_cells(cells_to_update)
```

#### 참석 처리

- 특정 이름이 주어지면: 해당 멤버만 `O`
- 이름 없이 "전원 출석"이면: 해당 팀 모든 멤버에 `O`

#### 출석률 조회

1. 시트 전체 데이터를 가져옵니다
2. 각 팀의 "팀 평균 출석률" 행에서 I열 값을 읽습니다
3. 팀별 출석률을 표로 출력합니다

#### 현황 조회

1. 해당 팀의 멤버별 출석 데이터를 읽습니다
2. 멤버별 O/X 현황과 출석률을 표로 출력합니다

### 4단계: 결과 보고

처리 완료 후 변경 내역을 간결하게 보고합니다:

```
소통의기술 2회차 출석 반영 완료:
- 불참: 이승원, 전소영
- 출석: 송서현, 김다영, 서지희, 이홍진, 홍수경
```

## 이벤트 출석 관리

이벤트는 팀 세션과 별도로, 슬랙 `2--`로 시작하는 채널에서 관리됩니다.

### 이벤트 출석 명령어

| 명령 | 설명 | 예시 |
|------|------|------|
| 이벤트출석 | 슬랙에서 참석 예정자 자동 수집 + 불참자 X 처리 | `/manage-attendance 이벤트출석 북콘서트` |
| 이벤트현황 | 이벤트 참석 현황 조회 | `/manage-attendance 이벤트현황 북콘서트` |

**자연어도 가능:**
```
/manage-attendance 북콘서트 출석 처리
/manage-attendance 북콘서트 전소영 불참
```

### 이벤트 출석 처리 절차 (슬랙 API 연동)

#### 1단계: 이벤트 채널 찾기

`2--`로 시작하는 슬랙 채널 중 이벤트명이 포함된 채널을 찾습니다.

```python
import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# 2--로 시작하는 이벤트 채널 검색
result = client.conversations_list(types="public_channel", limit=200)
event_channels = [
    ch for ch in result['channels']
    if ch['name'].startswith('2--') and event_name in ch['name']
]
channel_id = event_channels[0]['id']
```

#### 2단계: 이벤트 공지 메시지의 스레드에서 참석 예정자 수집

공지 메시지의 스레드(댓글)에서 참석 예정자 목록을 가져옵니다.

```python
# 채널 참여 (필요 시)
client.conversations_join(channel=channel_id)

# 채널의 최근 메시지에서 공지 찾기
messages = client.conversations_history(channel=channel_id, limit=20)
# 공지 메시지 식별 (참석/출석/명단 등 키워드 포함된 메시지)
notice_msg = None
for msg in messages['messages']:
    if any(kw in msg.get('text', '') for kw in ['참석', '출석', '명단', '신청']):
        notice_msg = msg
        break

# 공지의 스레드 댓글에서 참석 예정자 목록 가져오기
replies = client.conversations_replies(
    channel=channel_id, ts=notice_msg['ts']
)
# 스레드 댓글에서 참석 예정자 이름 목록 파싱
# (댓글에 이름 목록이 텍스트로 작성되어 있음)
```

#### 3단계: 출석 기록

1. 참석 예정자 전원을 `O`로 기록
2. 불참으로 별도 입력된 사람은 `X`로 수정
3. 최종 `O` 인원수를 집계하여 참석자 수 산출

#### 4단계: 결과 보고

```
북콘서트 이벤트 출석 처리 완료:
- 참석 예정자: 12명
- 참석(O): 김지원, 이승원 외 8명 (10명)
- 불참(X): 전소영, 박수진 (2명)
```

## 팀 목록 (26봄)

감각적기획, 강점차별화, 경영의전설, 고급화전략, 리더십첫줄, 리더의서재, 마케팅디깅, 소통의기술, 저스트두잇, 전략가의일, 팀오호츠크, AI부사수, AI핸즈온

## 주의사항

- 이미 O 또는 X가 입력된 셀은 덮어쓰지 않습니다 (명시적으로 수정 요청 시에만 변경)
- 파트너 행은 출석 체크 대상이 아닙니다
- 회차 번호는 반드시 1~6 사이여야 합니다
- 멤버 이름이 시트에 없으면 경고를 출력합니다
