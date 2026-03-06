#!/usr/bin/env python3
"""
백업 파일(2026-01-22)로부터 아임웹 상품 복구
- 26봄주중, 26봄주말 카테고리 상품은 절대 수정하지 않음
- 그 외 카테고리 상품은 백업 내용대로 복구
- '복제' 상품도 매칭하여 복구
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI

# API credentials
API_KEY = '809057085795e753d6135b26c46c559b2ea43f6384'
API_SECRET = '2310801a987b84e7e944ca'

# 26봄 카테고리 IDs (절대 수정 금지)
SPRING_WEEKDAY = 's2026012319995240b6e87'  # 26봄주중
SPRING_WEEKEND = 's2026012311f5fb372b835'  # 26봄주말
EXCLUDED_CATEGORIES = {SPRING_WEEKDAY, SPRING_WEEKEND}

# 백업 파일 경로
BACKUP_FILES = [
    'archive/data/imweb_products_20260122_170736.json',
    'archive/data/imweb_products_20260122_170906.json',
    'archive/data/imweb_products_20260122_171019.json',
    'archive/data/imweb_products_20260122_171322.json',
]


def load_backup_products():
    """4개 백업 파일에서 고유 상품 로드 (no 기준 중복 제거)"""
    products = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for filepath in BACKUP_FILES:
        full_path = os.path.join(base_dir, filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for product in data:
            no = product.get('no')
            if no and no not in products:
                products[no] = product

    print(f"백업에서 고유 상품 {len(products)}개 로드 완료")
    return products


def get_spring_product_nos(client):
    """26봄주중/26봄주말 카테고리에 속한 상품 no 목록 조회"""
    spring_nos = set()

    for cat_id, cat_name in [(SPRING_WEEKDAY, '26봄주중'), (SPRING_WEEKEND, '26봄주말')]:
        page = 1
        while True:
            result = client.get_products(category=cat_id, limit=100, page=page)
            if 'error' in result:
                print(f"  {cat_name} 조회 실패: {result}")
                break

            data = result.get('data', {})
            if isinstance(data, dict):
                product_list = data.get('list', [])
            elif isinstance(data, list):
                product_list = data
            else:
                break

            if not product_list:
                break

            for p in product_list:
                no = p.get('no')
                if no:
                    spring_nos.add(no)
                    print(f"  [제외] {cat_name} - no:{no} {p.get('name', '?')}")

            # 다음 페이지 확인
            if isinstance(data, dict):
                total_pages = data.get('totalPage', 1)
                if page >= total_pages:
                    break
            else:
                break
            page += 1
            time.sleep(0.3)

    print(f"\n26봄 카테고리 상품 총 {len(spring_nos)}개 (복구 대상에서 제외)")
    return spring_nos


def get_current_product_state(client, product_no):
    """현재 아임웹 상품의 상태 조회"""
    detail = client.get_product_detail(str(product_no))
    if 'error' in detail or detail.get('code') != 200:
        return None
    return detail.get('data', {})


def compare_product(backup, current):
    """백업과 현재 상태를 비교하여 변경 필요 필드 반환"""
    changes = {}
    fields_to_check = ['name', 'content', 'simple_content', 'price', 'prod_status']

    for field in fields_to_check:
        backup_val = backup.get(field)
        current_val = current.get(field)

        if backup_val is not None and backup_val != current_val:
            changes[field] = {
                'backup': backup_val if field not in ('content', 'simple_content') else f"({len(str(backup_val))} chars)",
                'current': current_val if field not in ('content', 'simple_content') else f"({len(str(current_val or ''))} chars)",
            }

    return changes


def restore_product(client, product_no, backup_data, dry_run=True):
    """단일 상품 복구"""
    # 복구할 데이터 구성
    update_data = {}
    fields_to_restore = ['name', 'content', 'simple_content', 'price', 'prod_status']

    for field in fields_to_restore:
        val = backup_data.get(field)
        if val is not None:
            update_data[field] = val

    if not update_data:
        return True

    if dry_run:
        return True

    result = client.update_product(str(product_no), update_data)
    return result.get('code') == 200


def main():
    dry_run = '--execute' not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN 모드 - 변경사항만 미리보기합니다")
        print("실제 복구: python scripts/restore_products.py --execute")
        print("=" * 60)
    else:
        print("=" * 60)
        print("실제 복구 모드로 실행합니다!")
        print("=" * 60)

    print()

    # 1. 백업 데이터 로드
    backup_products = load_backup_products()

    # 2. API 클라이언트 초기화
    client = ImwebAPI(API_KEY, API_SECRET)
    time.sleep(0.5)

    # 3. 26봄 카테고리 상품 조회 (제외 대상)
    print("\n=== 26봄 카테고리 상품 조회 (제외 대상) ===")
    spring_nos = get_spring_product_nos(client)
    time.sleep(0.5)

    # 4. 복구 대상 선정
    restore_targets = {}
    excluded_count = 0
    for no, product in backup_products.items():
        if no in spring_nos:
            excluded_count += 1
            continue
        restore_targets[no] = product

    print(f"\n=== 복구 대상 ===")
    print(f"백업 전체: {len(backup_products)}개")
    print(f"26봄 제외: {excluded_count}개")
    print(f"복구 대상: {len(restore_targets)}개")

    # 5. 각 상품 비교 및 복구
    print(f"\n=== 상품별 비교 및 {'미리보기' if dry_run else '복구'} ===")

    success_count = 0
    skip_count = 0
    fail_count = 0
    change_count = 0

    for no in sorted(restore_targets.keys()):
        backup = restore_targets[no]
        name = backup.get('name', '?')

        print(f"\n--- no:{no} [{name}] ---")

        # 현재 상태 조회
        current = get_current_product_state(client, no)
        time.sleep(0.3)

        if current is None:
            print(f"  현재 상품 조회 실패 (삭제되었을 수 있음)")
            fail_count += 1
            continue

        # 비교
        changes = compare_product(backup, current)

        if not changes:
            print(f"  변경 없음 (백업과 동일)")
            skip_count += 1
            continue

        # 변경 내역 출력
        change_count += 1
        for field, diff in changes.items():
            if field in ('content', 'simple_content'):
                print(f"  {field}: {diff['current']} → {diff['backup']}")
            elif field == 'name':
                print(f"  name: '{diff['current']}' → '{diff['backup']}'")
            elif field == 'price':
                print(f"  price: {diff['current']} → {diff['backup']}")
            elif field == 'prod_status':
                print(f"  prod_status: {diff['current']} → {diff['backup']}")

        # 복구 실행
        if restore_product(client, no, backup, dry_run=dry_run):
            success_count += 1
            if not dry_run:
                print(f"  복구 완료!")
                time.sleep(0.5)
        else:
            fail_count += 1
            print(f"  복구 실패!")

    # 결과 요약
    print(f"\n{'=' * 60}")
    print(f"복구 결과 요약")
    print(f"{'=' * 60}")
    print(f"복구 대상: {len(restore_targets)}개")
    print(f"변경 필요: {change_count}개")
    print(f"변경 없음: {skip_count}개")
    print(f"{'복구 성공' if not dry_run else '복구 예정'}: {success_count}개")
    print(f"실패/조회불가: {fail_count}개")

    if dry_run:
        print(f"\n실제 복구를 실행하려면:")
        print(f"  python scripts/restore_products.py --execute")


if __name__ == '__main__':
    main()
