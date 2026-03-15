# 슬랙 공지 예약 발송

입력받은 기간에 세션이 있는 팀을 찾아 슬랙 채널별 공지 메시지를 생성하고, 테스트 확인 후 예약 발송합니다.

## 인자 형식

```
/schedule-notices <시작일> <종료일> <예약발송일> <예약발송시간>
```

예시:
```
/schedule-notices 2026-02-16 2026-02-22 2026-02-09 21:00
```

- 시작일/종료일: 세션 일정 검색 범위 (YYYY-MM-DD)
- 예약발송일/시간: 슬랙 메시지가 실제 발송되는 시각 (KST)

## 실행 절차

### 1단계: 캘린더 일정 조회 + 팀 매칭

MCP Google Calendar `list-events` 도구로 시작일~종료일 기간의 HFK 캘린더 이벤트를 조회합니다.

조회된 이벤트에서 `[팀]` 접두사가 있는 일정을 추출하고 팀별로 그룹핑합니다.

**일정/장소**: 캘린더가 정본입니다.
- 장소: 이벤트 제목/장소에서 판단 (기본: 5층 오아시스 덕수궁, 일부 팀: 3층 소정동)

**세션 주제/부제**: 해당 팀의 Obsidian 상품 노트(`product/26봄주중/*.md` 또는 `product/26봄주말/*.md`)의 "## 3개월 세션 주제" 섹션에서 확인합니다.

### 2단계: 메시지 작성 규칙

#### 포맷: Block Kit `rich_text` 사용 (필수)

plain text로 보내면 글머리 기호가 제대로 렌더링되지 않습니다.
반드시 `chat.scheduleMessage`의 `blocks` 파라미터에 `rich_text` 블록을 사용합니다.

**Block Kit 구조:**
- 제목: `rich_text_section` + `{"type": "text", "style": {"bold": true}}` + `{"type": "broadcast", "range": "channel"}`
- 부제: `rich_text_quote`
- 리스트: `rich_text_list` (`"style": "bullet"`) → 슬랙 네이티브 글머리 기호 목록으로 렌더링
- 링크: `{"type": "link", "url": "...", "text": "..."}`

**참고 구현:** `/tmp/schedule_notices_v3.py`의 `build_blocks()` 함수

#### 메시지 구성

```
[bold] {회차}회차. {주제} @channel

[quote] {부제 (있는 경우만)}

[bold] 일시장소

[bullet] {M월 D일 (요일)} {시간} {장소}
[bullet] 전체 일정은 {M월 D일 (요일), M월 D일 (요일), ...} 입니다.

> **날짜 형식**: 모든 날짜는 `M월 D일 (요일)` 형식 사용. `3/21(토)` 축약 금지.

[bold] 주차

{주중 또는 주말 주차 안내}

[bold] 참석 여부

[bullet] 인원 수에 맞춰 핸드아웃을 출력해야합니다.
[bullet] 출석 여부를 반드시 체크해주세요.
[bullet] 참석 여부 변경시 댓글로 알려주세요.
```

#### 주차 안내 (주중/주말 구분)

**주중 (월~금):**
```
[bullet] 킨코스 시청센터 옆 공터에 주중 저녁 주차가 가능합니다.
[bullet] 주차공간이 여유롭지 않으니 대중교통 이용 부탁드립니다.
```

**주말 (토~일):**
```
[bullet] 킨코스 시청센터 옆 공터에 주말 무료 주차가 가능합니다.
[bullet] 오전 10시 이후에는 차없는 거리로 진행되니 킨코스 시청센터 앞 일방통행로로 진입해주세요.
[bullet] 주차공간이 여유롭지 않으니 대중교통 이용 부탁드립니다.
```

### 3단계: 사용자 확인

다음 항목을 사용자에게 확인합니다:
- 팀 목록이 캘린더와 일치하는지
- 팀별 채널 매핑, 장소가 맞는지
- 메시지 내용 (주제, 세부 주제, 일시 등)이 맞는지

### 4단계: 테스트 DM 발송

실제 채널 예약 전에, `chat.scheduleMessage`로 **이슬기_HFK (User ID: UUSL62UJ2)** 에게 DM 테스트 발송합니다:
- 채널 파라미터에 User ID `UUSL62UJ2` 직접 사용 (DM 전송)
- `blocks` 파라미터에 동일한 `rich_text` 블록 사용
- 각 메시지 앞에 `[테스트] #채널명` 접두사 추가
- 1분 뒤 예약 (`post_at = int(time.time()) + 60`)
- 사용자가 DM에서 글머리 기호, 링크 등 형태 확인

### 5단계: 확정 및 실제 채널 예약

테스트 DM 확인 후 사용자 승인을 받으면:
1. `slack_sdk`의 `conversations.list`로 팀 채널 ID 조회 (rate limit 대비 캐싱)
2. `conversations.join`으로 채널 참여
3. `chat.scheduleMessage`로 예약 발송 (`blocks` + `text` fallback)
4. 발송 결과를 테이블로 출력

**예약 관리:**
```bash
# 현재 예약된 메시지 조회
cd "$HFK_SKLEE" && venv/bin/python scripts/schedule_slack_notices.py --list-scheduled

# 모든 예약 메시지 취소
cd "$HFK_SKLEE" && venv/bin/python scripts/schedule_slack_notices.py --cancel-all
```

## 데이터 소스 (우선순위)

1. **일정/시간/장소**: Google Calendar (정본) → `gcalcli` 또는 MCP Calendar로 조회
2. **세션 주제/부제**: Obsidian 상품 노트 (정본) → `product/26봄주중/*.md`, `product/26봄주말/*.md`의 "## 3개월 세션 주제" 섹션
3. **보조 참고**: `archive/data/teams_structured_dataset.json`, `imweb_products_*.json` (시즌이 맞을 때만)
4. **채널 매핑**: 팀명 → `1--{팀명}` (예외: 경영에센셜→경영브릿지, 글쓰는OO→글쓰는oo, AI핸즈온→ai핸즈온, AI부사수→ai부사수)

**주의**: `note/` 폴더의 "팀별 추천 회차" 파일은 인스타 포스팅용 선별 목록이므로 세션 주제 소스로 사용하지 마세요.

## 알려진 한계

- `teams_structured_dataset.json`은 시즌별로 갱신되므로, 현재 시즌과 맞는지 확인 필요
- 장소가 팀별로 다를 수 있음 (5층 오아시스 덕수궁 / 3층 소정동) → 캘린더에서 확인
- 이미 공지된 팀은 해당 채널 메시지 히스토리를 조회하여 제외

$ARGUMENTS
