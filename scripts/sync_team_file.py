#!/usr/bin/env python3
"""
개별 팀 JSON 파일 동기화 스크립트

data/teams/ 폴더의 개별 JSON 파일을 직접 수정하고 IMWEB에 동기화합니다.

사용법:
    # 팀 목록 보기
    python scripts/sync_team_file.py --list

    # 특정 팀 파일 보기
    python scripts/sync_team_file.py --show "도쿄의기획"

    # 특정 팀 동기화
    python scripts/sync_team_file.py --sync "도쿄의기획"

    # 테스트 모드
    python scripts/sync_team_file.py --sync "도쿄의기획" --dry-run

    # 모든 팀 동기화 (복제 제외)
    python scripts/sync_team_file.py --sync-all
"""
import sys
import os
import json
import argparse
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from imweb_api import ImwebAPI
from content_converter import ContentConverter

load_dotenv()

TEAMS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'teams')


def get_team_files(include_duplicates=False):
    """팀 파일 목록 가져오기"""
    files = []
    for f in os.listdir(TEAMS_DIR):
        if f.endswith('.json'):
            if not include_duplicates and '복제' in f:
                continue
            files.append(f)
    return sorted(files)


def load_team_file(team_name):
    """팀 파일 로드 (이름 또는 파일명으로)"""
    # 직접 파일명 시도
    filepath = os.path.join(TEAMS_DIR, f"{team_name}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), filepath

    # 파일명에서 검색
    for filename in os.listdir(TEAMS_DIR):
        if filename.endswith('.json'):
            fp = os.path.join(TEAMS_DIR, filename)
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('name') == team_name:
                    return data, fp

    return None, None


def save_team_file(filepath, data):
    """팀 파일 저장"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 파일 저장: {filepath}")


def parse_content_to_structured(content_plain, name):
    """content_plain을 구조화된 데이터로 파싱"""
    result = {
        'team_name': name,
        'headline': '',
        'introduction': '',
        'team_background': '',
        'team_operation': '',
        'team_growth_points': [],
        'target_members': [],
        'partner': {'name': '', 'bio': ''},
        'sessions': [],
        'process': '',
        'ground_rules': [],
        'events': [],
        'benefits': [],
        'faq': []
    }

    if not content_plain:
        return result

    lines = content_plain.strip().split('\n')
    if lines:
        result['headline'] = lines[0].strip()

    # 소개글
    intro_match = re.search(r'^(.+?)(?=01\s*팀 배경|$)', content_plain, re.DOTALL)
    if intro_match:
        intro_text = intro_match.group(1).strip()
        intro_lines = intro_text.split('\n')[1:]
        result['introduction'] = '\n'.join(intro_lines).strip()

    # 01 팀 배경
    bg_match = re.search(r'01\s*팀 배경.*?어떤 계기로.*?\n(.+?)(?=02\s*팀 운영|$)', content_plain, re.DOTALL)
    if bg_match:
        result['team_background'] = bg_match.group(1).strip()

    # 02 팀 운영
    op_match = re.search(r'02\s*팀 운영.*?어떤 방식으로.*?\n(.+?)(?=03\s*팀 성장|$)', content_plain, re.DOTALL)
    if op_match:
        result['team_operation'] = op_match.group(1).strip()

    # 03 팀 성장
    growth_match = re.search(r'03\s*팀 성장.*?어떤 성장을.*?\n(.+?)(?=04\s*팀 멤버|$)', content_plain, re.DOTALL)
    if growth_match:
        result['team_growth_points'] = [p.strip() for p in growth_match.group(1).strip().split('\n') if p.strip()]

    # 04 팀 멤버
    member_match = re.search(r'04\s*팀 멤버.*?누가 함께.*?\n(.+?)(?=파트너 소개|$)', content_plain, re.DOTALL)
    if member_match:
        result['target_members'] = [m.strip() for m in member_match.group(1).strip().split('\n') if m.strip()]

    # 파트너
    partner_match = re.search(r'파트너 소개\s*\n(.+?)(?=\d개월 세션 주제|세션 주제|진행방식|$)', content_plain, re.DOTALL)
    if partner_match:
        partner_lines = [l.strip() for l in partner_match.group(1).strip().split('\n') if l.strip()]
        if partner_lines:
            result['partner']['name'] = partner_lines[0]
            result['partner']['bio'] = '\n'.join(partner_lines[1:])

    # 세션
    session_match = re.search(r'(\d개월 )?세션 주제\s*\n(.+?)(?=진행방식|$)', content_plain, re.DOTALL)
    if session_match:
        session_text = session_match.group(2).strip()
        session_pattern = r'(\d)회차\s*\n?(\d+월\s*\d+일)?\s*\(?(월|화|수|목|금|토|일)?\)?\s*\n?([^\n]+)\s*\n?([^\n]*)\s*\n?((?:- [^\n]+\n?)*)'
        sessions = re.findall(session_pattern, session_text)
        for s in sessions:
            session_info = {
                'session_number': int(s[0]) if s[0] else 0,
                'date': s[1].strip() if s[1] else '',
                'day': s[2].strip() if s[2] else '',
                'topic': s[3].strip() if s[3] else '',
                'subtitle': s[4].strip() if s[4] else '',
                'details': [d.strip('- ').strip() for d in s[5].split('\n') if d.strip()]
            }
            if session_info['topic']:
                result['sessions'].append(session_info)

    # 진행방식
    process_match = re.search(r'진행방식\s*\n(.+?)(?=그라운드룰|$)', content_plain, re.DOTALL)
    if process_match:
        result['process'] = process_match.group(1).strip()

    return result


def list_teams():
    """팀 목록 출력"""
    files = get_team_files(include_duplicates=False)

    print("\n=== 팀 파일 목록 (data/teams/) ===\n")
    print(f"{'No':<6} {'팀 이름':<25} {'파일명'}")
    print("-" * 70)

    for filename in files:
        filepath = os.path.join(TEAMS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"{data.get('no', '-'):<6} {data.get('name', '-'):<25} {filename}")

    print(f"\n총 {len(files)}개 팀 (복제 제외)")
    print(f"\n💡 파일 직접 편집: code data/teams/팀이름.json")


def show_team(team_name):
    """팀 상세 보기"""
    data, filepath = load_team_file(team_name)
    if not data:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return

    print(f"\n{'='*60}")
    print(f"팀: {data.get('name')}")
    print(f"파일: {filepath}")
    print(f"{'='*60}")

    print(f"\n[기본 정보]")
    print(f"  No: {data.get('no')}")
    print(f"  가격: {data.get('price', 0):,}원")
    print(f"  상태: {data.get('prod_status')}")

    print(f"\n[content_plain 미리보기]")
    content_plain = data.get('content_plain', '')
    print(f"  {content_plain[:300]}..." if content_plain else "  (없음)")

    print(f"\n💡 편집하려면: code {filepath}")


def sync_team(team_name, api, converter, dry_run=False):
    """팀 파일을 IMWEB에 동기화"""
    data, filepath = load_team_file(team_name)
    if not data:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return None

    product_code = str(data.get('no'))

    print(f"\n{'='*60}")
    print(f"동기화: {data.get('name')} (no: {product_code})")
    print(f"파일: {filepath}")
    print(f"{'='*60}")

    # content_plain을 구조화된 데이터로 파싱
    structured = parse_content_to_structured(
        data.get('content_plain', ''),
        data.get('name', '')
    )

    # 구조화 데이터를 HTML로 변환
    team_data = {
        'meta': {'name': data.get('name')},
        'content': structured
    }

    html_content = converter.convert_team_to_html(team_data)
    simple_content = converter.convert_simple_content(team_data)

    print(f"\n[변환 결과]")
    print(f"  content: {len(html_content):,}자")
    print(f"  simple_content: {len(simple_content):,}자")

    if dry_run:
        print(f"\n🔸 DRY RUN - 실제 업로드 없음")
        print(f"\n[HTML 미리보기]")
        print(html_content[:500])
        return {'dry_run': True}

    # API 호출
    print(f"\n⏳ IMWEB API 호출 중...")
    result = api.update_product(product_code, {
        'content': html_content,
        'simple_content': simple_content
    })

    if result.get('code') == 200:
        print(f"✅ 동기화 완료!")
    else:
        print(f"❌ 실패: {result}")

    return result


def sync_all(api, converter, dry_run=False):
    """모든 팀 동기화"""
    files = get_team_files(include_duplicates=False)

    print(f"\n{'='*60}")
    print(f"전체 동기화: {len(files)}개 팀")
    print(f"{'='*60}")

    if not dry_run:
        confirm = input("\n⚠️  모든 팀을 동기화합니다. 계속? (yes/no): ")
        if confirm.lower() != 'yes':
            print("취소됨")
            return

    results = {'success': 0, 'failed': 0}

    for i, filename in enumerate(files, 1):
        team_name = filename.replace('.json', '')
        print(f"\n[{i}/{len(files)}] {team_name}")

        try:
            result = sync_team(team_name, api, converter, dry_run)
            if result and (result.get('code') == 200 or result.get('dry_run')):
                results['success'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            print(f"❌ 에러: {e}")
            results['failed'] += 1

        if not dry_run:
            time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"완료 - 성공: {results['success']}, 실패: {results['failed']}")


def main():
    parser = argparse.ArgumentParser(description='개별 팀 파일 동기화')
    parser.add_argument('--list', action='store_true', help='팀 목록')
    parser.add_argument('--show', type=str, help='팀 상세 보기')
    parser.add_argument('--sync', type=str, help='팀 동기화')
    parser.add_argument('--sync-all', action='store_true', help='전체 동기화')
    parser.add_argument('--dry-run', action='store_true', help='테스트 모드')

    args = parser.parse_args()

    # API 초기화
    api = None
    converter = ContentConverter()

    if args.sync or args.sync_all:
        api_key = os.getenv('IMWEB_API_KEY')
        api_secret = os.getenv('IMWEB_API_SECRET')
        if not api_key or not api_secret:
            print("❌ IMWEB_API_KEY, IMWEB_API_SECRET 필요")
            sys.exit(1)
        api = ImwebAPI(api_key, api_secret)

    if args.list:
        list_teams()
    elif args.show:
        show_team(args.show)
    elif args.sync:
        sync_team(args.sync, api, converter, args.dry_run)
    elif args.sync_all:
        sync_all(api, converter, args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
