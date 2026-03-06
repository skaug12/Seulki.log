"""
구조화된 팀 데이터를 IMWEB HTML 포맷으로 변환하는 모듈
"""
import json
import html
from typing import Dict, List, Optional


class ContentConverter:
    """구조화된 JSON 데이터를 IMWEB HTML로 변환"""

    # 스타일 상수
    STYLES = {
        'headline': 'color:#980000; font-size:32px; line-height:1.4; letter-spacing:-0.02em;',
        'intro_text': 'color:#333; font-size:16px; letter-spacing:-0.01em;',
        'section_number': 'font-size:24px; font-weight:700; color:#222; letter-spacing:-0.02em;',
        'section_title': 'font-size:24px; font-weight:700; color:#222; margin-left:16px; letter-spacing:-0.02em;',
        'section_subtitle': 'font-size:18px; color:#666; letter-spacing:-0.01em;',
        'body_text': 'font-size:16px; color:#333; letter-spacing:-0.01em;',
        'partner_name': 'font-size:20px; font-weight:700; color:#222; letter-spacing:-0.02em;',
        'session_number': 'font-size:18px; font-weight:700; color:#980000;',
        'session_date': 'font-size:16px; color:#666;',
        'session_topic': 'font-size:18px; font-weight:700; color:#222;',
        'session_subtitle': 'font-size:16px; color:#333;',
        'list_item': 'font-size:15px; color:#444; line-height:1.7;',
    }

    def __init__(self):
        pass

    def escape_html(self, text: str) -> str:
        """HTML 특수문자 이스케이프"""
        if not text:
            return ''
        # 기본 이스케이프
        text = html.escape(text)
        # 추가 변환
        text = text.replace("'", '&#39;')
        text = text.replace('"', '&quot;')
        return text

    def convert_team_to_html(self, team_data: Dict) -> str:
        """팀 데이터를 HTML content로 변환"""
        content = team_data.get('content', {})
        parts = []

        # 1. Hero Section - 헤드라인
        if content.get('headline'):
            parts.append(self._render_headline(content['headline']))

        # 2. Intro Text - 소개글
        if content.get('introduction'):
            parts.append(self._render_introduction(content['introduction']))

        # 3. 01 팀 배경
        if content.get('team_background'):
            parts.append(self._render_section(
                '01', '팀 배경', '어떤 계기로 만들어지게 되었나요?',
                content['team_background']
            ))

        # 4. 02 팀 운영 방향
        if content.get('team_operation'):
            parts.append(self._render_section(
                '02', '팀 운영 방향', '어떤 방식으로 운영되나요?',
                content['team_operation']
            ))

        # 5. 03 팀 성장 포인트
        if content.get('team_growth_points'):
            parts.append(self._render_section_with_list(
                '03', '팀 성장 포인트', '어떤 성장을 기대할 수 있을까요?',
                content['team_growth_points']
            ))

        # 6. 04 팀 멤버들
        if content.get('target_members'):
            parts.append(self._render_section_with_list(
                '04', '팀 멤버들', '누가 함께 하면 좋을까요?',
                content['target_members']
            ))

        # 7. 파트너 소개
        if content.get('partner', {}).get('name'):
            parts.append(self._render_partner(content['partner']))

        # 8. 세션 주제
        if content.get('sessions'):
            parts.append(self._render_sessions(content['sessions']))

        # 9. 진행방식
        if content.get('process'):
            parts.append(self._render_process(content['process']))

        # 10. 그라운드룰
        if content.get('ground_rules'):
            parts.append(self._render_ground_rules(content['ground_rules']))

        # 11. 이벤트
        if content.get('events'):
            parts.append(self._render_events(content['events']))

        # 12. 멤버십 베네핏
        if content.get('benefits'):
            parts.append(self._render_benefits(content['benefits']))

        # 13. FAQ
        if content.get('faq'):
            parts.append(self._render_faq(content['faq']))

        return ''.join(parts)

    def _render_headline(self, headline: str) -> str:
        """헤드라인 렌더링"""
        return f'''<!-- Hero Section --><p style="margin:0 0 40px 0;"><strong><span style="{self.STYLES['headline']}">{self.escape_html(headline)}</span></strong></p>'''

    def _render_introduction(self, intro: str) -> str:
        """소개글 렌더링"""
        paragraphs = intro.strip().split('\n\n')
        p_tags = []
        for i, p in enumerate(paragraphs):
            if p.strip():
                margin = '0' if i == len(paragraphs) - 1 else '0 0 20px 0'
                p_tags.append(
                    f'<p style="line-height:1.8; margin:{margin};"><span style="{self.STYLES["intro_text"]}">{self.escape_html(p.strip())}</span></p>'
                )
        return f'''<!-- Intro Text --><div style="margin-bottom:60px;">{''.join(p_tags)}</div>'''

    def _render_section(self, number: str, title: str, subtitle: str, content: str) -> str:
        """기본 섹션 렌더링"""
        paragraphs = content.strip().split('\n\n')
        p_tags = []
        for i, p in enumerate(paragraphs):
            if p.strip():
                margin = '0' if i == len(paragraphs) - 1 else '0 0 20px 0'
                p_tags.append(
                    f'<p style="line-height:1.8; margin:{margin};"><span style="{self.STYLES["body_text"]}">{self.escape_html(p.strip())}</span></p>'
                )

        return f'''<!-- {number} {title} --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_number']}">{number}</span> <span style="{self.STYLES['section_title']}">{title}</span></div><div style="margin-bottom:16px;"><span style="{self.STYLES['section_subtitle']}">{subtitle}</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(p_tags)}</div></div>'''

    def _render_section_with_list(self, number: str, title: str, subtitle: str, items: List[str]) -> str:
        """리스트가 있는 섹션 렌더링"""
        list_items = []
        for item in items:
            if item.strip():
                list_items.append(
                    f'<p style="line-height:1.8; margin:0 0 12px 0;"><span style="{self.STYLES["body_text"]}">• {self.escape_html(item.strip())}</span></p>'
                )

        return f'''<!-- {number} {title} --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_number']}">{number}</span> <span style="{self.STYLES['section_title']}">{title}</span></div><div style="margin-bottom:16px;"><span style="{self.STYLES['section_subtitle']}">{subtitle}</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(list_items)}</div></div>'''

    def _render_partner(self, partner: Dict) -> str:
        """파트너 소개 렌더링"""
        name = self.escape_html(partner.get('name', ''))
        bio = self.escape_html(partner.get('bio', ''))

        return f'''<!-- 파트너 소개 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">파트너 소개</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div><p style="margin:0 0 16px 0;"><span style="{self.STYLES['partner_name']}">{name}</span></p><p style="line-height:1.8; margin:0;"><span style="{self.STYLES['body_text']}">{bio}</span></p></div></div>'''

    def _render_sessions(self, sessions: List[Dict]) -> str:
        """세션 주제 렌더링"""
        session_items = []
        for s in sessions:
            num = s.get('session_number', '')
            date = self.escape_html(s.get('date', ''))
            day = self.escape_html(s.get('day', ''))
            topic = self.escape_html(s.get('topic', ''))
            subtitle = self.escape_html(s.get('subtitle', ''))
            details = s.get('details', [])

            details_html = ''
            if details:
                detail_items = ''.join([
                    f'<p style="margin:0 0 8px 0;"><span style="{self.STYLES["list_item"]}">- {self.escape_html(d)}</span></p>'
                    for d in details if d
                ])
                details_html = f'<div style="margin-top:12px;">{detail_items}</div>'

            session_items.append(f'''<div style="margin-bottom:40px; padding:20px; background:#f9f9f9; border-left:4px solid #980000;"><div style="margin-bottom:8px;"><span style="{self.STYLES['session_number']}">{num}회차</span><span style="{self.STYLES['session_date']}; margin-left:12px;">{date} ({day})</span></div><div style="margin-bottom:8px;"><span style="{self.STYLES['session_topic']}">{topic}</span></div><div><span style="{self.STYLES['session_subtitle']}">{subtitle}</span></div>{details_html}</div>''')

        return f'''<!-- 세션 주제 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">세션 주제</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(session_items)}</div></div>'''

    def _render_process(self, process: str) -> str:
        """진행방식 렌더링"""
        paragraphs = process.strip().split('\n')
        p_tags = []
        for p in paragraphs:
            if p.strip():
                p_tags.append(
                    f'<p style="line-height:1.8; margin:0 0 12px 0;"><span style="{self.STYLES["body_text"]}">{self.escape_html(p.strip())}</span></p>'
                )

        return f'''<!-- 진행방식 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">진행방식</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(p_tags)}</div></div>'''

    def _render_ground_rules(self, rules: List[Dict]) -> str:
        """그라운드룰 렌더링"""
        rules_html = []
        for r in rules:
            rule = self.escape_html(r.get('rule', ''))
            desc = self.escape_html(r.get('description', ''))
            rules_html.append(
                f'<p style="margin:0 0 12px 0;"><span style="font-weight:700; color:#980000;">{rule}</span> <span style="{self.STYLES["body_text"]}">{desc}</span></p>'
            )

        return f'''<!-- 그라운드룰 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">그라운드룰</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div style="padding:20px; background:#f5f5f5;">{''.join(rules_html)}</div></div>'''

    def _render_events(self, events: List[Dict]) -> str:
        """이벤트 렌더링"""
        icons = ['❶', '❷', '❸', '❹', '❺']
        events_html = []
        for i, e in enumerate(events):
            icon = icons[i] if i < len(icons) else f'{i+1}.'
            name = self.escape_html(e.get('name', ''))
            date = self.escape_html(e.get('date', ''))
            desc = self.escape_html(e.get('description', ''))
            events_html.append(
                f'<div style="margin-bottom:20px;"><p style="margin:0 0 8px 0;"><span style="font-size:18px;">{icon}</span> <span style="font-size:18px; font-weight:700;">{name}</span></p><p style="margin:0 0 8px 0;"><span style="{self.STYLES["session_date"]}">{date}</span></p><p style="margin:0;"><span style="{self.STYLES["body_text"]}">{desc}</span></p></div>'
            )

        return f'''<!-- 이벤트 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">이벤트</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(events_html)}</div></div>'''

    def _render_benefits(self, benefits: List[Dict]) -> str:
        """멤버십 베네핏 렌더링"""
        benefits_html = []
        for b in benefits:
            num = self.escape_html(b.get('number', ''))
            title = self.escape_html(b.get('title', ''))
            desc = self.escape_html(b.get('description', ''))
            benefits_html.append(
                f'<div style="margin-bottom:24px; padding:20px; border:1px solid #ddd;"><p style="margin:0 0 8px 0;"><span style="font-size:14px; color:#980000; font-weight:700;">{num}</span></p><p style="margin:0 0 12px 0;"><span style="font-size:18px; font-weight:700;">{title}</span></p><p style="margin:0; line-height:1.7;"><span style="{self.STYLES["body_text"]}">{desc}</span></p></div>'
            )

        return f'''<!-- 멤버십 베네핏 --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">멤버십 베네핏</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(benefits_html)}</div></div>'''

    def _render_faq(self, faq: List[Dict]) -> str:
        """FAQ 렌더링"""
        faq_html = []
        for f in faq:
            q = self.escape_html(f.get('question', ''))
            a = self.escape_html(f.get('answer', ''))
            faq_html.append(
                f'<div style="margin-bottom:24px;"><p style="margin:0 0 12px 0;"><span style="font-size:17px; font-weight:700; color:#222;">Q. {q}</span></p><p style="margin:0; line-height:1.8;"><span style="{self.STYLES["body_text"]}">{a}</span></p></div>'
            )

        return f'''<!-- FAQ --><div style="margin-bottom:80px;"><div style="margin-bottom:32px;"><div style="margin-bottom:16px;"><span style="{self.STYLES['section_title']}">자주 묻는 질문</span></div><div style="width:100%; height:2px; background:#000;"><br></div></div><div>{''.join(faq_html)}</div></div>'''

    def convert_simple_content(self, team_data: Dict) -> str:
        """simple_content (간략 설명) 생성"""
        content = team_data.get('content', {})
        sessions = content.get('sessions', [])

        # 일정 정보 추출
        if not sessions:
            return ''

        # 요일과 시간 (첫 세션 기준)
        first_session = sessions[0] if sessions else {}
        day = first_session.get('day', '')
        schedule_title = f"{day}요일 19:30-22:00 (3개월)" if day else "3개월 시즌"

        # 세션 일정 테이블
        rows = []
        for i in range(0, len(sessions), 2):
            left = sessions[i] if i < len(sessions) else None
            right = sessions[i+1] if i+1 < len(sessions) else None

            left_html = f'<span style="flex:0 0 3em; font-weight:700;">{left["session_number"]}회차</span> {left.get("date", "")}' if left else ''
            right_html = f'<span style="flex:0 0 3em; font-weight:700;">{right["session_number"]}회차</span> {right.get("date", "")}' if right else ''

            border = 'border-bottom:1px solid #000;' if i < len(sessions) - 2 else ''
            rows.append(f'''<div style="display:flex; flex-wrap:nowrap; {border} padding:5px 0;"><div style="flex:0 0 50%; display:flex; align-items:baseline; gap:8px; padding-right:12px;">{left_html}</div><div style="flex:0 0 50%; display:flex; align-items:baseline; gap:8px; padding-left:12px;">{right_html}</div></div>''')

        schedule_table = f'''<div style="border-top:1px solid #000; border-bottom:1px solid #000; font-size:16px; line-height:1.7; color:#000;">{''.join(rows)}</div>'''

        return f'''<!-- 제목 --><p style="margin:0 0 12px;"><strong style="font-size:20px; color:#980000;">{schedule_title}</strong></p>{schedule_table}<p style="margin-top: 32px; margin-bottom: 10px;"><strong style="font-size:20px; color:#980000;">3개월 시즌 멤버십</strong></p><p><span style="font-size: 16px;">❶ 3개월동안 &#39;팀&#39; 참여 <br> ❷ 매주 일요일 밤 세미나, 북토크 등 &#39;이벤트&#39; 신청 <br>❸ HBR 매거진, 폴인 이용권, 공간 혜택 등 &#39;베네핏&#39; 경험&nbsp;</span></p>'''


def main():
    """테스트"""
    # 구조화된 데이터 로드
    with open('data/teams_structured_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    converter = ContentConverter()

    # 첫 번째 팀으로 테스트
    team = dataset['teams'][0]
    print(f"=== {team['meta']['name']} HTML 변환 테스트 ===\n")

    html_content = converter.convert_team_to_html(team)
    print(html_content[:2000])
    print("\n... (이하 생략)")


if __name__ == "__main__":
    main()
