# Slack 채널 일괄 생성 & 멤버 초대

CSV 파일을 읽어 Slack 채널을 생성하고, 이메일로 멤버를 초대합니다.

## 인자 형식

```
/create-slack-channels <csv파일명>
```

예시:
```
/create-slack-channels channels.csv
```

- csv파일명: 볼트 루트(`hfk-imweb/`) 기준 상대경로

## CSV 형식

```csv
channel_name,is_private,member1,member2,member3
project-alpha,false,user1@example.com,user2@example.com
team-beta,true,user3@example.com,user4@example.com
notice-general,false,user1@example.com
```

| 컬럼 | 설명 |
|------|------|
| channel_name | 채널 이름 (소문자, 하이픈 사용, 한글 불가) |
| is_private | `true`=비공개 채널, `false`=공개 채널 |
| 3번째 컬럼~ | 초대할 멤버의 이메일 주소 (여러 명 가능) |

## 실행 절차

### 1단계: CSV 검증

1. 인자로 받은 CSV 파일을 읽습니다
2. 각 행의 채널명, 공개/비공개, 멤버 이메일 목록을 파싱합니다
3. 사용자에게 생성할 채널 목록을 테이블로 보여주고 확인받습니다:

| # | 채널명 | 공개/비공개 | 멤버 수 | 멤버 이메일 |
|---|--------|------------|---------|------------|

### 2단계: Python 스크립트 실행

확인 후 다음 명령어로 실행합니다:

```bash
source ~/hfk-slack-venv/bin/activate && python slack_channel_creator.py <csv파일명>
```

스크립트가 하는 일:
1. `.env`에서 `SLACK_BOT_TOKEN` 로드
2. 토큰 인증 확인
3. 각 행에 대해:
   - 이메일 → Slack User ID 변환 (`users.lookupByEmail`)
   - 채널 생성 (`conversations.create`), 이미 존재하면 기존 채널 사용
   - 멤버 초대 (`conversations.invite`), 일괄 실패 시 개별 재시도

### 3단계: 결과 보고

실행 결과를 요약합니다:
- 성공/실패 채널 수
- 채널별 초대 결과
- 오류가 있었다면 원인과 해결 방법

## 필요 권한

Bot Token에 다음 OAuth scope가 필요합니다:
- `channels:manage` — 공개 채널 생성
- `channels:read` — 채널 조회
- `groups:write` — 비공개 채널 생성
- `channels:write.invites` / `groups:write.invites` — 멤버 초대
- `users:read.email` — 이메일로 사용자 조회

## 참고

- 스크립트: `slack_channel_creator.py`
- 토큰: `.env`의 `SLACK_BOT_TOKEN` (`.mcp.json`과 동일)
- venv: `~/hfk-slack-venv` (slack_sdk 설치됨)
- 샘플 CSV: `channels.csv`

$ARGUMENTS
