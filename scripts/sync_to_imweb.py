#!/usr/bin/env python3
"""
IMWEB 동기화 스크립트

구조화된 팀 데이터를 수정하고 IMWEB에 업데이트합니다.

사용법:
    # 모든 팀 목록 보기
    python scripts/sync_to_imweb.py --list

    # 특정 팀 상세 보기
    python scripts/sync_to_imweb.py --show "도쿄의기획"

    # 특정 팀 HTML 미리보기
    python scripts/sync_to_imweb.py --preview "도쿄의기획"

    # 특정 팀을 IMWEB에 동기화
    python scripts/sync_to_imweb.py --sync "도쿄의기획"

    # 모든 팀 동기화 (주의!)
    python scripts/sync_to_imweb.py --sync-all

    # 테스트 모드 (실제 API 호출 없이 확인)
    python scripts/sync_to_imweb.py --sync "도쿄의기획" --dry-run
"""
import sys
import os
import json
import argparse
from datetime import datetime

# 상위 디렉토리 모듈 접근
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from imweb_api import ImwebAPI
from content_converter import ContentConverter

# 환경 변수 로드
load_dotenv()

# 경로 설정
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DATASET_FILE = os.path.join(DATA_DIR, 'teams_structured_dataset.json')


def load_dataset():
    """구조화된 데이터셋 로드"""
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_dataset(dataset):
    """데이터셋 저장"""
    dataset['last_modified'] = datetime.now().isoformat()
    with open(DATASET_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ 데이터셋 저장 완료: {DATASET_FILE}")


def find_team(dataset, team_name):
    """팀 이름으로 팀 데이터 찾기"""
    for team in dataset['teams']:
        if team['meta']['name'] == team_name:
            return team
    return None


def list_teams(dataset):
    """모든 팀 목록 출력"""
    print("\n=== 팀 목록 ===\n")
    print(f"{'No':<6} {'팀 이름':<20} {'상태':<10} {'세션':<6} {'파트너'}")
    print("-" * 60)

    for team in dataset['teams']:
        meta = team['meta']
        content = team['content']
        sessions = len(content.get('sessions', []))
        partner = '✓' if content.get('partner', {}).get('name') else '-'
        status = meta.get('prod_status', '-')

        print(f"{meta['no']:<6} {meta['name']:<20} {status:<10} {sessions:<6} {partner}")

    print(f"\n총 {len(dataset['teams'])}개 팀")


def show_team(team):
    """팀 상세 정보 출력"""
    meta = team['meta']
    content = team['content']

    print(f"\n{'='*60}")
    print(f"팀 이름: {meta['name']}")
    print(f"{'='*60}")
    print(f"\n[메타 정보]")
    print(f"  - No: {meta['no']}")
    print(f"  - 가격: {meta.get('price', 0):,}원")
    print(f"  - 상태: {meta.get('prod_status', '-')}")

    print(f"\n[콘텐츠]")
    print(f"  - 헤드라인: {content.get('headline', '-')}")
    print(f"  - 소개글: {content.get('introduction', '-')[:100]}...")
    print(f"  - 팀 배경: {content.get('team_background', '-')[:100]}...")
    print(f"  - 팀 운영: {content.get('team_operation', '-')[:100]}...")

    print(f"\n[성장 포인트]")
    for i, point in enumerate(content.get('team_growth_points', [])[:3], 1):
        print(f"  {i}. {point[:60]}...")

    print(f"\n[대상 멤버]")
    for i, member in enumerate(content.get('target_members', [])[:3], 1):
        print(f"  {i}. {member[:60]}...")

    partner = content.get('partner', {})
    print(f"\n[파트너]")
    print(f"  - 이름: {partner.get('name', '-')}")
    print(f"  - 소개: {partner.get('bio', '-')[:100]}...")

    print(f"\n[세션] ({len(content.get('sessions', []))}개)")
    for s in content.get('sessions', []):
        print(f"  {s['session_number']}회차 | {s.get('date', '-')} | {s.get('topic', '-')}")


def preview_html(team, converter):
    """HTML 변환 미리보기"""
    print(f"\n=== {team['meta']['name']} HTML 미리보기 ===\n")

    html_content = converter.convert_team_to_html(team)
    simple_content = converter.convert_simple_content(team)

    print("[content] (상세 설명)")
    print("-" * 40)
    print(html_content[:1500])
    print("\n... (이하 생략)\n")

    print("[simple_content] (간략 설명)")
    print("-" * 40)
    print(simple_content[:1000])


def sync_team(team, api, converter, dry_run=False):
    """단일 팀을 IMWEB에 동기화"""
    meta = team['meta']
    product_code = str(meta['no'])
    team_name = meta['name']

    print(f"\n{'='*60}")
    print(f"동기화 시작: {team_name} (no: {product_code})")
    print(f"{'='*60}")

    # HTML 변환
    html_content = converter.convert_team_to_html(team)
    simple_content = converter.convert_simple_content(team)

    # 업데이트 데이터 구성
    update_data = {
        'content': html_content,
        'simple_content': simple_content,
    }

    print(f"\n[업데이트 내용]")
    print(f"  - content 길이: {len(html_content):,}자")
    print(f"  - simple_content 길이: {len(simple_content):,}자")

    if dry_run:
        print(f"\n🔸 DRY RUN 모드 - 실제 API 호출 없음")
        print(f"\n[content 미리보기 (처음 500자)]")
        print(html_content[:500])
        return {'dry_run': True, 'product_code': product_code}

    # API 호출
    print(f"\n⏳ IMWEB API 호출 중...")
    result = api.update_product(product_code, update_data)

    if result.get('code') == 200:
        print(f"✅ 동기화 완료: {team_name}")
    else:
        print(f"❌ 동기화 실패: {result}")

    return result


def sync_all_teams(dataset, api, converter, dry_run=False):
    """모든 팀 동기화"""
    print(f"\n{'='*60}")
    print(f"전체 팀 동기화 시작 ({len(dataset['teams'])}개)")
    print(f"{'='*60}")

    if not dry_run:
        confirm = input("\n⚠️  모든 팀을 IMWEB에 동기화합니다. 계속하시겠습니까? (yes/no): ")
        if confirm.lower() != 'yes':
            print("취소되었습니다.")
            return

    results = {'success': 0, 'failed': 0, 'errors': []}

    for i, team in enumerate(dataset['teams'], 1):
        print(f"\n[{i}/{len(dataset['teams'])}] {team['meta']['name']}")

        try:
            result = sync_team(team, api, converter, dry_run)
            if result.get('code') == 200 or result.get('dry_run'):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'team': team['meta']['name'],
                    'error': result
                })
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'team': team['meta']['name'],
                'error': str(e)
            })

        # API 호출 간격
        if not dry_run:
            import time
            time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"동기화 완료")
    print(f"  - 성공: {results['success']}")
    print(f"  - 실패: {results['failed']}")
    print(f"{'='*60}")

    if results['errors']:
        print("\n[에러 목록]")
        for err in results['errors']:
            print(f"  - {err['team']}: {err['error']}")


def main():
    parser = argparse.ArgumentParser(description='IMWEB 동기화 도구')
    parser.add_argument('--list', action='store_true', help='모든 팀 목록 보기')
    parser.add_argument('--show', type=str, help='특정 팀 상세 보기')
    parser.add_argument('--preview', type=str, help='특정 팀 HTML 미리보기')
    parser.add_argument('--sync', type=str, help='특정 팀 동기화')
    parser.add_argument('--sync-all', action='store_true', help='모든 팀 동기화')
    parser.add_argument('--dry-run', action='store_true', help='테스트 모드 (실제 API 호출 없음)')

    args = parser.parse_args()

    # 데이터 로드
    dataset = load_dataset()
    converter = ContentConverter()

    # API 클라이언트 (sync 명령에만 필요)
    api = None
    if args.sync or args.sync_all:
        api_key = os.getenv('IMWEB_API_KEY')
        api_secret = os.getenv('IMWEB_API_SECRET')

        if not api_key or not api_secret:
            print("❌ 환경 변수 IMWEB_API_KEY, IMWEB_API_SECRET이 필요합니다.")
            sys.exit(1)

        api = ImwebAPI(api_key, api_secret)

    # 명령 처리
    if args.list:
        list_teams(dataset)

    elif args.show:
        team = find_team(dataset, args.show)
        if team:
            show_team(team)
        else:
            print(f"❌ 팀을 찾을 수 없습니다: {args.show}")

    elif args.preview:
        team = find_team(dataset, args.preview)
        if team:
            preview_html(team, converter)
        else:
            print(f"❌ 팀을 찾을 수 없습니다: {args.preview}")

    elif args.sync:
        team = find_team(dataset, args.sync)
        if team:
            sync_team(team, api, converter, dry_run=args.dry_run)
        else:
            print(f"❌ 팀을 찾을 수 없습니다: {args.sync}")

    elif args.sync_all:
        sync_all_teams(dataset, api, converter, dry_run=args.dry_run)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
