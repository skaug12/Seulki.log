#!/usr/bin/env python3
"""
26봄주중, 26봄주말 카테고리 상품의 content와 simple_content를 새로운 형식으로 변환
- 텍스트 내용은 유지하면서 HTML 형식만 변경
"""

import sys
import os
import re
from bs4 import BeautifulSoup
from html import unescape, escape

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI

# API credentials
API_KEY = '809057085795e753d6135b26c46c559b2ea43f6384'
API_SECRET = '2310801a987b84e7e944ca'


def extract_images_from_content(content_html):
    """HTML content에서 이미지 URL 추출"""
    soup = BeautifulSoup(content_html, 'html.parser')
    images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and 'cdn.imweb.me' in src:
            images.append(src)
    return images


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

    # h3 태그에서도 찾기
    if not schedule_header:
        for h3 in soup.find_all('h3'):
            text = h3.get_text().strip()
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
            sessions[i] = f"{match.group(1)} {match.group(2)}"

    return schedule_header, sessions


def extract_content_sections(content_plain):
    """content_plain에서 각 섹션 텍스트 추출"""
    sections = {
        'headline': '',
        'intro': [],
        'team_background': [],
        'team_direction': [],
        'team_growth': [],
        'team_members': [],
        'partner_name': '',
        'partner_desc': '',
        'partner_reason': '',
        'sessions': {},
        'process': []
    }

    if not content_plain:
        return sections

    lines = content_plain.split('\n')
    current_section = 'intro'
    current_session = 0
    session_data = {}
    skip_next_subtitle = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 섹션 헤더 감지 - 한 줄에 같이 있는 패턴 (예: "01  팀 배경")
        if re.match(r'^01\s+팀\s*배경', line):
            current_section = 'team_background'
            skip_next_subtitle = True
            i += 1
            continue
        elif re.match(r'^02\s+팀\s*운영\s*방향', line):
            current_section = 'team_direction'
            skip_next_subtitle = True
            i += 1
            continue
        elif re.match(r'^02\s+팀\s*멤버들', line):
            current_section = 'team_members'
            skip_next_subtitle = True
            i += 1
            continue
        elif re.match(r'^03\s+팀\s*성장\s*포인트', line):
            current_section = 'team_growth'
            skip_next_subtitle = True
            i += 1
            continue
        elif re.match(r'^04\s+팀\s*멤버들', line):
            current_section = 'team_members'
            skip_next_subtitle = True
            i += 1
            continue
        # 섹션 헤더 감지 (단독 라인)
        elif line == '01':
            current_section = 'wait_team_background'
            i += 1
            continue
        elif line == '팀 배경' and current_section == 'wait_team_background':
            current_section = 'team_background'
            skip_next_subtitle = True
            i += 1
            continue
        elif line == '02':
            current_section = 'wait_02'
            i += 1
            continue
        elif line == '팀 운영 방향' and current_section == 'wait_02':
            current_section = 'team_direction'
            skip_next_subtitle = True
            i += 1
            continue
        elif line == '팀 멤버들' and current_section == 'wait_02':
            current_section = 'team_members'
            skip_next_subtitle = True
            i += 1
            continue
        elif line == '03':
            current_section = 'wait_team_growth'
            i += 1
            continue
        elif line == '팀 성장 포인트' and current_section == 'wait_team_growth':
            current_section = 'team_growth'
            skip_next_subtitle = True
            i += 1
            continue
        elif line == '04':
            current_section = 'wait_team_members'
            i += 1
            continue
        elif line == '팀 멤버들' and current_section == 'wait_team_members':
            current_section = 'team_members'
            skip_next_subtitle = True
            i += 1
            continue
        elif line in ['PARTNER', '파트너 소개']:
            current_section = 'partner'
            i += 1
            continue
        elif line == '3개월 세션 주제':
            current_section = 'sessions'
            i += 1
            continue
        elif line == '진행방식':
            current_section = 'process'
            i += 1
            continue
        elif line == '그라운드룰':
            current_section = 'end'
            break

        # 부제목 스킵
        if skip_next_subtitle:
            skip_next_subtitle = False
            if '어떤 계기로' in line or '어떤 방식으로' in line or '어떤 성장을' in line or '누가 함께' in line:
                i += 1
                continue

        # 좌우로 스크롤 텍스트는 스킵
        if '좌우로 스크롤' in line:
            i += 1
            continue

        # 세션 데이터 파싱
        if current_section == 'sessions':
            session_match = re.match(r'^(\d)회차$', line)
            if session_match:
                if current_session > 0 and session_data:
                    sections['sessions'][current_session] = session_data
                current_session = int(session_match.group(1))
                session_data = {'date': '', 'title': '', 'description': '', 'activities': []}
                i += 1
                continue

            if current_session > 0:
                # 날짜 (예: 12월 7일 (금))
                date_match = re.match(r'^(\d+월\s*\d+일\s*\([월화수목금토일]\))$', line)
                if date_match and not session_data['date']:
                    session_data['date'] = date_match.group(1)
                    i += 1
                    continue

                # N회차 패턴이면 스킵 (다음 세션)
                if re.match(r'^(\d)회차$', line):
                    i += 1
                    continue

                # 활동 (※로 시작)
                if line.startswith('※'):
                    session_data['activities'].append(line)
                    i += 1
                    continue

                # 제목 (날짜 이후 첫 번째 비어있지 않은 줄, 진행방식이 아닌 경우)
                if session_data['date'] and not session_data['title'] and line and line != '진행방식':
                    session_data['title'] = line
                elif session_data['title'] and line and line != '진행방식':
                    if not session_data['description']:
                        session_data['description'] = line
                    else:
                        session_data['description'] += ' ' + line

            i += 1
            continue

        # 파트너 섹션 파싱
        if current_section == 'partner':
            if line == '파트너 소개':
                i += 1
                continue
            if not sections['partner_name'] and line:
                sections['partner_name'] = line
            elif 'HFK가' in line and '기획한 이유' in line:
                i += 1
                if i < len(lines):
                    sections['partner_reason'] = lines[i].strip()
            elif sections['partner_name'] and not sections['partner_desc'] and line and 'HFK가' not in line:
                sections['partner_desc'] = line
            i += 1
            continue

        # 대기 섹션은 스킵
        if current_section.startswith('wait_'):
            i += 1
            continue

        # 일반 섹션 처리
        if line:
            if current_section == 'intro':
                sections['intro'].append(line)
            elif current_section == 'team_background':
                item = line.lstrip('- ').strip() if line.startswith('-') else line
                sections['team_background'].append(item)
            elif current_section == 'team_direction':
                item = line.lstrip('- ').strip() if line.startswith('-') else line
                sections['team_direction'].append(item)
            elif current_section == 'team_growth':
                item = line.lstrip('- ').strip() if line.startswith('-') else line
                sections['team_growth'].append(item)
            elif current_section == 'team_members':
                item = line.lstrip('- ').strip() if line.startswith('-') else line
                sections['team_members'].append(item)
            elif current_section == 'process':
                if line[0].isdigit() or line[0] in '❶❷❸❹❺':
                    sections['process'].append(line)

        i += 1

    # 마지막 세션 저장
    if current_session > 0 and session_data:
        sections['sessions'][current_session] = session_data

    # 헤드라인 추출 (첫 번째 또는 두 번째 intro가 서브 타이틀이면 합침)
    if sections['intro']:
        # 첫 줄이 짧고 두 번째 줄도 짧으면 둘 다 헤드라인
        if len(sections['intro']) >= 2 and len(sections['intro'][0]) < 30 and len(sections['intro'][1]) < 30:
            sections['headline'] = sections['intro'][0] + '\n' + sections['intro'][1]  # newline으로 구분
            sections['intro'] = sections['intro'][2:]
        else:
            sections['headline'] = sections['intro'][0]
            sections['intro'] = sections['intro'][1:]

    # 각 섹션에서 부제목 질문 제거
    subtitle_questions = ['어떤 계기로 만들어지게 되었나요?', '어떤 방식으로 운영되나요?',
                          '어떤 성장을 기대할 수 있을까요?', '누가 함께 하면 좋을까요?']
    for key in ['team_background', 'team_direction', 'team_growth', 'team_members']:
        sections[key] = [item for item in sections[key] if item not in subtitle_questions]

    return sections


def extract_session_topics_from_plain(content_plain):
    """content_plain에서 세션 주제만 추출 (simple_content용)"""
    topics = {}

    if not content_plain:
        return topics

    # 세션 주제 섹션 찾기
    idx = content_plain.find('세션 주제')
    if idx < 0:
        idx = content_plain.find('3개월 세션')
    if idx < 0:
        return topics

    section = content_plain[idx:idx+3000]
    lines = section.split('\n')

    current_session = 0
    for i, line in enumerate(lines):
        line = line.strip()
        session_match = re.match(r'^(\d)회차$', line)
        if session_match:
            current_session = int(session_match.group(1))
            # 날짜 다음에 오는 줄이 제목
            for j in range(i+1, min(i+6, len(lines))):
                next_line = lines[j].strip()
                # 날짜는 스킵
                if re.match(r'^\d+월\s*\d+일', next_line):
                    continue
                # 빈 줄 스킵
                if not next_line:
                    continue
                # 다음 회차면 이 세션에는 주제가 없음
                if re.match(r'^(\d)회차$', next_line):
                    break
                # 진행방식이면 주제 섹션 종료
                if next_line == '진행방식':
                    break
                # ※로 시작하는 줄은 스킵
                if next_line.startswith('※'):
                    continue
                # 주제 발견
                topics[current_session] = next_line
                break

    return topics


def generate_simple_content(schedule_header, sessions, topics):
    """새로운 형식의 simple_content 생성"""

    session_rows = ""
    for i in range(1, 7):
        date = sessions.get(i, "")
        topic = topics.get(i, "")
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


def generate_list_items(items):
    """리스트 아이템 HTML 생성"""
    html = ""
    for item in items:
        item_escaped = escape(item)
        html += f'''		<li style="margin-bottom:14px; padding-left:6px;">
			<span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">{item_escaped}</span>
		</li>
'''
    return html


def generate_session_html(sessions_data):
    """3개월 세션 주제 HTML 생성"""
    session_html = ""
    for i in range(1, 7):
        session = sessions_data.get(i, {})
        date = session.get('date', '')
        title = session.get('title', '')
        description = session.get('description', '')
        activities = session.get('activities', [])

        # 활동 텍스트 생성
        activities_text = ""
        for activity in activities:
            # ※ 토론: ... 형식을 파싱
            activity = activity.replace('※ ', '')
            if ':' in activity:
                activity_type, activity_desc = activity.split(':', 1)
                activities_text += f'<br><span style="color:#8B0000; font-weight:600;">{escape(activity_type.strip())}</span> {escape(activity_desc.strip())}'

        border_style = 'border-bottom:1px solid #ddd;' if i < 6 else 'border-bottom:2px solid #222;'

        session_html += f'''		<!-- {i}회차 -->
		<div style="display:flex; flex-wrap:wrap; gap:24px; padding:24px 0; {border_style}">
			<div style="flex:0 0 120px;">

				<p style="font-size:14px; font-weight:600; color:#8B0000; margin:0;">{i}회차</p>

				<p style="font-size:15px; font-weight:600; color:#222; margin:4px 0 0 0;">{escape(date)}</p>
			</div>
			<div style="flex:1 1 400px;">

				<p style="font-size:17px; font-weight:700; color:#222; margin:0 0 12px 0;">{escape(title)}</p>

				<p style="font-size:15px; line-height:1.9; color:#444; margin:0 0 16px 0;">{escape(description)}</p>
				<div style="background:#F0EAE2; border-radius:6px; padding:14px 18px;">

					<p style="font-size:14px; line-height:1.8; color:#555; margin:0;">{activities_text}</p>
				</div></div></div>
'''
    return session_html


def generate_full_content(sections, images):
    """새로운 형식의 content 생성"""

    # 기본 이미지 URL들 (이미지가 없는 경우 사용)
    default_images = [
        "https://cdn.imweb.me/upload/S20240629fee25a0bc999e/8fccc84156ecf.png",
        "https://cdn.imweb.me/upload/S20240629fee25a0bc999e/c9119940129cd.png",
        "https://cdn.imweb.me/upload/S20240629fee25a0bc999e/47d7f6eb0efa2.png",
        "https://cdn.imweb.me/upload/S20240629fee25a0bc999e/6583f5d0d0e29.png"
    ]

    # 이미지 선택 (최대 4개)
    gallery_images = images[:4] if len(images) >= 4 else images + default_images[len(images):4]

    # 메인 타이틀 섹션
    headline_raw = sections.get('headline', '')
    # newline을 <br>로 변환한 후 escape 적용
    if '\n' in headline_raw:
        parts = headline_raw.split('\n')
        headline = '<br>'.join(escape(p) for p in parts)
    else:
        headline = escape(headline_raw)
    intro_paragraphs = ""
    for para in sections.get('intro', []):
        intro_paragraphs += f'\n\n\t\t<p style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em; margin:24px 0 0 0;">{escape(para)}</p>'

    # 01~04 섹션
    team_background_items = generate_list_items(sections.get('team_background', []))
    team_direction_items = generate_list_items(sections.get('team_direction', []))
    team_growth_items = generate_list_items(sections.get('team_growth', []))
    team_members_items = generate_list_items(sections.get('team_members', []))

    # 파트너 섹션
    partner_name = escape(sections.get('partner_name', ''))
    partner_desc = escape(sections.get('partner_desc', ''))
    partner_reason = escape(sections.get('partner_reason', ''))

    # 세션 섹션
    sessions_html = generate_session_html(sections.get('sessions', {}))

    # 진행방식 섹션
    process_items = sections.get('process', [])
    process_html = ""
    for idx, item in enumerate(process_items[:3], 1):
        # ❶, ❷, ❸ 제거하고 텍스트만
        item_text = re.sub(r'^[❶❷❸❹❺\d\.]\s*', '', item)
        border_style = 'border-bottom:1px solid #ddd;' if idx < 3 else ''
        process_html += f'''		<div style="padding:24px 0; {border_style}">

			<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">{idx}</span> {escape(item_text)}</p>
		</div>
'''

    html = f'''<!-- ========================================
     HFK 팀 페이지
     ======================================== -->
<!-- 전체 컨테이너 -->
<div style="max-width:900px; margin:0 auto; font-family:'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:#333; letter-spacing:-0.01em;">
	<!-- ========================================
     SECTION: 메인 타이틀
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h1 style="font-size:32px; font-weight:700; color:#8B0000; line-height:1.5; margin:0 0 40px 0; letter-spacing:-0.02em;">{headline}</h1>
{intro_paragraphs}
	</div>
	<!-- // SECTION: 메인 타이틀 -->
	<!-- ========================================
     SECTION: 메인 이미지 갤러리
     ======================================== -->
	<div style="margin-bottom:80px;">
		<div style="display:flex; gap:16px; overflow-x:auto; padding-bottom:16px; scroll-snap-type:x mandatory;">
			<div style="flex:0 0 auto; width:280px; scroll-snap-align:start;"><img src="{gallery_images[0]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" class="fr-fic fr-dii"></div>
			<div style="flex:0 0 auto; width:280px; scroll-snap-align:start;"><img src="{gallery_images[1]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" class="fr-fic fr-dii"></div>
			<div style="flex:0 0 auto; width:280px; scroll-snap-align:start;"><img src="{gallery_images[2]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" class="fr-fic fr-dii"></div>
			<div style="flex:0 0 auto; width:280px; scroll-snap-align:start;"><img src="{gallery_images[3]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" class="fr-fic fr-dii"></div></div>

		<p style="font-size:13px; color:#888; text-align:center; margin:8px 0 0 0;">좌우로 스크롤하여 더 많은 이미지를 확인하세요</p>
	</div>
	<!-- // SECTION: 메인 이미지 갤러리 -->
	<!-- ========================================
     SECTION: 01 팀 배경
     ======================================== -->
	<div style="margin-bottom:80px;">
		<!-- 섹션 헤더 -->
		<div style="margin-bottom:32px;"><span style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em;">01</span>

			<h2 style="font-size:24px; font-weight:700; color:#222; margin:8px 0 4px 0; line-height:1.4;">팀 배경</h2>

			<p style="font-size:17px; color:#555; letter-spacing:-0.01em; margin:0;">어떤 계기로 만들어지게 되었나요?</p>
			<div style="width:100%; height:1px; background:#222; margin-top:20px;"></div></div>
		<!-- 콘텐츠 -->

		<ul style="margin:0; padding:0 0 0 20px; list-style:disc; color:#8B0000;">
{team_background_items}		</ul>
	</div>
	<!-- // SECTION: 01 팀 배경 -->
	<!-- ========================================
     SECTION: 02 팀 운영 방향
     ======================================== -->
	<div style="margin-bottom:80px;">
		<!-- 섹션 헤더 -->
		<div style="margin-bottom:32px;"><span style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em;">02</span>

			<h2 style="font-size:24px; font-weight:700; color:#222; margin:8px 0 4px 0; line-height:1.4;">팀 운영 방향</h2>

			<p style="font-size:17px; color:#555; letter-spacing:-0.01em; margin:0;">어떤 방식으로 운영되나요?</p>
			<div style="width:100%; height:1px; background:#222; margin-top:20px;"></div></div>
		<!-- 콘텐츠 -->

		<ul style="margin:0; padding:0 0 0 20px; list-style:disc; color:#8B0000;">
{team_direction_items}		</ul>
	</div>
	<!-- // SECTION: 02 팀 운영 방향 -->
	<!-- ========================================
     SECTION: 03 팀 성장 포인트
     ======================================== -->
	<div style="margin-bottom:80px;">
		<!-- 섹션 헤더 -->
		<div style="margin-bottom:32px;"><span style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em;">03</span>

			<h2 style="font-size:24px; font-weight:700; color:#222; margin:8px 0 4px 0; line-height:1.4;">팀 성장 포인트</h2>

			<p style="font-size:17px; color:#555; letter-spacing:-0.01em; margin:0;">어떤 성장을 기대할 수 있을까요?</p>
			<div style="width:100%; height:1px; background:#222; margin-top:20px;"></div></div>
		<!-- 콘텐츠 -->

		<ul style="margin:0; padding:0 0 0 20px; list-style:disc; color:#8B0000;">
{team_growth_items}		</ul>
	</div>
	<!-- // SECTION: 03 팀 성장 포인트 -->
	<!-- ========================================
     SECTION: 04 팀 멤버들
     ======================================== -->
	<div style="margin-bottom:80px;">
		<!-- 섹션 헤더 -->
		<div style="margin-bottom:32px;"><span style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em;">04</span>

			<h2 style="font-size:24px; font-weight:700; color:#222; margin:8px 0 4px 0; line-height:1.4;">팀 멤버들</h2>

			<p style="font-size:17px; color:#555; letter-spacing:-0.01em; margin:0;">누가 함께 하면 좋을까요?</p>
			<div style="width:100%; height:1px; background:#222; margin-top:20px;"></div></div>
		<!-- 콘텐츠 -->

		<ul style="margin:0; padding:0 0 0 20px; list-style:disc; color:#8B0000;">
{team_members_items}		</ul>
	</div>
	<!-- // SECTION: 04 팀 멤버들 -->
	<!-- ========================================
     SECTION: 파트너 소개
     ======================================== -->
	<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px; margin-bottom:80px;">

		<p style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em; margin:0 0 8px 0;">PARTNER</p>

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">파트너 소개</h2>

		<h3 style="font-size:22px; font-weight:700; color:#222; margin:0 0 16px 0;">{partner_name}</h3>

		<p style="font-size:16px; line-height:1.75; color:#444; margin:0 0 32px 0;">{partner_desc}</p>
		<div style="background:#fff; border-radius:8px; padding:24px 28px;">

			<p style="font-size:15px; font-weight:600; color:#8B0000; margin:0 0 10px 0;">HFK가 {partner_name}님과 이 팀을 기획한 이유</p>

			<p style="font-size:15px; line-height:1.9; color:#555; margin:0;">{partner_reason}</p>
		</div></div>
	<!-- // SECTION: 파트너 소개 -->
	<!-- ========================================
     SECTION: 3개월 세션 주제
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">3개월 세션 주제</h2>
		<div style="border-top:2px solid #222;">
{sessions_html}		</div></div>
	<!-- // SECTION: 3개월 세션 주제 -->
	<!-- ========================================
     SECTION: 진행방식
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">진행방식</h2>
		<div style="border-top:2px solid #222; border-bottom:2px solid #222;">
{process_html}		</div></div>
	<!-- // SECTION: 진행방식 -->
	<!-- ========================================
     SECTION: 그라운드룰
     ======================================== -->
	<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px; margin-bottom:80px;">
		<div style="display:flex; flex-wrap:wrap; gap:48px; align-items:flex-start;">
			<div style="flex:1 1 280px; min-width:250px;">

				<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 14px 0;">그라운드룰</h2>

				<p style="font-size:15px; line-height:1.8; color:#8B0000; font-weight:500; margin:0;">다양한 산업, 직무, 연차가 모이는 HFK에서는
					<br>서로의 성장을 위해 그라운드룰을 꼭 명심해주세요.</p>
			</div>
			<div style="flex:1 1 350px; min-width:300px;">
				<div style="background:#fff; border-radius:12px; padding:28px; border:1px solid #e5e5e5;">
					<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">호칭</span> <span style="font-size:15px; color:#555; margin-left:12px;">서로 &#39;님&#39;으로 부릅니다.</span></div>
					<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">존중</span> <span style="font-size:15px; color:#555; margin-left:12px;">서로의 의견과 취향을 존중합니다.</span></div>
					<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">환대</span> <span style="font-size:15px; color:#555; margin-left:12px;">새로운 멤버를 반갑게 맞이합니다.</span></div>
					<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">약속</span> <span style="font-size:15px; color:#555; margin-left:12px;">과제를 충실히 합니다.</span></div>
					<div><span style="font-size:15px; font-weight:700; color:#222;">기록</span> <span style="font-size:15px; color:#555; margin-left:12px;">모임에서 배운 것을 4L로 정리합니다.</span>

						<p style="font-size:13px; color:#888; margin:4px 0 0 44px;">(Liked, Learned, Lacked, Long for)</p>
					</div></div></div></div></div>
	<!-- // SECTION: 그라운드룰 -->
	<!-- ========================================
     SECTION: 이벤트
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 8px 0;">이벤트</h2>

		<p style="font-size:15px; font-weight:500; color:#8B0000; margin:0 0 32px 0;">모든 시즌 멤버들이 신청할 수 있습니다</p>
		<div style="border-top:2px solid #222; border-bottom:2px solid #222;">
			<div style="padding:24px 0; border-bottom:1px solid #ddd;">

				<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">1</span> <strong>PEST브리핑</strong>
					<br><span style="margin-left:36px; display:inline-block;"><strong>12월 17일 (수)</strong> 정치/경제/사회문화/기술 4개 영역의 <strong style="color:#8B0000;">주요 뉴스와 시사점</strong>을 공유합니다.</span></p>
			</div>
			<div style="padding:24px 0; border-bottom:1px solid #ddd;">

				<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">2</span> <strong>AAR 밋업 (After Action Review)</strong>
					<br><span style="margin-left:36px; display:inline-block;"><strong>1월 21일 (수)</strong> 다른 사람은 어떻게 일하는지 궁금하신가요? HFK 멤버가 최근 진행한 <strong style="color:#8B0000;">실무 프로젝트의 진행 과정과 고민점, 회고</strong>를 나눕니다.</span></p>
			</div>
			<div style="padding:24px 0; border-bottom:1px solid #ddd;">

				<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">3</span> <strong>HBR 포럼</strong>
					<br><span style="margin-left:36px; display:inline-block;"><strong>2월 25일 (수)</strong> 지금 꼭 읽어둬야 할 <strong style="color:#8B0000;">최신 HBR 아티클과 업무 인사이트</strong>를 소개합니다.</span></p>
			</div>
			<div style="padding:24px 0;">

				<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">4</span> <strong>저자 북토크</strong>
					<br><span style="margin-left:36px; display:inline-block;">지금 우리에게 필요한 <strong style="color:#8B0000;">인사이트를 저자에게 직접 듣고 질의 응답</strong>을 나눕니다. 저자 북토크는 2~3주 전 HFK 슬랙에 일시장소가 공지됩니다.</span></p>
			</div></div></div>
	<!-- // SECTION: 이벤트 -->
	<!-- ========================================
     SECTION: 멤버십 베네핏
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 36px 0;">멤버십 베네핏</h2>
		<div style="display:flex; flex-wrap:wrap; gap:28px;">
			<!-- 01 -->
			<div style="flex:1 1 200px; min-width:200px;">

				<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">01</p>

				<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">비즈니스
					<br>매거진</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/4a058c9e78d51.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

				<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">HFK 멤버는 하버드 비즈니스 리뷰(HBR) 한국 커뮤니티의 일원이기도 합니다. 모든 멤버에게 최신 HBR 1권을 선물로 드립니다. (정가 2.5만원)</p>
			</div>
			<!-- 02 -->
			<div style="flex:1 1 200px; min-width:200px;">

				<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">02</p>

				<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">사색의 시간과
					<br>와인</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/fdeabe924dbc2.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

				<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">도심 속 사색을 즐길 수 있는 마이시크릿덴과 소정동 이용 할인을 제공합니다. (마이시크릿덴 낮 이용권 1회, 밤 글래스 와인 50% 할인, 바틀 10% 할인, 소정동 공간비 1회 50% 할인)</p>
			</div>
			<!-- 03 -->
			<div style="flex:1 1 200px; min-width:200px;">

				<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">03</p>

				<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">느슨하지만 꾸준한
					<br>네트워크</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/7d5f649085b57.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

				<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">재등록 멤버에게는 20만원 할인 혜택을 드리고, 멤버만의 관심사별 소모임(미식, 운동, 독서 등)인 클럽에도 참여할 수 있습니다.</p>
			</div>
			<!-- 04 -->
			<div style="flex:1 1 200px; min-width:200px;">

				<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">04</p>

				<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">현업에 도움되는
					<br>컨텐츠</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/886c0c55ab875.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

				<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">폴인은 일에 진심인 사람들을 위한 콘텐츠 구독 서비스로 많은 HFK 멤버가 소개된 곳이기도 합니다. 등록하신 모든 멤버에게 폴인 Plus 3개월 이용권이 제공됩니다.</p>
			</div></div></div>
	<!-- // SECTION: 멤버십 베네핏 -->
	<!-- ========================================
     SECTION: FAQ
     ======================================== -->
	<div style="margin-bottom:80px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 36px 0;">등록 전 많이
			<br>물어보시는 질문</h2>
		<div style="margin-bottom:32px;">

			<h3 style="font-size:16px; font-weight:700; color:#222; margin:0 0 14px 0;">팀별 멤버들의 산업, 직무, 연차가 어떻게 되나요</h3>

			<p style="font-size:15px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">20대 후반의 1년차부터 50대 초반의 2N년차까지 다양한 산업, 직무, 연차의 멤버들이 참여 중 입니다. 주로 대기업/외국계기업 8-10년차 직장인이 많은 편입니다. &#39;내가 가도 괜찮을까..?&#39; 라는 고민은 직무/연차와 무관하게 모든 멤버들이 한번쯤 해보는 고민입니다. 자신의 영역(Comfort zone)을 벗어나 다양한 산업과 직무에 종사하는 멤버들과 서로의 생각을 나누면 정체되어 있던 성장이 다시 시작됩니다.</p>
		</div>
		<div>

			<h3 style="font-size:16px; font-weight:700; color:#222; margin:0 0 14px 0;">회사 교육비로 결제 가능한가요</h3>

			<p style="font-size:15px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">가능합니다. 먼저 HFK 이메일 info@hbrforum.org로 사업자 등록증을 전달해주신 후, 채널톡을 남겨주세요. 채널톡 확인 후, HFK(위어드벤처)에서 세금계산서 발행해 드리고, 멤버십 쿠폰코드를 이메일로 보내드립니다. 메일로 받으신 쿠폰코드는 등록하실 팀 상세페이지의 [멤버십 등록하기] 버튼을 누르고, 결제 페이지 상단에서 입력 가능합니다. 무료 등록이 완료되면 멤버십 등록도 완료됩니다.</p>
		</div></div>
	<!-- // SECTION: FAQ -->
	<!-- ========================================
     SECTION: 첫 세션까지 진행 과정
     ======================================== -->
	<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px;">

		<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 14px 0;">첫 세션까지 진행 과정</h2>

		<p style="font-size:15px; font-weight:500; color:#8B0000; line-height:1.8; margin:0 0 8px 0;">봄 시즌은 아래의 순서로 진행됩니다. 신청 전 꼼꼼히 읽어주시기 바랍니다.
			<br>
			<br>
		</p>
		<div style="background:#fff; border-radius:12px; padding:36px; border:1px solid #e5e5e5;">
			<!-- Step 1 -->
			<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

				<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 1.</span> 시즌 등록 마감</p>

				<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">2월 25일 (화) 자정에 등록이 마감됩니다.
					<br>2월 28일 (토)에 가입 시 입력했던 이메일로 HFK 슬랙에 초대드립니다.
					<br>3월 2일 (일) 21시에 첫 봄시즌 공지가 전달됩니다. 미리 이메일을 확인해 HFK 슬랙에 가입해주세요.</p>
			</div>
			<!-- Step 2 -->
			<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

				<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 2.</span> 시즌 첫 공지 및 자기소개 미션</p>

				<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">3월 2일(일) 21시에 등록한 모든 멤버에게 HFK 슬랙으로 전체 공지(시즌 레터), 팀별 공지, 자기소개 미션이 전달됩니다.
					<br>전체 공지와 팀별 공지는 시즌 기간 동안 매주 일요일 밤 아홉 시에 안내됩니다.
					<br>첫 세션 이전까지 자기소개 미션을 꼭 마쳐주세요.</p>
			</div>
			<!-- Step 3 -->
			<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

				<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 3.</span> 뉴멤버 오리엔테이션</p>

				<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">3월 5일 (수), 3월 6일 (목) 오아시스 덕수궁에서 양일간 동일한 내용으로 뉴멤버 오리엔테이션이 진행됩니다.
					<br>멤버십 구성, HFK 슬랙 사용법을 안내드리고, 뉴멤버 네트워킹 시간도 준비되어 있습니다.
					<br>양일 모두 같은 내용을 진행하므로 가능한 일정에 참석해주세요.
					<br>HFK가 처음이시라면 꼭 함께 해주세요.</p>
			</div>
			<!-- Step 4 -->
			<div>

				<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 4.</span> 팀별 첫 세션</p>

				<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">3월 8일(토)부터 각 팀의 1회차 세션이 시작됩니다.
					<br>멤버와 파트너가 서로 인사하고, 준비된 내용을 바탕으로 세션이 진행됩니다.
					<br>자기소개를 위해 명함을 챙겨와주세요.</p>
			</div></div></div>
	<!-- // SECTION: 첫 세션까지 진행 과정 -->
</div>
<!-- // 전체 컨테이너 -->'''

    return html


def convert_product(client, product_no, dry_run=True):
    """상품 content와 simple_content를 변환하고 업데이트"""
    print(f"\n{'='*60}")
    print(f"상품 번호: {product_no}")
    print(f"{'='*60}")

    # 상품 상세 조회
    detail = client.get_product_detail(str(product_no))
    if 'error' in detail:
        print(f"상품 조회 실패: {detail['error']}")
        return False

    product_data = detail.get('data', {})
    name = product_data.get('name', 'unknown')
    content = product_data.get('content', '')
    simple_content = product_data.get('simple_content', '')
    content_plain = product_data.get('content_plain', '')

    print(f"상품명: {name}")
    print(f"Content 길이: {len(content)}")
    print(f"Simple Content 길이: {len(simple_content)}")
    print(f"Content Plain 길이: {len(content_plain)}")

    if not content_plain:
        print("content_plain이 비어있습니다. 스킵합니다.")
        return False

    # 이미지 추출
    images = extract_images_from_content(content)
    print(f"추출된 이미지 수: {len(images)}")

    # 섹션 추출
    sections = extract_content_sections(content_plain)
    print(f"헤드라인: {sections['headline'][:50]}..." if sections['headline'] else "헤드라인 없음")
    print(f"파트너: {sections['partner_name']}")
    print(f"세션 수: {len(sections['sessions'])}")

    # 일정 정보 추출 (simple_content용)
    schedule_header, sessions = extract_schedule_info(simple_content)
    topics = extract_session_topics_from_plain(content_plain)
    print(f"일정 헤더: {schedule_header}")
    print(f"세션 날짜: {sessions}")
    print(f"세션 주제: {topics}")

    if not sections['headline']:
        print("필수 정보가 부족합니다. 스킵합니다.")
        return False

    # 새 콘텐츠 생성
    new_content = generate_full_content(sections, images)
    new_simple_content = generate_simple_content(schedule_header, sessions, topics) if schedule_header else simple_content

    # 미리보기 저장
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    preview_content_file = os.path.join(data_dir, f"preview_{product_no}_{name}_content.html")
    with open(preview_content_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Content 미리보기 저장: {preview_content_file}")

    preview_simple_file = os.path.join(data_dir, f"preview_{product_no}_{name}_simple.html")
    with open(preview_simple_file, 'w', encoding='utf-8') as f:
        f.write(new_simple_content)
    print(f"Simple Content 미리보기 저장: {preview_simple_file}")

    if dry_run:
        print("DRY RUN 모드 - 실제 업데이트하지 않음")
        return True

    # 실제 업데이트
    update_data = {
        'content': new_content,
        'simple_content': new_simple_content
    }

    result = client.update_product(str(product_no), update_data)
    if result.get('code') == 200:
        print(f"상품 업데이트 성공: {name}")
        return True
    else:
        print(f"상품 업데이트 실패: {result}")
        return False


def main():
    """메인 함수"""
    client = ImwebAPI(API_KEY, API_SECRET)

    # 26봄주중 카테고리 ID
    cat_weekday = 's2026012319995240b6e87'
    # 26봄주말 카테고리 ID
    cat_weekend = 's2026012311f5fb372b835'

    # 카테고리별 상품 목록 조회
    product_nos = []

    import time

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
    else:
        print(f"  API 응답 오류: {weekday_products}")

    # API 호출 간 대기
    time.sleep(1)

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
    else:
        print(f"  API 응답 오류: {weekend_products}")

    if not product_nos:
        print("\n조회된 상품이 없습니다.")
        return

    print(f"\n총 {len(product_nos)}개 상품을 변환합니다.")

    # dry_run=True로 먼저 테스트
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("실제 업데이트 모드로 실행합니다!")

    success_count = 0
    fail_count = 0

    for product_no in product_nos:
        try:
            if convert_product(client, product_no, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"완료: 성공 {success_count}개, 실패 {fail_count}개")

    if dry_run:
        print("\n실제 업데이트를 하려면 --execute 옵션을 추가하세요:")
        print("   python scripts/convert_26spring_full_content.py --execute")


if __name__ == "__main__":
    main()
