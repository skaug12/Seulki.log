#!/usr/bin/env python3
"""
HFK 슬랙 공지 예약 발송

일정 범위 내 팀 세션을 찾아 슬랙 채널별 공지를 생성/예약합니다.
teams_structured_dataset.json과 아임웹 상품 데이터를 참조합니다.

주의: teams_structured_dataset.json에 누락된 팀(리더의서재, 팀오호츠크 등)이 있을 수 있음.
      실제 캘린더와 교차 확인 필요. 장소도 팀별로 다를 수 있음 (기본: 5층 오아시스 덕수궁).

사용법:
  # 메시지 미리보기
  venv/bin/python scripts/schedule_slack_notices.py 2026-02-16 2026-02-22

  # 예약 발송
  venv/bin/python scripts/schedule_slack_notices.py 2026-02-16 2026-02-22 --schedule-at "2026-02-09 21:00"

  # 현재 예약 목록 확인
  venv/bin/python scripts/schedule_slack_notices.py --list-scheduled

  # 예약 전체 취소
  venv/bin/python scripts/schedule_slack_notices.py --cancel-all
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ── 설정 ──────────────────────────────────────────────

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

KST = timezone(timedelta(hours=9))
DATA_DIR = Path(__file__).resolve().parent.parent / 'archive' / 'data'
LOCATION = "5층 오아시스 덕수궁"

PARKING_INFO = """\
• 킨코스 시청센터 옆 공터에 주말 무료 주차가 가능합니다.
• 오전 10시 이후에는 차없는 거리로 진행되니 킨코스 시청센터 앞 일방통행로로 진입해주세요.
• 주차공간이 여유롭지 않으니 대중교통 이용 부탁드립니다."""

ATTENDANCE_INFO = """\
• 인원 수에 맞춰 핸드아웃을 출력해야합니다.
• 출석 여부를 반드시 체크해주세요.
• 참석 여부 변경시 댓글로 알려주세요."""

# 팀 이름 → Slack 채널명 (예외 매핑)
CHANNEL_OVERRIDES = {
    "경영에센셜": "1--경영브릿지",
    "글쓰는OO": "1--글쓰는oo",
    "AI핸즈온": "1--ai핸즈온",
    "리더의서재": "1--리더의서재",
    "팀오호츠크": "1--팀오호츠크",
}


# ── 데이터 로딩 ───────────────────────────────────────

def load_teams_data():
    """teams_structured_dataset.json 로드"""
    path = DATA_DIR / 'teams_structured_dataset.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_imweb_products():
    """아임웹 상품 JSON을 모두 로드하여 product_no → product dict 매핑 반환"""
    products = {}
    for path in sorted(DATA_DIR.glob('imweb_products_*.json')):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                products[item['no']] = item
    return products


def extract_time_range(product):
    """상품의 simple_content_plain에서 시간대 추출 (예: '19:30~22:00')"""
    text = product.get('simple_content_plain', '')
    match = re.search(r'(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})', text)
    if match:
        return f"{match.group(1)}~{match.group(2)}"
    return None


# ── 날짜 처리 ─────────────────────────────────────────

def parse_korean_date(date_str, range_start, range_end):
    """'2월 19일' 형식을 datetime으로 변환. 범위 내이면 반환, 아니면 None."""
    match = re.match(r'(\d+)월\s*(\d+)일', date_str)
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))

    for year in [range_start.year, range_start.year - 1, range_start.year + 1]:
        try:
            d = datetime(year, month, day)
            if range_start <= d <= range_end:
                return d
        except ValueError:
            continue
    return None


# ── 세션 매칭 ─────────────────────────────────────────

def find_matching_sessions(teams_data, products, start_date, end_date):
    """주어진 날짜 범위에 세션이 있는 팀 목록을 반환"""
    results = []

    for team in teams_data.get('teams', []):
        meta = team.get('meta', {})
        content = team.get('content', {})
        team_name = content.get('team_name', meta.get('name', ''))
        product_no = meta.get('no')
        sessions = content.get('sessions', [])

        if not sessions:
            continue

        product = products.get(product_no, {})
        time_range = extract_time_range(product)

        for session in sessions:
            session_date = parse_korean_date(
                session.get('date', ''), start_date, end_date
            )
            if session_date:
                all_dates = ", ".join(
                    f"{s['date']} ({s['day']})" for s in sessions
                )

                results.append({
                    'team_name': team_name,
                    'product_no': product_no,
                    'session_number': session.get('session_number'),
                    'date': session.get('date'),
                    'day': session.get('day'),
                    'session_date': session_date,
                    'time_range': time_range,
                    'topic': session.get('topic', ''),
                    'subtitle': session.get('subtitle', ''),
                    'all_dates': all_dates,
                })
                break  # 같은 팀에서 1세션만

    results.sort(key=lambda x: x['session_date'])
    return results


# ── 메시지 생성 ───────────────────────────────────────

def clean_text(text):
    """데이터에서 가져온 텍스트 정리"""
    text = text.strip()
    # "N회차:" 또는 "N회차 " 접두사 제거
    text = re.sub(r'^\d+회차[:\s]+', '', text)
    # 선행 "- " 제거
    text = re.sub(r'^-\s+', '', text)
    return text


def format_notice(info):
    """세션 정보로 슬랙 공지 메시지 생성"""
    session_num = info['session_number']
    topic = clean_text(info['topic'])
    subtitle = clean_text(info['subtitle'])
    date = info['date']
    day = info['day']
    time_range = info['time_range'] or '시간 미정'
    all_dates = info['all_dates']

    return f"""*{session_num}회차. {topic} <!channel>*

>{subtitle}

*일시장소*

• {date} ({day}) {time_range} {LOCATION}
• 전체 일정은 {all_dates} 입니다.

*주차*

{PARKING_INFO}

*참석 여부*

{ATTENDANCE_INFO}"""


# ── Slack 연동 ────────────────────────────────────────

def get_client():
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("ERROR: .env에 SLACK_BOT_TOKEN을 설정해주세요.")
        sys.exit(1)
    return WebClient(token=token)


def get_channel_name(team_name):
    """팀 이름으로 Slack 채널명 추정"""
    if team_name in CHANNEL_OVERRIDES:
        return CHANNEL_OVERRIDES[team_name]
    name = team_name.lower()
    name = re.sub(r'\(.*?\)', '', name).strip()
    return f"1--{name}"


def resolve_channel_id(client, channel_name):
    """채널명으로 ID 조회"""
    for channel_type in ["public_channel", "private_channel"]:
        cursor = None
        while True:
            try:
                result = client.conversations_list(
                    types=channel_type, limit=200, cursor=cursor
                )
                for ch in result["channels"]:
                    if ch["name"] == channel_name:
                        return ch["id"]
                cursor = result.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            except SlackApiError:
                break
    return None


def schedule_notices(client, notices, schedule_time):
    """메시지들을 Slack에 예약 발송"""
    post_at = int(schedule_time.timestamp())
    print(f"\n예약 시각: {schedule_time.strftime('%Y-%m-%d %H:%M KST')}")
    print("=" * 60)

    results = []
    for item in notices:
        team = item['team_name']
        channel_name = item['channel_name']
        message = item['message']

        print(f"\n{'─' * 40}")
        print(f"팀: {team}  →  #{channel_name}")

        channel_id = resolve_channel_id(client, channel_name)
        if not channel_id:
            print(f"  ❌ 채널 '{channel_name}'을 찾을 수 없습니다.")
            results.append({"team": team, "status": "error", "reason": "channel not found"})
            continue

        # 채널 참여
        try:
            client.conversations_join(channel=channel_id)
        except SlackApiError as e:
            if "already_in_channel" not in str(e):
                print(f"  ⚠️ 채널 참여 실패: {e.response.get('error', str(e))}")

        try:
            resp = client.chat_scheduleMessage(
                channel=channel_id, text=message, post_at=post_at
            )
            msg_id = resp.get("scheduled_message_id", "")
            print(f"  ✅ 예약 완료 (ID: {msg_id})")
            results.append({"team": team, "status": "scheduled", "id": msg_id})
        except SlackApiError as e:
            error = e.response.get("error", str(e))
            print(f"  ❌ 실패: {error}")
            results.append({"team": team, "status": "error", "reason": error})

    ok = sum(1 for r in results if r["status"] == "scheduled")
    fail = sum(1 for r in results if r["status"] == "error")
    print(f"\n{'=' * 60}")
    print(f"결과: 성공 {ok}개 / 실패 {fail}개")
    return results


def list_scheduled(client):
    """현재 예약된 메시지 목록 조회"""
    result = client.chat_scheduledMessages_list()
    msgs = result.get('scheduled_messages', [])
    if not msgs:
        print("예약된 메시지가 없습니다.")
        return
    print(f"\n예약된 메시지: {len(msgs)}개")
    for msg in msgs:
        ts = datetime.fromtimestamp(msg['post_at'], tz=KST)
        print(f"  채널: {msg['channel_id']}  |  발송: {ts.strftime('%Y-%m-%d %H:%M KST')}  |  ID: {msg['id']}")


def cancel_all_scheduled(client):
    """모든 예약 메시지 취소"""
    result = client.chat_scheduledMessages_list()
    msgs = result.get('scheduled_messages', [])
    if not msgs:
        print("취소할 예약 메시지가 없습니다.")
        return
    for msg in msgs:
        try:
            client.chat_deleteScheduledMessage(
                channel=msg['channel_id'],
                scheduled_message_id=msg['id']
            )
            print(f"  삭제: {msg['id']}")
        except Exception as e:
            print(f"  실패: {msg['id']} - {e}")
    print(f"\n{len(msgs)}개 예약 메시지 취소 완료")


# ── 메인 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="HFK 슬랙 공지 예약 발송")
    parser.add_argument("start_date", nargs="?", help="시작일 (YYYY-MM-DD)")
    parser.add_argument("end_date", nargs="?", help="종료일 (YYYY-MM-DD)")
    parser.add_argument("--schedule-at", help="예약 시각 (YYYY-MM-DD HH:MM, KST)")
    parser.add_argument("--list-scheduled", action="store_true", help="예약 목록 조회")
    parser.add_argument("--cancel-all", action="store_true", help="모든 예약 취소")
    args = parser.parse_args()

    client = get_client()

    if args.list_scheduled:
        list_scheduled(client)
        return

    if args.cancel_all:
        cancel_all_scheduled(client)
        return

    if not args.start_date or not args.end_date:
        parser.error("시작일과 종료일을 입력해주세요. 예: 2026-02-16 2026-02-22")

    start = datetime.strptime(args.start_date, "%Y-%m-%d")
    end = datetime.strptime(args.end_date, "%Y-%m-%d")

    # 데이터 로드
    print("데이터 로딩 중...")
    teams_data = load_teams_data()
    products = load_imweb_products()

    # 매칭 세션 찾기
    matches = find_matching_sessions(teams_data, products, start, end)

    if not matches:
        print(f"\n{args.start_date} ~ {args.end_date} 범위에 팀 세션이 없습니다.")
        return

    # 메시지 생성 및 미리보기
    notices = []
    print(f"\n{args.start_date} ~ {args.end_date} 세션: {len(matches)}개 팀")
    print("=" * 60)

    for info in matches:
        message = format_notice(info)
        channel_name = get_channel_name(info['team_name'])
        notices.append({
            **info,
            'channel_name': channel_name,
            'message': message,
        })

        print(f"\n{'─' * 40}")
        print(f"팀: {info['team_name']}  →  #{channel_name}")
        print(f"{'─' * 40}")
        print(message)

    # 예약 발송
    if args.schedule_at:
        dt = datetime.strptime(args.schedule_at, "%Y-%m-%d %H:%M")
        schedule_time = dt.replace(tzinfo=KST)
        schedule_notices(client, notices, schedule_time)
    else:
        print(f"\n{'=' * 60}")
        print("미리보기 모드입니다. 예약하려면 --schedule-at 옵션을 추가하세요:")
        print(f'  venv/bin/python scripts/schedule_slack_notices.py {args.start_date} {args.end_date} --schedule-at "YYYY-MM-DD HH:MM"')


if __name__ == "__main__":
    main()
