#!/usr/bin/env python3
"""
아임웹 상품 content를 새로운 형식으로 변환하는 스크립트
- 텍스트 내용은 유지하면서 HTML 형식만 변경
- 색상 테마: #980000 → #8B0000
- 배경색: #F0E6DB → #F5EBE0
"""

import sys
import os
import re
import json
from bs4 import BeautifulSoup
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI
from dotenv import load_dotenv

load_dotenv()


def extract_text_content(html_content, preserve_breaks=False):
    """HTML에서 텍스트 내용 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')

    if preserve_breaks:
        # <br> 태그를 특수 마커로 변환
        for br in soup.find_all('br'):
            br.replace_with('|||BREAK|||')
        text = soup.get_text()
        text = text.replace('|||BREAK|||', '\n')
    else:
        text = soup.get_text()

    # 엔티티 디코딩
    text = unescape(text)
    return text.strip()


def extract_section_content(soup, section_num):
    """특정 섹션의 내용 추출 (01~04)"""
    # 섹션 번호로 시작하는 요소 찾기
    section_patterns = [f"0{section_num}", f"{section_num:02d}"]

    for element in soup.find_all(['span', 'div']):
        text = element.get_text().strip()
        for pattern in section_patterns:
            if text.startswith(pattern):
                # 부모 요소에서 전체 섹션 찾기
                parent = element.find_parent('div', style=lambda x: x and 'margin-bottom' in str(x))
                if parent:
                    # 본문 내용 찾기
                    content_div = parent.find('div', style=lambda x: x and 'line-height:2' in str(x))
                    if content_div:
                        return extract_text_content(str(content_div), preserve_breaks=True)
    return ""


def extract_partner_info(soup):
    """파트너 정보 추출"""
    partner_wrap = soup.find('div', id='partnerWrap')
    if not partner_wrap:
        partner_wrap = soup.find('div', style=lambda x: x and 'F0E6DB' in str(x).upper())

    if partner_wrap:
        # 파트너 이름
        name_elem = partner_wrap.find('strong', string=lambda x: x and len(x) < 10 and '파트너' not in str(x))
        if not name_elem:
            for strong in partner_wrap.find_all('strong'):
                text = strong.get_text().strip()
                if text and len(text) < 10 and '파트너' not in text and 'HFK' not in text:
                    name_elem = strong
                    break

        partner_name = name_elem.get_text().strip() if name_elem else ""

        # 파트너 소개 텍스트들
        intro_texts = []
        hfk_reason = ""

        for div in partner_wrap.find_all('div', style=lambda x: x and 'padding' in str(x)):
            text = extract_text_content(str(div))
            if text and len(text) > 20:
                if 'HFK가' in text and '이유' in text:
                    hfk_reason = text
                elif partner_name not in text and '파트너 소개' not in text:
                    intro_texts.append(text)

        return {
            'name': partner_name,
            'intro': '\n\n'.join(intro_texts),
            'hfk_reason': hfk_reason
        }
    return {'name': '', 'intro': '', 'hfk_reason': ''}


def extract_sessions(soup):
    """세션 정보 추출"""
    sessions = []

    # 회차 정보 찾기
    for i in range(1, 7):
        pattern = f"{i}회차"
        for elem in soup.find_all(['strong', 'span']):
            if pattern in elem.get_text():
                parent = elem.find_parent('div', style=lambda x: x and 'flex' in str(x))
                if parent:
                    # 날짜 찾기
                    date_match = re.search(r'\d+월\s*\d+일\s*\([일월화수목금토]\)', parent.get_text())
                    date = date_match.group(0) if date_match else ""

                    # 세션 내용 찾기
                    content_div = parent.find('div', style=lambda x: x and 'flex: 1 1' in str(x))
                    content = extract_text_content(str(content_div)) if content_div else ""

                    # 제목과 설명 분리
                    lines = content.split('\n')
                    title = ""
                    description = ""
                    for line in lines:
                        line = line.strip()
                        if line and not any(x in line for x in ['회차', date]):
                            if not title:
                                title = line
                            else:
                                description += line + " "

                    sessions.append({
                        'num': i,
                        'date': date,
                        'title': title.strip(),
                        'description': description.strip()
                    })
                    break
    return sessions


def extract_main_title_and_intro(soup):
    """메인 타이틀과 소개글 추출"""
    # 첫 번째 큰 텍스트 (타이틀)
    title = ""
    intro_paragraphs = []

    first_p = soup.find('p')
    if first_p:
        strong = first_p.find('strong')
        if strong:
            # 타이틀에서 줄바꿈 유지
            title = extract_text_content(str(strong), preserve_breaks=True)
            title = title.replace('\n', '<br>')

    # 소개글 (두 번째 p 태그 - 01 섹션 전까지의 본문)
    found_title = False
    for p in soup.find_all('p'):
        # 타이틀을 포함한 p는 스킵
        p_text = p.get_text().strip()

        if not found_title:
            if title and title.replace('<br>', '\n').split('\n')[0] in p_text:
                found_title = True
                continue
            continue

        # 01 섹션 이전까지만
        if '01' in p_text and '팀 배경' in p_text:
            break

        # 빈 p 태그 스킵
        if not p_text or len(p_text) < 20:
            continue

        # 그라운드룰, FAQ 등 공통 섹션 내용 제외
        if any(keyword in p_text for keyword in ['그라운드룰', '등록 전 많이', '첫 세션까지', '멤버십 베네핏', '이벤트', '진행방식']):
            break

        # line-height 스타일이 있는 본문 텍스트
        style = p.get('style', '')
        if 'line-height' in style:
            text = extract_text_content(str(p), preserve_breaks=True)
            # 줄바꿈으로 분리된 문단들
            paragraphs = [para.strip() for para in text.split('\n\n') if para.strip() and len(para.strip()) > 20]
            intro_paragraphs.extend(paragraphs)

            if len(intro_paragraphs) >= 4:
                break

    # 최대 4개 문단만 사용
    return title, intro_paragraphs[:4]


def extract_images(soup):
    """이미지 URL 추출"""
    images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and 'cdn.imweb.me' in src:
            images.append(src)
    return images[:4]  # 최대 4개


def extract_section_items(soup, section_num):
    """섹션의 리스트 아이템 추출"""
    items = []
    section_text = extract_section_content(soup, section_num)

    if section_text:
        # 줄바꿈으로 분리
        lines = section_text.replace('\n\n', '\n').split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                items.append(line)

    return items


def generate_new_format(data):
    """새로운 형식의 HTML 생성"""

    title = data.get('title', '')
    intro = data.get('intro', [])
    images = data.get('images', [])
    sections = data.get('sections', {})
    partner = data.get('partner', {})
    session_list = data.get('sessions', [])

    # 이미지 갤러리 HTML
    image_gallery = ""
    if images:
        image_items = ""
        for img_url in images:
            image_items += f'''<div style="flex:0 0 auto; width:280px; scroll-snap-align:start;"><img src="{img_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" class="fr-fic fr-dii"></div>\n\t\t\t'''

        image_gallery = f'''<!-- ========================================
     SECTION: 메인 이미지 갤러리
     ======================================== -->
\t<div style="margin-bottom:80px;">
\t\t<div style="display:flex; gap:16px; overflow-x:auto; padding-bottom:16px; scroll-snap-type:x mandatory;">
\t\t\t{image_items.strip()}</div>

\t\t<p style="font-size:13px; color:#888; text-align:center; margin:8px 0 0 0;">좌우로 스크롤하여 더 많은 이미지를 확인하세요</p>
\t</div>
\t<!-- // SECTION: 메인 이미지 갤러리 -->'''

    # 섹션 01~04 HTML 생성
    section_titles = {
        1: ('팀 배경', '어떤 계기로 만들어지게 되었나요?'),
        2: ('팀 운영 방향', '어떤 방식으로 운영되나요?'),
        3: ('팀 성장 포인트', '어떤 성장을 기대할 수 있을까요?'),
        4: ('팀 멤버들', '누가 함께 하면 좋을까요?')
    }

    sections_html = ""
    for num in range(1, 5):
        section_title, section_subtitle = section_titles[num]
        items = sections.get(num, [])

        list_items = ""
        for item in items:
            list_items += f'''\t\t\t<li style="margin-bottom:14px; padding-left:6px;">
\t\t\t\t<span style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em;">{item}</span>
\t\t\t</li>\n'''

        sections_html += f'''<!-- ========================================
     SECTION: 0{num} {section_title}
     ======================================== -->
\t<div style="margin-bottom:80px;">
\t\t<!-- 섹션 헤더 -->
\t\t<div style="margin-bottom:32px;"><span style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em;">0{num}</span>

\t\t\t<h2 style="font-size:24px; font-weight:700; color:#222; margin:8px 0 4px 0; line-height:1.4;">{section_title}</h2>

\t\t\t<p style="font-size:17px; color:#555; letter-spacing:-0.01em; margin:0;">{section_subtitle}</p>
\t\t\t<div style="width:100%; height:1px; background:#222; margin-top:20px;"></div></div>
\t\t<!-- 콘텐츠 -->

\t\t<ul style="margin:0; padding:0 0 0 20px; list-style:disc; color:#8B0000;">
{list_items}\t\t</ul>
\t</div>
\t<!-- // SECTION: 0{num} {section_title} -->
\t'''

    # 파트너 소개 HTML
    partner_html = ""
    if partner.get('name'):
        hfk_reason_html = ""
        if partner.get('hfk_reason'):
            hfk_reason_html = f'''<div style="background:#fff; border-radius:8px; padding:24px 28px;">

\t\t\t<p style="font-size:15px; font-weight:600; color:#8B0000; margin:0 0 10px 0;">HFK가 {partner['name'].split()[0]}님과 이 팀을 기획한 이유</p>

\t\t\t<p style="font-size:15px; line-height:1.9; color:#555; margin:0;">{partner.get('hfk_reason', '').replace('HFK가', '').split('이유')[-1].strip()}</p>
\t\t</div>'''

        partner_html = f'''<!-- ========================================
     SECTION: 파트너 소개
     ======================================== -->
\t<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px; margin-bottom:80px;">

\t\t<p style="font-size:14px; font-weight:600; color:#8B0000; letter-spacing:0.05em; margin:0 0 8px 0;">PARTNER</p>

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">파트너 소개</h2>

\t\t<h3 style="font-size:22px; font-weight:700; color:#222; margin:0 0 16px 0;">{partner.get('name', '')}</h3>

\t\t<p style="font-size:16px; line-height:1.75; color:#444; margin:0 0 32px 0;">{partner.get('intro', '')}</p>
\t\t{hfk_reason_html}</div>
\t<!-- // SECTION: 파트너 소개 -->
\t'''

    # 세션 주제 HTML
    session_items = ""
    for i, session in enumerate(session_list):
        border_style = 'border-bottom:1px solid #ddd;' if i < len(session_list) - 1 else 'border-bottom:2px solid #222;'

        session_items += f'''<!-- {session['num']}회차 -->
\t\t\t<div style="display:flex; flex-wrap:wrap; gap:24px; padding:24px 0; {border_style}">
\t\t\t\t<div style="flex:0 0 120px;">

\t\t\t\t\t<p style="font-size:14px; font-weight:600; color:#8B0000; margin:0;">{session['num']}회차</p>

\t\t\t\t\t<p style="font-size:15px; font-weight:600; color:#222; margin:4px 0 0 0;">{session['date']}</p>
\t\t\t\t</div>
\t\t\t\t<div style="flex:1 1 400px;">

\t\t\t\t\t<p style="font-size:17px; font-weight:700; color:#222; margin:0 0 12px 0;">{session['title']}</p>

\t\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;">{session['description']}</p>
\t\t\t\t</div></div>
\t\t\t'''

    sessions_html = f'''<!-- ========================================
     SECTION: 3개월 세션 주제
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">3개월 세션 주제</h2>
\t\t<div style="border-top:2px solid #222;">
\t\t\t{session_items}
\t\t</div></div>
\t<!-- // SECTION: 3개월 세션 주제 -->
\t''' if session_list else ""

    # 진행방식 HTML (공통)
    process_html = '''<!-- ========================================
     SECTION: 진행방식
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 32px 0;">진행방식</h2>
\t\t<div style="border-top:2px solid #222; border-bottom:2px solid #222;">
\t\t\t<div style="padding:24px 0; border-bottom:1px solid #ddd;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">1</span> 최대 15명의 멤버들에게 파트너가 준비한 발표를 전달합니다.</p>
\t\t\t</div>
\t\t\t<div style="padding:24px 0; border-bottom:1px solid #ddd;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">2</span> 매회 4L 관점(Liked, Learned, Lacked, Long for)으로 회고를 하고 마칩니다.</p>
\t\t\t</div>
\t\t\t<div style="padding:24px 0;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">3</span> 지난 회차 리캡(Recap) &rarr; 파트너의 발표 &rarr; 파트너의 어젠더에 바탕한 디스커션 &rarr; 4L 회고 순으로 진행됩니다.</p>
\t\t\t</div></div></div>
\t<!-- // SECTION: 진행방식 -->
\t'''

    # 그라운드룰 HTML (공통)
    groundrule_html = '''<!-- ========================================
     SECTION: 그라운드룰
     ======================================== -->
\t<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px; margin-bottom:80px;">
\t\t<div style="display:flex; flex-wrap:wrap; gap:48px; align-items:flex-start;">
\t\t\t<div style="flex:1 1 280px; min-width:250px;">

\t\t\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 14px 0;">그라운드룰</h2>

\t\t\t\t<p style="font-size:15px; line-height:1.8; color:#8B0000; font-weight:500; margin:0;">다양한 산업, 직무, 연차가 모이는 HFK에서는
\t\t\t\t\t<br>서로의 성장을 위해 그라운드룰을 꼭 명심해주세요.</p>
\t\t\t</div>
\t\t\t<div style="flex:1 1 350px; min-width:300px;">
\t\t\t\t<div style="background:#fff; border-radius:12px; padding:28px; border:1px solid #e5e5e5;">
\t\t\t\t\t<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">호칭</span> <span style="font-size:15px; color:#555; margin-left:12px;">서로 \'님\'으로 부릅니다.</span></div>
\t\t\t\t\t<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">존중</span> <span style="font-size:15px; color:#555; margin-left:12px;">서로의 의견과 취향을 존중합니다.</span></div>
\t\t\t\t\t<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">환대</span> <span style="font-size:15px; color:#555; margin-left:12px;">새로운 멤버를 반갑게 맞이합니다.</span></div>
\t\t\t\t\t<div style="margin-bottom:18px;"><span style="font-size:15px; font-weight:700; color:#222;">약속</span> <span style="font-size:15px; color:#555; margin-left:12px;">과제를 충실히 합니다.</span></div>
\t\t\t\t\t<div><span style="font-size:15px; font-weight:700; color:#222;">기록</span> <span style="font-size:15px; color:#555; margin-left:12px;">모임에서 배운 것을 4L로 정리합니다.</span>

\t\t\t\t\t\t<p style="font-size:13px; color:#888; margin:4px 0 0 44px;">(Liked, Learned, Lacked, Long for)</p>
\t\t\t\t\t</div></div></div></div></div>
\t<!-- // SECTION: 그라운드룰 -->
\t'''

    # 이벤트 HTML (공통)
    event_html = '''<!-- ========================================
     SECTION: 이벤트
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 8px 0;">이벤트</h2>

\t\t<p style="font-size:15px; font-weight:500; color:#8B0000; margin:0 0 32px 0;">모든 시즌 멤버들이 신청할 수 있습니다</p>
\t\t<div style="border-top:2px solid #222; border-bottom:2px solid #222;">
\t\t\t<div style="padding:24px 0; border-bottom:1px solid #ddd;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">1</span> <strong>PEST브리핑</strong>
\t\t\t\t\t<br><span style="margin-left:36px; display:inline-block;"><strong>4월 16일 (수)</strong> 정치/경제/사회문화/기술 4개 영역의 <strong style="color:#8B0000;">주요 뉴스와 시사점</strong>을 공유합니다.</span></p>
\t\t\t</div>
\t\t\t<div style="padding:24px 0; border-bottom:1px solid #ddd;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">2</span> <strong>AAR 밋업 (After Action Review)</strong>
\t\t\t\t\t<br><span style="margin-left:36px; display:inline-block;"><strong>5월 21일 (수)</strong> 다른 사람은 어떻게 일하는지 궁금하신가요? HFK 멤버가 최근 진행한 <strong style="color:#8B0000;">실무 프로젝트의 진행 과정과 고민점, 회고</strong>를 나눕니다.</span></p>
\t\t\t</div>
\t\t\t<div style="padding:24px 0; border-bottom:1px solid #ddd;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">3</span> <strong>HBR 포럼</strong>
\t\t\t\t\t<br><span style="margin-left:36px; display:inline-block;"><strong>6월 25일 (수)</strong> 지금 꼭 읽어둬야 할 <strong style="color:#8B0000;">최신 HBR 아티클과 업무 인사이트</strong>를 소개합니다.</span></p>
\t\t\t</div>
\t\t\t<div style="padding:24px 0;">

\t\t\t\t<p style="font-size:15px; line-height:1.9; color:#444; margin:0;"><span style="display:inline-block; width:24px; height:24px; background:#8B0000; color:#fff; border-radius:50%; text-align:center; line-height:24px; font-size:13px; font-weight:600; margin-right:12px;">4</span> <strong>저자 북토크</strong>
\t\t\t\t\t<br><span style="margin-left:36px; display:inline-block;">지금 우리에게 필요한 <strong style="color:#8B0000;">인사이트를 저자에게 직접 듣고 질의 응답</strong>을 나눕니다. 저자 북토크는 2~3주 전 HFK 슬랙에 일시장소가 공지됩니다.</span></p>
\t\t\t</div></div></div>
\t<!-- // SECTION: 이벤트 -->
\t'''

    # 멤버십 베네핏 HTML (공통)
    benefit_html = '''<!-- ========================================
     SECTION: 멤버십 베네핏
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 36px 0;">멤버십 베네핏</h2>
\t\t<div style="display:flex; flex-wrap:wrap; gap:28px;">
\t\t\t<!-- 01 -->
\t\t\t<div style="flex:1 1 200px; min-width:200px;">

\t\t\t\t<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">01</p>

\t\t\t\t<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">비즈니스
\t\t\t\t\t<br>매거진</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/4a058c9e78d51.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

\t\t\t\t<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">HFK 멤버는 하버드 비즈니스 리뷰(HBR) 한국 커뮤니티의 일원이기도 합니다. 모든 멤버에게 최신 HBR 1권을 선물로 드립니다. (정가 2.5만원)</p>
\t\t\t</div>
\t\t\t<!-- 02 -->
\t\t\t<div style="flex:1 1 200px; min-width:200px;">

\t\t\t\t<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">02</p>

\t\t\t\t<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">사색의 시간과
\t\t\t\t\t<br>와인</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/fdeabe924dbc2.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

\t\t\t\t<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">도심 속 사색을 즐길 수 있는 마이시크릿덴과 소정동 이용 할인을 제공합니다. (마이시크릿덴 낮 이용권 1회, 밤 글래스 와인 50% 할인, 바틀 10% 할인, 소정동 공간비 1회 50% 할인)</p>
\t\t\t</div>
\t\t\t<!-- 03 -->
\t\t\t<div style="flex:1 1 200px; min-width:200px;">

\t\t\t\t<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">03</p>

\t\t\t\t<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">느슨하지만 꾸준한
\t\t\t\t\t<br>네트워크</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/7d5f649085b57.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

\t\t\t\t<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">재등록 멤버에게는 20만원 할인 혜택을 드리고, 멤버만의 관심사별 소모임(미식, 운동, 독서 등)인 클럽에도 참여할 수 있습니다.</p>
\t\t\t</div>
\t\t\t<!-- 04 -->
\t\t\t<div style="flex:1 1 200px; min-width:200px;">

\t\t\t\t<p style="font-size:13px; font-weight:600; color:#8B0000; margin:0;">04</p>

\t\t\t\t<h3 style="font-size:18px; font-weight:700; color:#222; margin:8px 0 16px 0; line-height:1.4;">현업에 도움되는
\t\t\t\t\t<br>컨텐츠</h3><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/886c0c55ab875.png" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom:16px;" class="fr-fic fr-dii">

\t\t\t\t<p style="font-size:14px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">폴인은 일에 진심인 사람들을 위한 콘텐츠 구독 서비스로 많은 HFK 멤버가 소개된 곳이기도 합니다. 등록하신 모든 멤버에게 폴인 Plus 3개월 이용권이 제공됩니다.</p>
\t\t\t</div></div></div>
\t<!-- // SECTION: 멤버십 베네핏 -->
\t'''

    # FAQ HTML (공통)
    faq_html = '''<!-- ========================================
     SECTION: FAQ
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 36px 0;">등록 전 많이
\t\t\t<br>물어보시는 질문</h2>
\t\t<div style="margin-bottom:32px;">

\t\t\t<h3 style="font-size:16px; font-weight:700; color:#222; margin:0 0 14px 0;">팀별 멤버들의 산업, 직무, 연차가 어떻게 되나요</h3>

\t\t\t<p style="font-size:15px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">20대 후반의 1년차부터 50대 초반의 2N년차까지 다양한 산업, 직무, 연차의 멤버들이 참여 중 입니다. 주로 대기업/외국계기업 8-10년차 직장인이 많은 편입니다. \'내가 가도 괜찮을까..?\' 라는 고민은 직무/연차와 무관하게 모든 멤버들이 한번쯤 해보는 고민입니다. 자신의 영역(Comfort zone)을 벗어나 다양한 산업과 직무에 종사하는 멤버들과 서로의 생각을 나누면 정체되어 있던 성장이 다시 시작됩니다.</p>
\t\t</div>
\t\t<div>

\t\t\t<h3 style="font-size:16px; font-weight:700; color:#222; margin:0 0 14px 0;">회사 교육비로 결제 가능한가요</h3>

\t\t\t<p style="font-size:15px; line-height:1.75; color:#555; letter-spacing:-0.01em; margin:0;">가능합니다. 먼저 HFK 이메일 info@hbrforum.org로 사업자 등록증을 전달해주신 후, 채널톡을 남겨주세요. 채널톡 확인 후, HFK(위어드벤처)에서 세금계산서 발행해 드리고, 멤버십 쿠폰코드를 이메일로 보내드립니다. 메일로 받으신 쿠폰코드는 등록하실 팀 상세페이지의 [멤버십 등록하기] 버튼을 누르고, 결제 페이지 상단에서 입력 가능합니다. 무료 등록이 완료되면 멤버십 등록도 완료됩니다.</p>
\t\t</div></div>
\t<!-- // SECTION: FAQ -->
\t'''

    # 첫 세션까지 진행 과정 HTML (공통)
    process_steps_html = '''<!-- ========================================
     SECTION: 첫 세션까지 진행 과정
     ======================================== -->
\t<div style="background:#F5EBE0; border-radius:12px; padding:48px 36px;">

\t\t<h2 style="font-size:24px; font-weight:700; color:#8B0000; margin:0 0 14px 0;">첫 세션까지 진행 과정</h2>

\t\t<p style="font-size:15px; font-weight:500; color:#8B0000; line-height:1.8; margin:0 0 8px 0;">봄 시즌은 아래의 순서로 진행됩니다. 신청 전 꼼꼼히 읽어주시기 바랍니다.
\t\t\t<br>
\t\t\t<br>
\t\t</p>
\t\t<div style="background:#fff; border-radius:12px; padding:36px; border:1px solid #e5e5e5;">
\t\t\t<!-- Step 1 -->
\t\t\t<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

\t\t\t\t<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 1.</span> 시즌 등록 마감</p>

\t\t\t\t<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">3월 25일 (화) 자정에 등록이 마감됩니다.
\t\t\t\t\t<br>3월 29일 (토)에 가입 시 입력했던 이메일로 HFK 슬랙에 초대드립니다.
\t\t\t\t\t<br>3월 30일 (일) 21시에 첫 봄시즌 공지가 전달됩니다. 미리 이메일을 확인해 HFK 슬랙에 가입해주세요.</p>
\t\t\t</div>
\t\t\t<!-- Step 2 -->
\t\t\t<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

\t\t\t\t<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 2.</span> 시즌 첫 공지 및 자기소개 미션</p>

\t\t\t\t<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">3월 30일(일) 21시에 등록한 모든 멤버에게 HFK 슬랙으로 전체 공지(시즌 레터), 팀별 공지, 자기소개 미션이 전달됩니다.
\t\t\t\t\t<br>전체 공지와 팀별 공지는 시즌 기간 동안 매주 일요일 밤 아홉 시에 안내됩니다.
\t\t\t\t\t<br>첫 세션 이전까지 자기소개 미션을 꼭 마쳐주세요.</p>
\t\t\t</div>
\t\t\t<!-- Step 3 -->
\t\t\t<div style="margin-bottom:32px; padding-bottom:32px; border-bottom:1px solid #eee;">

\t\t\t\t<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 3.</span> 뉴멤버 오리엔테이션</p>

\t\t\t\t<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">4월 2일 (수), 4월 3일 (목) 오아시스 덕수궁에서 양일간 동일한 내용으로 뉴멤버 오리엔테이션이 진행됩니다.
\t\t\t\t\t<br>멤버십 구성, HFK 슬랙 사용법을 안내드리고, 뉴멤버 네트워킹 시간도 준비되어 있습니다.
\t\t\t\t\t<br>양일 모두 같은 내용을 진행하므로 가능한 일정에 참석해주세요.
\t\t\t\t\t<br>HFK가 처음이시라면 꼭 함께 해주세요.</p>
\t\t\t</div>
\t\t\t<!-- Step 4 -->
\t\t\t<div>

\t\t\t\t<p style="font-size:15px; font-weight:700; color:#222; margin:0 0 14px 0;"><span style="color:#8B0000;">Step 4.</span> 팀별 첫 세션</p>

\t\t\t\t<p style="font-size:14px; line-height:1.9; color:#555; margin:0;">4월 5일(토)부터 각 팀의 1회차 세션이 시작됩니다.
\t\t\t\t\t<br>멤버와 파트너가 서로 인사하고, 준비된 내용을 바탕으로 세션이 진행됩니다.
\t\t\t\t\t<br>자기소개를 위해 명함을 챙겨와주세요.</p>
\t\t\t</div></div></div>
\t<!-- // SECTION: 첫 세션까지 진행 과정 -->'''

    # 메인 타이틀과 소개글
    intro_html = ""
    for para in intro:
        intro_html += f'\n\t\t<p style="font-size:16px; line-height:1.75; color:#444; letter-spacing:-0.01em; margin:24px 0 0 0;">{para}</p>'

    # 전체 HTML 조합
    full_html = f'''<!-- ========================================
     HFK 팀 페이지
     ======================================== -->
<!-- 전체 컨테이너 -->
<div style="max-width:900px; margin:0 auto; font-family:'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:#333; letter-spacing:-0.01em;">
\t<!-- ========================================
     SECTION: 메인 타이틀
     ======================================== -->
\t<div style="margin-bottom:80px;">

\t\t<h1 style="font-size:32px; font-weight:700; color:#8B0000; line-height:1.5; margin:0 0 40px 0; letter-spacing:-0.02em;">{title}</h1>
{intro_html}
\t</div>
\t<!-- // SECTION: 메인 타이틀 -->
\t{image_gallery}
\t{sections_html}
\t{partner_html}
\t{sessions_html}
\t{process_html}
\t{groundrule_html}
\t{event_html}
\t{benefit_html}
\t{faq_html}
\t{process_steps_html}
</div>
<!-- // 전체 컨테이너 -->'''

    return full_html


def parse_product_content(html_content):
    """상품 content에서 데이터 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 메인 타이틀과 소개글
    title, intro = extract_main_title_and_intro(soup)

    # 이미지들
    images = extract_images(soup)

    # 01~04 섹션
    sections = {}
    for i in range(1, 5):
        sections[i] = extract_section_items(soup, i)

    # 파트너 정보
    partner = extract_partner_info(soup)

    # 세션 정보
    sessions = extract_sessions(soup)

    return {
        'title': title,
        'intro': intro,
        'images': images,
        'sections': sections,
        'partner': partner,
        'sessions': sessions
    }


def convert_and_update_product(client, product_no, dry_run=True):
    """상품 content를 변환하고 업데이트"""
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
    content = product_data.get('content', '')

    print(f"상품명: {name}")

    if not content:
        print("⚠️ content가 비어있습니다. 스킵합니다.")
        return False

    # 데이터 추출
    parsed_data = parse_product_content(content)
    print(f"추출된 데이터:")
    print(f"  - 타이틀: {parsed_data['title'][:50]}..." if parsed_data['title'] else "  - 타이틀: (없음)")
    print(f"  - 소개글: {len(parsed_data['intro'])}개 문단")
    print(f"  - 이미지: {len(parsed_data['images'])}개")
    print(f"  - 섹션 1 아이템: {len(parsed_data['sections'].get(1, []))}개")
    print(f"  - 섹션 2 아이템: {len(parsed_data['sections'].get(2, []))}개")
    print(f"  - 섹션 3 아이템: {len(parsed_data['sections'].get(3, []))}개")
    print(f"  - 섹션 4 아이템: {len(parsed_data['sections'].get(4, []))}개")
    print(f"  - 파트너: {parsed_data['partner'].get('name', '(없음)')}")
    print(f"  - 세션: {len(parsed_data['sessions'])}개")

    # 새 형식으로 변환
    new_content = generate_new_format(parsed_data)

    # 미리보기 저장
    preview_file = f"data/preview_{product_no}_{name}_new.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ 미리보기 저장: {preview_file}")

    if dry_run:
        print("🔍 DRY RUN 모드 - 실제 업데이트하지 않음")
        return True

    # 실제 업데이트
    result = client.update_product(str(product_no), {'content': new_content})
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
            if convert_and_update_product(client, product_no, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            fail_count += 1

    print(f"\n{'='*50}")
    print(f"완료: 성공 {success_count}개, 실패 {fail_count}개")

    if dry_run:
        print("\n💡 실제 업데이트를 하려면 --execute 옵션을 추가하세요:")
        print("   python scripts/convert_content_format.py --execute")


if __name__ == "__main__":
    main()
