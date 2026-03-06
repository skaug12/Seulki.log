#!/usr/bin/env python3
"""
팀 데이터 편집 스크립트

구조화된 팀 데이터를 편집합니다.

사용법:
    # 팀 헤드라인 수정
    python scripts/edit_team.py "도쿄의기획" --headline "새로운 헤드라인"

    # 팀 소개글 수정
    python scripts/edit_team.py "도쿄의기획" --introduction "새로운 소개글"

    # 파트너 이름 수정
    python scripts/edit_team.py "도쿄의기획" --partner-name "홍길동"

    # 파트너 소개 수정
    python scripts/edit_team.py "도쿄의기획" --partner-bio "새로운 소개"

    # 세션 추가
    python scripts/edit_team.py "도쿄의기획" --add-session '{"session_number": 7, "date": "3월 10일", "day": "화", "topic": "새 주제", "subtitle": "부제목", "details": ["상세1", "상세2"]}'

    # 세션 수정
    python scripts/edit_team.py "도쿄의기획" --update-session 1 '{"topic": "수정된 주제"}'

    # JSON 파일로 전체 수정
    python scripts/edit_team.py "도쿄의기획" --from-json path/to/updates.json
"""
import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DATASET_FILE = os.path.join(DATA_DIR, 'teams_structured_dataset.json')


def load_dataset():
    """데이터셋 로드"""
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_dataset(dataset):
    """데이터셋 저장"""
    dataset['last_modified'] = datetime.now().isoformat()
    with open(DATASET_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ 저장 완료: {DATASET_FILE}")


def find_team_index(dataset, team_name):
    """팀 인덱스 찾기"""
    for i, team in enumerate(dataset['teams']):
        if team['meta']['name'] == team_name:
            return i
    return -1


def edit_team(dataset, team_name, updates):
    """팀 데이터 수정"""
    idx = find_team_index(dataset, team_name)
    if idx < 0:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return False

    team = dataset['teams'][idx]
    content = team['content']

    for key, value in updates.items():
        if key == 'headline':
            content['headline'] = value
            print(f"  ✓ headline 수정")

        elif key == 'introduction':
            content['introduction'] = value
            print(f"  ✓ introduction 수정")

        elif key == 'team_background':
            content['team_background'] = value
            print(f"  ✓ team_background 수정")

        elif key == 'team_operation':
            content['team_operation'] = value
            print(f"  ✓ team_operation 수정")

        elif key == 'team_growth_points':
            content['team_growth_points'] = value
            print(f"  ✓ team_growth_points 수정 ({len(value)}개)")

        elif key == 'target_members':
            content['target_members'] = value
            print(f"  ✓ target_members 수정 ({len(value)}개)")

        elif key == 'partner_name':
            if 'partner' not in content:
                content['partner'] = {}
            content['partner']['name'] = value
            print(f"  ✓ partner.name 수정")

        elif key == 'partner_bio':
            if 'partner' not in content:
                content['partner'] = {}
            content['partner']['bio'] = value
            print(f"  ✓ partner.bio 수정")

        elif key == 'process':
            content['process'] = value
            print(f"  ✓ process 수정")

        elif key == 'ground_rules':
            content['ground_rules'] = value
            print(f"  ✓ ground_rules 수정")

        elif key == 'events':
            content['events'] = value
            print(f"  ✓ events 수정")

        elif key == 'benefits':
            content['benefits'] = value
            print(f"  ✓ benefits 수정")

        elif key == 'faq':
            content['faq'] = value
            print(f"  ✓ faq 수정")

    dataset['teams'][idx] = team
    return True


def add_session(dataset, team_name, session_data):
    """세션 추가"""
    idx = find_team_index(dataset, team_name)
    if idx < 0:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return False

    team = dataset['teams'][idx]
    if 'sessions' not in team['content']:
        team['content']['sessions'] = []

    team['content']['sessions'].append(session_data)
    dataset['teams'][idx] = team
    print(f"  ✓ 세션 추가: {session_data.get('session_number')}회차")
    return True


def update_session(dataset, team_name, session_number, updates):
    """세션 수정"""
    idx = find_team_index(dataset, team_name)
    if idx < 0:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return False

    team = dataset['teams'][idx]
    sessions = team['content'].get('sessions', [])

    for i, session in enumerate(sessions):
        if session.get('session_number') == session_number:
            sessions[i].update(updates)
            print(f"  ✓ {session_number}회차 세션 수정")
            dataset['teams'][idx]['content']['sessions'] = sessions
            return True

    print(f"❌ {session_number}회차 세션을 찾을 수 없습니다")
    return False


def export_team_json(dataset, team_name, output_path):
    """팀 데이터를 JSON 파일로 내보내기"""
    idx = find_team_index(dataset, team_name)
    if idx < 0:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return False

    team = dataset['teams'][idx]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(team, f, ensure_ascii=False, indent=2)
    print(f"✅ 내보내기 완료: {output_path}")
    return True


def import_team_json(dataset, team_name, input_path):
    """JSON 파일에서 팀 데이터 가져오기"""
    idx = find_team_index(dataset, team_name)
    if idx < 0:
        print(f"❌ 팀을 찾을 수 없습니다: {team_name}")
        return False

    with open(input_path, 'r', encoding='utf-8') as f:
        updates = json.load(f)

    # content 부분만 업데이트
    if 'content' in updates:
        dataset['teams'][idx]['content'] = updates['content']
        print(f"✅ content 전체 업데이트")
    else:
        # updates가 content의 일부분인 경우
        for key, value in updates.items():
            dataset['teams'][idx]['content'][key] = value
            print(f"  ✓ {key} 업데이트")

    return True


def main():
    parser = argparse.ArgumentParser(description='팀 데이터 편집 도구')
    parser.add_argument('team_name', nargs='?', help='팀 이름')

    # 단일 필드 수정
    parser.add_argument('--headline', type=str, help='헤드라인 수정')
    parser.add_argument('--introduction', type=str, help='소개글 수정')
    parser.add_argument('--team-background', type=str, help='팀 배경 수정')
    parser.add_argument('--team-operation', type=str, help='팀 운영 방향 수정')
    parser.add_argument('--partner-name', type=str, help='파트너 이름 수정')
    parser.add_argument('--partner-bio', type=str, help='파트너 소개 수정')
    parser.add_argument('--process', type=str, help='진행방식 수정')

    # 세션 관련
    parser.add_argument('--add-session', type=str, help='세션 추가 (JSON 문자열)')
    parser.add_argument('--update-session', nargs=2, metavar=('NUM', 'JSON'), help='세션 수정')

    # 파일 기반 수정
    parser.add_argument('--from-json', type=str, help='JSON 파일에서 업데이트')
    parser.add_argument('--export', type=str, help='팀 데이터를 JSON 파일로 내보내기')

    args = parser.parse_args()

    if not args.team_name:
        parser.print_help()
        return

    dataset = load_dataset()
    team_name = args.team_name
    modified = False

    print(f"\n=== {team_name} 편집 ===\n")

    # 내보내기
    if args.export:
        export_team_json(dataset, team_name, args.export)
        return

    # JSON 파일에서 가져오기
    if args.from_json:
        if import_team_json(dataset, team_name, args.from_json):
            modified = True

    # 단일 필드 수정
    updates = {}
    if args.headline:
        updates['headline'] = args.headline
    if args.introduction:
        updates['introduction'] = args.introduction
    if args.team_background:
        updates['team_background'] = args.team_background
    if args.team_operation:
        updates['team_operation'] = args.team_operation
    if args.partner_name:
        updates['partner_name'] = args.partner_name
    if args.partner_bio:
        updates['partner_bio'] = args.partner_bio
    if args.process:
        updates['process'] = args.process

    if updates:
        if edit_team(dataset, team_name, updates):
            modified = True

    # 세션 추가
    if args.add_session:
        session_data = json.loads(args.add_session)
        if add_session(dataset, team_name, session_data):
            modified = True

    # 세션 수정
    if args.update_session:
        session_num = int(args.update_session[0])
        session_updates = json.loads(args.update_session[1])
        if update_session(dataset, team_name, session_num, session_updates):
            modified = True

    # 저장
    if modified:
        save_dataset(dataset)
    else:
        print("변경 사항이 없습니다.")


if __name__ == "__main__":
    main()
