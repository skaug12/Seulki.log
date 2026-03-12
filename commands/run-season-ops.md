# HFK 시즌 운영 에이전트

시즌 시작/운영에 필요한 일련의 작업을 자동으로 수행하는 에이전트입니다.
개별 스킬을 순차적으로 실행하며, 사용자 승인이 필요한 지점에서 확인을 요청합니다.

## 사용법

```
/run-season-ops
```

## 실행 워크플로우

### Step 1: 일정 업데이트 (update-schedule)

1. 사용자에게 대상 시즌 카테고리를 선택하도록 질문합니다 (26봄주중, 26봄주말 등)
2. MCP Google Calendar `list-events`로 해당 시즌 기간의 캘린더 일정을 조회합니다
3. 이벤트를 팀명별로 매칭하여 각 상품 노트의 세션 날짜를 업데이트합니다
4. 업데이트된 파일 목록과 변경 내용을 사용자에게 보여줍니다
5. `status`를 `draft`로 변경합니다

**사용자 확인**: 업데이트된 일정이 맞는지 확인

### Step 2: 아임웹 동기화 (sync-products)

1. Step 1에서 `status: draft`로 변경된 파일 목록을 보여줍니다
2. 각 파일의 Markdown을 파싱하여 HTML 생성
3. MCP Imweb `imweb_update_product` / `imweb_create_product`로 동기화
4. 성공 시 `status: synced`로 변경

**사용자 확인**: 동기화 진행 여부

### Step 3: 시즌레터 생성 (generate-letter) [선택]

사용자에게 시즌레터를 생성할지 질문합니다:
- "예" → 시즌, 레터번호, 제목을 입력받아 시즌레터 생성
  - MCP Google Calendar `list-events`로 팀 세션 안내 일정 자동 조회
  - 섹션 구성에 대해 사용자와 대화
  - HTML 결과물 생성
- "아니오" → Step 4로 이동

### Step 4: Slack 공지 예약 (schedule-notices) [선택]

사용자에게 Slack 공지를 예약할지 질문합니다:
- "예" → 시작일, 종료일, 예약발송일시를 입력받아 실행
  - MCP Google Calendar로 일정 조회
  - MCP Slack `slack_post_message`로 테스트 DM 발송
  - 사용자 승인 후 실제 채널에 발송
- "아니오" → 종료

## 워크플로우 다이어그램

```
[카테고리 선택]
      ↓
[Step 1: 일정 업데이트] ← Google Calendar MCP
      ↓ (사용자 확인)
[Step 2: 아임웹 동기화] ← Imweb MCP
      ↓ (사용자 확인)
[Step 3: 시즌레터?] ← Google Calendar MCP (선택)
      ↓
[Step 4: Slack 공지?] ← Slack MCP (선택)
      ↓
[완료 요약]
```

## 완료 요약

모든 단계 완료 후 실행 결과를 요약합니다:
- 업데이트된 상품 노트 수
- 동기화된 상품 수
- 생성된 시즌레터 (있는 경우)
- 예약된 Slack 공지 수 (있는 경우)

## 내용 보존 규칙 (전 단계 공통)

- **Step 1 (update-schedule)**: 날짜 필드만 수정합니다. 주제, 설명, 활동, 본문 섹션은 절대 변경하지 않습니다. 파일 전체를 다시 쓰지 않고 해당 줄만 Edit합니다
- **Step 2 (sync-products)**: MD→HTML 변환 시 원본 텍스트를 1:1로 그대로 변환합니다. 요약, 축약, 의역하지 않습니다. `status`와 `product_no`만 변경합니다
- **Step 1에서 변경되지 않은 파일**은 Step 2에서 동기화 대상이 아닙니다 (`status: synced` 유지 → 스킵)
- 각 Step 사이에 사용자 확인을 반드시 거칩니다
