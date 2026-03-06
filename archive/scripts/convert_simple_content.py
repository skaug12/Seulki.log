#!/usr/bin/env python3
"""
아임웹 상품 simple_content를 새로운 형식으로 변환하는 스크립트
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
        if '요일' in text:
            schedule_header = text
            break

    # 회차별 날짜 추출
    sessions = {}

    # 패턴 1: "1회차 12월 12일" 형식
    text = soup.get_text()
    for i in range(1, 7):
        pattern = rf'{i}회차\s*(\d+월\s*\d+일)'
        match = re.search(pattern, text)
        if match:
            sessions[i] = match.group(1).replace(' ', '')

    return schedule_header, sessions


def extract_session_topics_from_file(product_no, name):
    """저장된 원본 content 파일에서 세션 주제 추출"""
    topics = {}

    # 원본 파일 경로 시도
    file_paths = [
        f"data/product_{product_no}_{name}_content.html",
        f"data/product_{product_no}_unknown_content.html"
    ]

    content = ""
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  원본 파일 로드: {file_path}")
            break

    if not content:
        print(f"  원본 파일 없음")
        return topics

    soup = BeautifulSoup(content, 'html.parser')

    # "3개월 세션 주제" 섹션 찾기
    session_section = None
    for elem in soup.find_all(['p', 'strong']):
        if '3개월 세션 주제' in elem.get_text() or '세션 주제' in elem.get_text():
            # 다음 형제 요소에서 세션 정보 찾기
            session_section = elem.find_next('div', style=lambda x: x and 'border' in str(x))
            break

    if session_section:
        # 회차별 세션 주제 찾기
        for i in range(1, 7):
            pattern = f"{i}회차"
            # 해당 회차를 포함하는 div 찾기
            for div in session_section.find_all('div', style=lambda x: x and 'flex' in str(x)):
                div_text = div.get_text()
                if pattern in div_text:
                    # 세션 제목 찾기 - 회차/날짜가 아닌 strong 태그
                    for strong in div.find_all('strong'):
                        strong_text = strong.get_text().strip()
                        # 회차, 날짜가 아닌 실제 주제 텍스트 찾기
                        if (strong_text and
                            '회차' not in strong_text and
                            not re.match(r'^\d+월', strong_text) and
                            len(strong_text) > 3):
                            topics[i] = unescape(strong_text)
                            break
                    break

    return topics


def extract_session_topics(content):
    """content에서 세션 주제 추출 (레거시 - 현재 content에서)"""
    soup = BeautifulSoup(content, 'html.parser')
    topics = {}

    # 회차별 세션 주제 찾기
    for i in range(1, 7):
        pattern = f"{i}회차"
        for elem in soup.find_all(['strong', 'span', 'p']):
            if pattern in elem.get_text():
                # 부모 div에서 세션 주제 찾기
                parent = elem.find_parent('div', style=lambda x: x and 'flex' in str(x))
                if parent:
                    # 세션 제목 찾기 (font-weight:700 스타일의 p 태그)
                    title_elem = parent.find('p', style=lambda x: x and 'font-weight:700' in str(x))
                    if title_elem:
                        title_text = title_elem.get_text().strip()
                        # 회차, 날짜 정보 제거
                        if title_text and '회차' not in title_text and '월' not in title_text[:3]:
                            topics[i] = title_text
                            break

                    # 또는 strong 태그 내 텍스트
                    for strong in parent.find_all('strong'):
                        strong_text = strong.get_text().strip()
                        if strong_text and '회차' not in strong_text and '월' not in strong_text[:3] and len(strong_text) > 5:
                            topics[i] = strong_text
                            break
                break

    return topics


def generate_new_simple_content(schedule_header, sessions, topics):
    """새로운 형식의 simple_content 생성"""

    # 세션 행 HTML 생성
    session_rows = ""
    for i in range(1, 7):
        date = sessions.get(i, f"{i}회차")
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
    content = product_data.get('content', '')

    print(f"상품명: {name}")

    if not simple_content:
        print("⚠️ simple_content가 비어있습니다. 스킵합니다.")
        return False

    # 기존 데이터 추출
    schedule_header, sessions = extract_schedule_info(simple_content)

    # 원본 파일에서 세션 주제 추출 시도
    topics = extract_session_topics_from_file(product_no, name)

    # 원본 파일에서 못 찾으면 현재 content에서 추출
    if not topics:
        topics = extract_session_topics(content)

    print(f"일정: {schedule_header}")
    print(f"회차별 날짜: {sessions}")
    print(f"회차별 주제: {topics}")

    if not schedule_header:
        print("⚠️ 일정 정보를 찾을 수 없습니다. 스킵합니다.")
        return False

    # 새 형식으로 변환
    new_simple_content = generate_new_simple_content(schedule_header, sessions, topics)

    # 미리보기 저장
    preview_file = f"data/preview_{product_no}_{name}_simple.html"
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

    # 26봄주중 카테고리 상품 목록
    product_nos = [136, 134, 132, 128, 60, 58, 52, 49]

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
        print("   python scripts/convert_simple_content.py --execute")


if __name__ == "__main__":
    main()
