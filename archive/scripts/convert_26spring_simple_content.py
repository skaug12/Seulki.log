#!/usr/bin/env python3
"""
26봄주중, 26봄주말 카테고리 상품의 simple_content를 새로운 형식으로 변환
- 텍스트 내용은 유지하면서 HTML 형식만 변경
"""

import sys
import os
import re
from bs4 import BeautifulSoup
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI
from dotenv import load_dotenv

load_dotenv()


def extract_schedule_info(simple_content):
    """기존 simple_content에서 일정 정보 추출"""
    soup = BeautifulSoup(simple_content, 'html.parser')

    # 요일/시간 추출
    schedule_header = ""
    for strong in soup.find_all('strong'):
        text = strong.get_text().strip()
        if '요일' in text and ('개월' in text or ':' in text):
            schedule_header = text
            break

    # 회차별 날짜 추출
    sessions = {}
    text = soup.get_text()
    for i in range(1, 7):
        pattern = rf'{i}회차\s*(\d+월)\s*(\d+일)'
        match = re.search(pattern, text)
        if match:
            # "12월 12일" 형식으로 공백 포함
            sessions[i] = f"{match.group(1)} {match.group(2)}"

    return schedule_header, sessions


def extract_session_topics(content_plain):
    """content_plain에서 세션 주제 추출"""
    topics = {}

    if not content_plain:
        return topics

    # 세션 주제 섹션 찾기
    idx = content_plain.find('세션 주제')
    if idx < 0:
        return topics

    section = content_plain[idx:idx+2000]

    # 각 회차별로 주제 찾기
    for i in range(1, 7):
        # 패턴: "N회차" 이후에 날짜가 아닌 텍스트
        pattern = rf'{i}회차\s*\n+(\d+월\s*\d+일[^\n]*)\s*\n+([^\n]+)'
        match = re.search(pattern, section)
        if match:
            topic_text = match.group(2).strip()
            # 다음 회차나 진행방식이 아닌 경우에만 세션 주제로 저장
            if topic_text and not topic_text.startswith(str(i+1)) and topic_text != '진행방식':
                topics[i] = topic_text

    return topics


def generate_new_simple_content(schedule_header, sessions, topics):
    """새로운 형식의 simple_content 생성"""

    # 세션 행 HTML 생성
    session_rows = ""
    for i in range(1, 7):
        date = sessions.get(i, "")
        topic = topics.get(i, "")

        # 마지막 회차는 border-bottom 없음
        border_style = 'border-bottom:1px solid #ddd; ' if i < 6 else ''

        session_rows += f'''<!-- {i}회차 -->
		<div style="display:flex; flex-wrap:nowrap; {border_style}padding:14px 0;">
			<div style="flex:0 0 80px; padding:0 12px;">

				<p style="font-size:14px; font-weight:600; color:#8B0000; margin:0;">{i}회차</p>
			</div>
			<div style="flex:0 0 100px; padding:0 12px;">

				<p style="font-size:14px; color:#222; margin:0;">{date}</p>
			</div>
			<div style="flex:1 1 auto; padding:0 12px;">

				<p style="font-size:14px; color:#444; letter-spacing:-0.01em; margin:0;">{topic}</p>
			</div></div>
		'''

    # 전체 HTML 조합
    html = f'''<!-- ========================================
     SECTION: 일정 및 멤버십 안내
     ======================================== -->
<div style="margin-bottom:80px;">

	<h3 style="font-size:20px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">{schedule_header}</h3>
	<div style="border-top:2px solid #222; border-bottom:2px solid #222;">
		<!-- 일정 헤더 -->
		<div style="display:flex; flex-wrap:nowrap; border-bottom:1px solid #ddd; padding:12px 0; background:#F0EAE2;">
			<div style="flex:0 0 80px; padding:0 12px;">

				<p style="font-size:13px; font-weight:600; color:#555; letter-spacing:-0.01em; margin:0;">회차</p>
			</div>
			<div style="flex:0 0 100px; padding:0 12px;">

				<p style="font-size:13px; font-weight:600; color:#555; letter-spacing:-0.01em; margin:0;">날짜</p>
			</div>
			<div style="flex:1 1 auto; padding:0 12px;">

				<p style="font-size:13px; font-weight:600; color:#555; letter-spacing:-0.01em; margin:0;">세션 주제</p>
			</div></div>
		{session_rows}</div></div>
<!-- // SECTION: 일정 및 멤버십 안내 -->
<!-- ========================================
     SECTION: 3개월 시즌 멤버십
     ======================================== -->
<div style="margin-bottom:80px;">

	<h3 style="font-size:20px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">3개월 시즌 멤버십</h3>

	<ul style="margin:0; padding:0; list-style:none;">
		<li style="display:flex; align-items:flex-start; margin-bottom:14px;"><span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; font-size:13px; font-weight:600; margin-right:12px; flex-shrink:0;">1</span> <span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">6회의 정규 세션 참석</span></li>
		<li style="display:flex; align-items:flex-start; margin-bottom:14px;"><span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; font-size:13px; font-weight:600; margin-right:12px; flex-shrink:0;">2</span> <span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">HFK 이벤트 참여 (PEST브리핑, AAR 밋업, HBR 포럼, 저자 북토크)</span></li>
		<li style="display:flex; align-items:flex-start; margin-bottom:14px;"><span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; font-size:13px; font-weight:600; margin-right:12px; flex-shrink:0;">3</span> <span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">HBR 최신호 1권 (정가 2.5만원)</span></li>
		<li style="display:flex; align-items:flex-start; margin-bottom:14px;"><span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; font-size:13px; font-weight:600; margin-right:12px; flex-shrink:0;">4</span> <span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">마이시크릿덴/소정동 이용 할인</span></li>
		<li style="display:flex; align-items:flex-start;"><span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; font-size:13px; font-weight:600; margin-right:12px; flex-shrink:0;">5</span> <span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">폴인 Plus 3개월 이용권</span></li>
	</ul>
</div>
<!-- // SECTION: 3개월 시즌 멤버십 -->'''

    return html


def convert_and_update_simple_content(client, product_no, dry_run=True):
    """상품 simple_content를 변환하고 업데이트"""
    print(f"\n{'='*50}")
    print(f"상품 번호: {product_no}")
    print(f"{'='*50}")

    # 상품 상세 조회
    detail = client.get_product_detail(str(product_no))
    if 'error' in detail:
        print(f"❌ 상품 조회 실패: {detail['error']}")
        return False

    product_data = detail.get('data', {})
    name = product_data.get('name', 'unknown')
    simple_content = product_data.get('simple_content', '')
    content_plain = product_data.get('content_plain', '')

    print(f"상품명: {name}")

    if not simple_content:
        print("⚠️ simple_content가 비어있습니다. 스킵합니다.")
        return False

    # 기존 데이터 추출
    schedule_header, sessions = extract_schedule_info(simple_content)
    topics = extract_session_topics(content_plain)

    print(f"일정: {schedule_header}")
    print(f"회차별 날짜: {sessions}")
    print(f"회차별 주제: {topics}")

    if not schedule_header:
        print("⚠️ 일정 정보를 찾을 수 없습니다. 스킵합니다.")
        return False

    # 새 형식으로 변환
    new_simple_content = generate_new_simple_content(schedule_header, sessions, topics)

    # data 폴더가 없으면 생성
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 미리보기 저장
    preview_file = os.path.join(data_dir, f"preview_{product_no}_{name}_simple.html")
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(new_simple_content)
    print(f"✅ 미리보기 저장: {preview_file}")

    if dry_run:
        print("🔍 DRY RUN 모드 - 실제 업데이트하지 않음")
        return True

    # 실제 업데이트
    result = client.update_product(str(product_no), {'simple_content': new_simple_content})
    if result.get('code') == 200:
        print(f"✅ 상품 업데이트 성공: {name}")
        return True
    else:
        print(f"❌ 상품 업데이트 실패: {result}")
        return False


def main():
    """메인 함수"""
    api_key = os.getenv('IMWEB_API_KEY')
    api_secret = os.getenv('IMWEB_API_SECRET')

    if not api_key or not api_secret:
        print("❌ API 키가 설정되지 않았습니다.")
        return

    client = ImwebAPI(api_key, api_secret)

    # 26봄주중 카테고리 ID
    cat_weekday = 's2026012319995240b6e87'
    # 26봄주말 카테고리 ID
    cat_weekend = 's2026012311f5fb372b835'

    # 카테고리별 상품 목록 조회
    product_nos = []

    print("=== 26봄주중 카테고리 상품 조회 ===")
    weekday_products = client.get_products(category=cat_weekday, limit=50)
    if 'data' in weekday_products:
        data = weekday_products['data']
        if isinstance(data, dict) and 'list' in data:
            for p in data['list']:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")
        elif isinstance(data, list):
            for p in data:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")

    print("\n=== 26봄주말 카테고리 상품 조회 ===")
    weekend_products = client.get_products(category=cat_weekend, limit=50)
    if 'data' in weekend_products:
        data = weekend_products['data']
        if isinstance(data, dict) and 'list' in data:
            for p in data['list']:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")
        elif isinstance(data, list):
            for p in data:
                product_nos.append(p.get('no'))
                print(f"  {p.get('no')}: {p.get('name')}")

    if not product_nos:
        print("\n⚠️ 조회된 상품이 없습니다.")
        return

    print(f"\n총 {len(product_nos)}개 상품을 변환합니다.")

    # dry_run=True로 먼저 테스트
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("⚠️ 실제 업데이트 모드로 실행합니다!")

    success_count = 0
    fail_count = 0

    for product_no in product_nos:
        try:
            if convert_and_update_simple_content(client, product_no, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"\n{'='*50}")
    print(f"완료: 성공 {success_count}개, 실패 {fail_count}개")

    if dry_run:
        print("\n💡 실제 업데이트를 하려면 --execute 옵션을 추가하세요:")
        print("   python scripts/convert_26spring_simple_content.py --execute")


if __name__ == "__main__":
    main()
