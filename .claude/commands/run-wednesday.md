# HFK 수요일 루틴 에이전트

매주 수요일, 한 주간의 슬랙 활동 정리부터 핸드아웃 생성, 공지 예약, 시즌레터, 녹취 콘텐츠까지 순차 실행합니다.

## 사용법

```
/run-wednesday
```

## 실행 워크플로우

### Step 1: 슬랙 한 주간 리뷰 → 미팅 어젠더 정리

hbrforum 워크스페이스의 `idea-log`, `crew` 채널에서 지난 7일간의 메시지를 수집하고 미팅 어젠더를 정리합니다.

1. `$HOME/Seulki.log/.env`에서 `SLACK_BOT_TOKEN`을 로드합니다
2. `slack_sdk`로 채널 목록 조회 → `idea-log`, `crew` 채널 ID를 찾습니다
   - 채널명에 `idea-log` 또는 `crew`가 포함된 채널 모두 대상
3. 각 채널의 최근 7일간 메시지를 `conversations.history`로 수집합니다
   - `oldest` 파라미터: 7일 전 timestamp
   - 스레드 답글도 `conversations.replies`로 수집
4. 수집된 메시지를 분석하여 미팅 어젠더를 정리합니다:
   - 새로운 아이디어 / 제안
   - 논의가 필요한 사항
   - 결정된 사항 / 액션 아이템
   - 진행 중인 프로젝트 업데이트
5. 정리된 어젠더를 사용자에게 보여줍니다

```python
from slack_sdk import WebClient
from dotenv import load_dotenv
import os, time
from datetime import datetime, timedelta

load_dotenv("$HOME/Seulki.log/.env")
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# 7일 전 timestamp
oldest = str(int((datetime.now() - timedelta(days=7)).timestamp()))

# 채널 찾기
channels = client.conversations_list(types="public_channel", limit=1000)
target_channels = [ch for ch in channels['channels']
                   if 'idea-log' in ch['name'] or 'crew' in ch['name']]

# 메시지 수집
for ch in target_channels:
    client.conversations_join(channel=ch['id'])
    time.sleep(0.5)
    history = client.conversations_history(channel=ch['id'], oldest=oldest, limit=200)
    # 스레드 답글 수집
    for msg in history['messages']:
        if msg.get('thread_ts') and msg.get('reply_count', 0) > 0:
            replies = client.conversations_replies(channel=ch['id'], ts=msg['thread_ts'])
            time.sleep(0.5)
```

**사용자 확인**: 어젠더 내용이 맞는지 확인

### Step 2: 할일 → 미리알림 추가

Step 1에서 정리된 액션 아이템 중 할일이 있으면 미리알림에 추가합니다.

1. 어젠더에서 추출된 할일 목록을 사용자에게 보여줍니다
2. 사용자가 확인/수정한 항목을 MCP Apple Reminders `bulk_create`로 추가합니다
   - 리스트: "HFK"
   - 마감일: 사용자 지정 (기본: 다음 수요일 09:00)
3. 추가할 항목이 없으면 건너뜁니다

**사용자 확인**: 추가할 미리알림 내용과 마감일

### Step 3: 팀 포스팅 → 미리알림 추가

Step 1의 메시지에서 팀 포스팅(인스타, 블로그 등) 관련 언급을 찾아 미리알림에 추가합니다.

1. 포스팅 관련 키워드 탐색: 포스팅, 인스타, 블로그, 콘텐츠, 업로드, 게시, 발행
2. 발견된 포스팅 할일을 사용자에게 보여줍니다
3. 사용자가 확인한 항목을 MCP Apple Reminders `bulk_create`로 추가합니다
   - 리스트: "HFK"
   - 마감일: 사용자 지정
4. 추가할 항목이 없으면 건너뜁니다

**사용자 확인**: 포스팅 미리알림 내용

### Step 4: HFK 미리알림 → to-do-log 채널에 공유

HFK 미리알림 리스트의 미완료 항목을 슬랙 to-do-log 채널에 공유합니다.
단, **AI부사수, 필사, 에세이** 관련 미리알림은 제외합니다.

1. MCP Apple Reminders `list`로 "HFK" 리스트의 미완료 미리알림을 조회합니다
2. 제외 필터 적용:
   - 제목에 "AI부사수", "ai부사수" 포함 → 제외
   - 제목에 "필사" 포함 → 제외
   - 제목에 "에세이" 포함 → 제외
3. 필터링된 미리알림 목록을 사용자에게 보여줍니다
4. 사용자 확인 후, `slack_sdk`로 `to-do-log` 채널에 점리스트로 포스팅합니다

```python
# to-do-log 채널 찾기
channels = client.conversations_list(types="public_channel", limit=1000)
todo_ch = next((ch for ch in channels['channels'] if 'to-do-log' in ch['name']), None)

# 메시지 작성 (점리스트)
today = datetime.now().strftime("%Y. %m. %d")
lines = [f"*{today} 이번 주 할일*", ""]
for item in filtered_reminders:
    due = f" ({item['due']})" if item.get('due') else ""
    lines.append(f"• {item['title']}{due}")

client.conversations_join(channel=todo_ch['id'])
client.chat_postMessage(channel=todo_ch['id'], text="\n".join(lines))
```

**사용자 확인**: to-do-log에 공유할 내용

### Step 5: 핸드아웃 생성 → GitHub Pages 링크

`/generate-handout` 스킬을 실행합니다.

1. 이번 주 세션 날짜를 계산합니다:
   - 오늘(수요일) 이후 가장 가까운 세션 날짜
   - Product 노트를 확인하여 이번 주 또는 다음 주에 해당하는 날짜 확인
2. 사용자에게 세션 날짜를 확인합니다
3. `/generate-handout {날짜}` 실행
4. 완료 후 GitHub Pages 링크를 출력합니다:

```
핸드아웃 GitHub Pages:
  https://skaug12.github.io/session-guide/?team={팀명}&date={날짜}
```

**사용자 확인**: 세션 날짜, 공지 내용, 타임테이블 (generate-handout 내부에서 확인)

### Step 6: 슬랙 세션 공지 예약 (일요일 21:00)

`/schedule-notices` 스킬을 실행하여 해당 주의 일요일 오후 9시에 세션 공지를 예약합니다.

1. 날짜를 자동 계산합니다:
   - 시작일: Step 5에서 사용한 세션 날짜 기준으로 해당 주의 월요일
   - 종료일: 해당 주의 일요일
   - 예약발송일: 이번 주 일요일
   - 예약발송시간: 21:00
2. `/schedule-notices {시작일} {종료일} {예약발송일} 21:00` 실행
3. 테스트 DM → 사용자 확인 → 실제 예약

**사용자 확인**: schedule-notices 내부 워크플로우에서 확인

### Step 7: 시즌레터 생성

`/generate-letter` 스킬을 실행합니다.

1. 사용자에게 시즌레터를 작성할지 질문합니다:
   - "예" → 시즌, 레터번호, 제목을 입력받아 실행
   - "아니오" → Step 8로 이동
2. `/generate-letter {시즌} {레터번호} {제목}` 실행

**사용자 확인**: 시즌레터 작성 여부, 섹션 구성 등 (generate-letter 내부에서 확인)

### Step 8: 녹취 → 콘텐츠 초안 생성

`/draft-from-recording` 스킬을 실행합니다.

1. 사용자에게 녹취 콘텐츠를 만들지 질문합니다:
   - "예" → `/draft-from-recording` 실행
   - "아니오" → 종료
2. Downloads 폴더에서 녹취 파일을 찾거나 경로를 입력받습니다

**사용자 확인**: 녹취 파일 선택, 리뷰 유형 선택 (draft-from-recording 내부에서 확인)

## 워크플로우 다이어그램

```
[Step 1: 슬랙 리뷰 → 미팅 어젠더] ← slack_sdk (idea-log, crew)
      ↓ (사용자 확인)
[Step 2: 할일 → 미리알림 추가] ← Apple Reminders MCP
      ↓
[Step 3: 포스팅 → 미리알림 추가] ← Apple Reminders MCP
      ↓
[Step 4: 미리알림 → to-do-log 공유] ← Apple Reminders MCP → slack_sdk
      ↓ (사용자 확인)
[Step 5: 핸드아웃 생성] ← /generate-handout
      ↓ (사용자 확인)
[Step 6: 세션 공지 예약 (일요일 21:00)] ← /schedule-notices
      ↓ (사용자 확인)
[Step 7: 시즌레터?] ← /generate-letter (선택)
      ↓
[Step 8: 녹취 콘텐츠?] ← /draft-from-recording (선택)
      ↓
[완료 요약]
```

## 완료 요약

모든 단계 완료 후 실행 결과를 요약합니다:
- 미팅 어젠더 항목 수
- 추가된 미리알림 수 (Step 2 + Step 3)
- to-do-log에 공유된 항목 수
- 생성된 핸드아웃 (팀 수, GitHub Pages 링크)
- 예약된 Slack 공지 수
- 생성된 시즌레터 (있는 경우)
- 생성된 콘텐츠 초안 (있는 경우)

## 데이터 소스

| 정보 | 소스 | 토큰/인증 |
|------|------|-----------|
| 슬랙 메시지 | hbrforum 워크스페이스 | `$HOME/Seulki.log/.env` → `SLACK_BOT_TOKEN` |
| 미리알림 | Apple Reminders (iPhone) | MCP Apple Reminders |
| 세션 일정 | Product 노트 (Obsidian) | 파일 시스템 |
| 파트너/멤버 | Google Sheets | `$HOME/google_sheet_search/credentials.json` |
| 캘린더 이벤트 | Google Calendar | `$HOME/Seulki.log/.env` → `GOOGLE_API_KEY` |

## 참고

- Python venv: `$HOME/hfk-slack-venv/`
- 각 Step은 사용자 확인 후 다음으로 진행
- Step 7, 8은 선택 사항 (사용자가 "아니오" 시 건너뜀)
- Slack API rate limit 준수 (요청 간 0.5초 대기)
