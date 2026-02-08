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

### 1단계: 스크립트 미리보기 + 캘린더 교차 확인

$ARGUMENTS에서 시작일과 종료일(앞 2개)만 추출하여 미리보기를 실행합니다:

```bash
cd /Users/sklee/hfk-sklee && venv/bin/python scripts/schedule_slack_notices.py <시작일> <종료일>
```

**중요: `teams_structured_dataset.json`에 누락된 팀이 있을 수 있습니다.**
스크립트 결과를 HFK 캘린더의 해당 기간 `[팀]` 일정과 반드시 교차 확인하세요:
- 캘린더에는 있지만 스크립트에 없는 팀 → `archive/data/preview_*_팀명_content.html` 참고하여 수동 추가
- 스크립트에는 있지만 캘린더에 없는 팀 → 제외
- 장소가 다른 경우 → 캘린더 기준으로 수정 (기본: 5층 오아시스 덕수궁, 일부 팀: 3층 소정동)

### 2단계: 메시지 작성 규칙

- `@channel` 대신 반드시 `<!channel>` 사용 (Slack API에서 실제 알림을 트리거하려면 필수)
- 리스트는 `- ` 가 아닌 `• ` (Unicode bullet) 사용 (Slack에서 점 리스트로 표시)
- 주제(topic)만 있고 부제(subtitle)가 없는 팀은 blockquote(`>`) 줄 생략
- 메시지 템플릿:
```
*{회차}회차. {주제} <!channel>*

>{부제 (있는 경우만)}

*일시장소*

• {날짜} ({요일}) {시간} {장소}
• 전체 일정은 {전체 일정} 입니다.

*주차*

• 킨코스 시청센터 옆 공터에 주말 무료 주차가 가능합니다.
• 오전 10시 이후에는 차없는 거리로 진행되니 킨코스 시청센터 앞 일방통행로로 진입해주세요.
• 주차공간이 여유롭지 않으니 대중교통 이용 부탁드립니다.

*참석 여부*

• 인원 수에 맞춰 핸드아웃을 출력해야합니다.
• 출석 여부를 반드시 체크해주세요.
• 참석 여부 변경시 댓글로 알려주세요.
```

### 3단계: 사용자 확인

다음 항목을 사용자에게 확인합니다:
- 팀 목록이 캘린더와 일치하는지
- 팀별 채널 매핑, 장소가 맞는지
- 메시지 내용 (주제, 세부 주제, 일시 등)이 맞는지

### 4단계: 테스트 DM 발송

실제 채널 예약 전에, 생성된 메시지를 **이슬기_HFK (User ID: UUSL62UJ2)** 에게 DM으로 테스트 발송합니다:
- `chat.scheduleMessage`로 1분 뒤 DM 예약
- 채널 파라미터에 user ID를 직접 사용 (`UUSL62UJ2`)
- 각 메시지 앞에 `[테스트] #팀명` 접두사 추가
- 사용자가 DM에서 메시지 형태를 확인

### 5단계: 확정 및 실제 채널 예약

테스트 DM 확인 후 사용자 승인을 받으면:
1. 실제 팀 채널에 `chat.scheduleMessage`로 예약 (인자에서 받은 예약발송일시 사용)
2. 채널 자동 참여: `conversations_join` 호출 후 예약
3. 예약 결과를 테이블로 출력

## 기타 명령

```bash
# 현재 예약된 메시지 조회
cd /Users/sklee/hfk-sklee && venv/bin/python scripts/schedule_slack_notices.py --list-scheduled

# 모든 예약 메시지 취소
cd /Users/sklee/hfk-sklee && venv/bin/python scripts/schedule_slack_notices.py --cancel-all
```

## 데이터 소스

- 팀/세션 정보: `archive/data/teams_structured_dataset.json` (일부 팀 누락 가능)
- 시간대 정보: `archive/data/imweb_products_*.json`
- 팀 상품 HTML: `archive/data/preview_*_팀명_content.html` (structured dataset에 없는 팀 참고용)
- 채널 매핑: 팀명 → `1--{팀명}` (예외: 경영에센셜→경영브릿지, 글쓰는OO→글쓰는oo, AI핸즈온→ai핸즈온)

## 알려진 한계

- `teams_structured_dataset.json`에 리더의서재, 팀오호츠크 등 일부 팀이 누락됨
- 장소가 팀별로 다를 수 있음 (5층 오아시스 덕수궁 / 3층 소정동)
- 캘린더와 structured dataset의 일정이 다를 수 있음 → 캘린더가 정본

$ARGUMENTS
