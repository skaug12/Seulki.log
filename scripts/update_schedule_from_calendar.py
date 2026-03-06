#!/usr/bin/env python3
"""
Google Calendar에서 일정을 가져와 아임웹 26봄주중/26봄주말 상품의 content 업데이트
"""

import sys
import os
import re
import subprocess
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI

# API credentials
API_KEY = '809057085795e753d6135b26c46c559b2ea43f6384'
API_SECRET = '2310801a987b84e7e944ca'

# 상품명 → 캘린더 팀명 매핑 (26봄 캘린더 이벤트용)
PRODUCT_TO_CALENDAR = {
    '영화로운일': '영화로운일',
    '전략가의일': '전략가의일',
    '넘버앤센스': '넘버앤센스',
    '경영의전설': '경영의전설',
    '써보는경험': '써보는경험',
    'AI부사수': 'AI부사수',
    '경영브릿지': '경영브릿지',
    '리더의서재': '리더의서재',
    'AI핸즈온': 'AI핸즈온',
    '생각의구조': '생각의구조',
    '소통의기술': '소통의기술',
    '경영에센셜': '경영에센셜',
    '팀오호츠크': '팀오호츠크',
    '감각적기획': '감각적기획',
    '고급진영어': '고급진영어',
    '강점차별화': '강점차별화',
    '리더십첫줄': '리더십첫줄',
    '남다른한끗': '남다른한끗',
}

# 요일 매핑
DAY_MAP = {
    0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'
}


def get_calendar_events():
    """gcalcli를 사용해서 캘린더 이벤트 가져오기"""
    result = subprocess.run(
        ['gcalcli', '--calendar', 'HFK 캘린더', 'agenda', '2025-12-01', '2026-06-30', '--tsv'],
        capture_output=True, text=True
    )

    events = []
    for line in result.stdout.strip().split('\n')[1:]:  # Skip header
        parts = line.split('\t')
        if len(parts) >= 5:
            date_str = parts[0]
            title = parts[4]
            events.append({'date': date_str, 'title': title})

    return events


def parse_team_schedules(events):
    """이벤트에서 팀별 일정 추출 - 26봄 형식 지원"""
    team_schedules = {}

    for event in events:
        title = event['title']
        date_str = event['date']

        # [팀] 26봄 으로 시작하는 이벤트만 처리
        if '[팀] 26봄 ' in title:
            # 팀 이름 추출 (26봄 다음의 상품명)
            team_name = title.replace('[팀] 26봄 ', '').strip()

            # 요일+시간 슬롯 형식은 스킵 (예: "월요일 저녁 소정동A")
            if any(day in team_name for day in ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']):
                continue

            # 날짜 파싱
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month = date_obj.month
                day = date_obj.day
                weekday = DAY_MAP[date_obj.weekday()]
                formatted_date = f"{month}월 {day}일"
                formatted_with_day = f"{month}월 {day}일 ({weekday})"

                if team_name not in team_schedules:
                    team_schedules[team_name] = []
                team_schedules[team_name].append({
                    'date': date_obj,
                    'formatted': formatted_date,
                    'formatted_with_day': formatted_with_day
                })
            except ValueError:
                continue

    # 날짜순 정렬하고 첫 6개만
    for team_name in team_schedules:
        team_schedules[team_name] = sorted(team_schedules[team_name], key=lambda x: x['date'])[:6]

    return team_schedules


def update_content_dates(content, sessions):
    """content에서 세션 날짜 업데이트"""
    if not content or not sessions:
        return content, []

    changes = []
    new_content = content

    # 각 회차별로 날짜 업데이트
    for i, session in enumerate(sessions, 1):
        new_date = session['formatted']

        # 패턴: N회차 뒤에 나오는 날짜를 찾아서 업데이트
        # 예: <p style="...">12월 7일</p> 같은 형태
        pattern = rf'({i}회차</p>\s*</div>\s*<div[^>]*>\s*<p[^>]*>)(\d+월\s*\d+일)(</p>)'

        match = re.search(pattern, new_content)
        if match:
            old_date = match.group(2)
            if old_date.replace(' ', '') != new_date.replace(' ', ''):
                new_content = re.sub(pattern, rf'\g<1>{new_date}\g<3>', new_content)
                changes.append(f"{i}회차: {old_date} → {new_date}")

    return new_content, changes


def update_simple_content_dates(simple_content, sessions):
    """simple_content에서 세션 날짜 업데이트"""
    if not simple_content or not sessions:
        return simple_content, []

    changes = []
    new_content = simple_content

    for i, session in enumerate(sessions, 1):
        new_date = session['formatted']

        # simple_content의 날짜 패턴
        pattern = rf'({i}회차</p>\s*</div>\s*<div[^>]*>\s*<p[^>]*>)(\d+월\s*\d+일)(</p>)'

        match = re.search(pattern, new_content)
        if match:
            old_date = match.group(2)
            if old_date.replace(' ', '') != new_date.replace(' ', ''):
                new_content = re.sub(pattern, rf'\g<1>{new_date}\g<3>', new_content)
                changes.append(f"simple {i}회차: {old_date} → {new_date}")

    return new_content, changes


def update_product(client, product_no, team_schedules, dry_run=True):
    """상품 content 업데이트"""
    print(f"\n{'='*60}")
    print(f"상품 번호: {product_no}")
    print(f"{'='*60}")

    # 상품 상세 조회
    detail = client.get_product_detail(str(product_no))
    if 'error' in detail or detail.get('code') != 200:
        print(f"상품 조회 실패: {detail}")
        return False

    product_data = detail.get('data', {})
    name = product_data.get('name', 'unknown')
    content = product_data.get('content', '')
    simple_content = product_data.get('simple_content', '')

    print(f"상품명: {name}")

    # 캘린더 팀명 찾기
    calendar_name = PRODUCT_TO_CALENDAR.get(name)
    if not calendar_name:
        print(f"캘린더 매핑 없음: {name}")
        return True

    # 캘린더에서 일정 찾기
    sessions = team_schedules.get(calendar_name, [])
    if not sessions:
        print(f"캘린더에서 일정을 찾을 수 없음: {calendar_name}")
        return True

    print(f"캘린더 일정 ({len(sessions)}개):")
    for i, s in enumerate(sessions, 1):
        print(f"  {i}회차: {s['formatted_with_day']}")

    # 5개 미만 세션은 스킵 (불완전한 데이터)
    if len(sessions) < 5:
        print(f"세션 수가 부족하여 스킵 (최소 5개 필요)")
        return True

    # content 업데이트
    new_content, content_changes = update_content_dates(content, sessions)
    new_simple, simple_changes = update_simple_content_dates(simple_content, sessions)

    all_changes = content_changes + simple_changes

    if not all_changes:
        print("변경사항 없음 (일정이 이미 최신)")
        return True

    print(f"변경사항:")
    for change in all_changes:
        print(f"  - {change}")

    if dry_run:
        print("DRY RUN 모드 - 실제 업데이트하지 않음")
        return True

    # 실제 업데이트
    update_data = {}
    if content_changes:
        update_data['content'] = new_content
    if simple_changes:
        update_data['simple_content'] = new_simple

    if update_data:
        result = client.update_product(str(product_no), update_data)
        if result.get('code') == 200:
            print(f"상품 업데이트 성공: {name}")
            return True
        else:
            print(f"상품 업데이트 실패: {result}")
            return False

    return True


def main():
    print("=== Google Calendar에서 일정 가져오기 ===")
    events = get_calendar_events()
    print(f"총 {len(events)}개 이벤트 조회됨")

    print("\n=== 팀별 일정 파싱 ===")
    team_schedules = parse_team_schedules(events)
    for team, sessions in sorted(team_schedules.items()):
        if len(sessions) >= 4:  # 4회차 이상인 팀만 출력
            dates = [s['formatted'] for s in sessions]
            print(f"  {team}: {dates}")

    client = ImwebAPI(API_KEY, API_SECRET)

    # 26봄주중 카테고리 ID
    cat_weekday = 's2026012319995240b6e87'
    # 26봄주말 카테고리 ID
    cat_weekend = 's2026012311f5fb372b835'

    # 카테고리별 상품 목록 조회
    product_nos = []

    print("\n=== 26봄주중 카테고리 상품 조회 ===")
    weekday_products = client.get_products(category=cat_weekday, limit=50)
    if 'data' in weekday_products:
        data = weekday_products['data']
        if isinstance(data, dict) and 'list' in data:
            for p in data['list']:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")

    time.sleep(1)

    print("\n=== 26봄주말 카테고리 상품 조회 ===")
    weekend_products = client.get_products(category=cat_weekend, limit=50)
    if 'data' in weekend_products:
        data = weekend_products['data']
        if isinstance(data, dict) and 'list' in data:
            for p in data['list']:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")

    if not product_nos:
        print("\n조회된 상품이 없습니다.")
        return

    print(f"\n총 {len(product_nos)}개 상품을 업데이트합니다.")

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("실제 업데이트 모드로 실행합니다!")

    success_count = 0
    fail_count = 0

    for product_no in product_nos:
        try:
            if update_product(client, product_no, team_schedules, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"완료: 성공 {success_count}개, 실패 {fail_count}개")

    if dry_run:
        print("\n실제 업데이트를 하려면 --execute 옵션을 추가하세요:")
        print("   python scripts/update_schedule_from_calendar.py --execute")


if __name__ == '__main__':
    main()
