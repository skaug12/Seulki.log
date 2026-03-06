#!/usr/bin/env python3
"""
26봄주중, 26봄주말 카테고리 상품의 content에서 날짜 및 텍스트 수정
"""

import sys
import os
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imweb_api import ImwebAPI

# API credentials
API_KEY = '809057085795e753d6135b26c46c559b2ea43f6384'
API_SECRET = '2310801a987b84e7e944ca'


def update_content(content):
    """content의 날짜 및 텍스트 수정"""
    if not content:
        return content, []

    changes = []
    new_content = content

    # 1. 이벤트 섹션 날짜 변경
    # PEST브리핑: 기존 날짜 → 3월 22일 (수)
    pest_pattern = r'(PEST브리핑</strong>\s*<br><span[^>]*><strong>)[^<]+(</strong>)'
    if re.search(pest_pattern, new_content):
        new_content = re.sub(pest_pattern, r'\g<1>3월 22일 (수)\g<2>', new_content)
        changes.append("PEST브리핑 날짜 → 3월 22일 (수)")

    # AAR 밋업: 기존 날짜 → 4월 22일 (수)
    aar_pattern = r'(AAR 밋업[^<]*</strong>\s*<br><span[^>]*><strong>)[^<]+(</strong>)'
    if re.search(aar_pattern, new_content):
        new_content = re.sub(aar_pattern, r'\g<1>4월 22일 (수)\g<2>', new_content)
        changes.append("AAR밋업 날짜 → 4월 22일 (수)")

    # HBR 포럼: 기존 날짜 → 5월 20일 (수)
    hbr_pattern = r'(HBR 포럼</strong>\s*<br><span[^>]*><strong>)[^<]+(</strong>)'
    if re.search(hbr_pattern, new_content):
        new_content = re.sub(hbr_pattern, r'\g<1>5월 20일 (수)\g<2>', new_content)
        changes.append("HBR포럼 날짜 → 5월 20일 (수)")

    # 저자 북토크: "지금 우리에게" 앞에 "매월 진행되며," (bold) 추가
    # 이미 "매월 진행되며"가 있으면 스킵
    if '저자 북토크' in new_content and '매월 진행되며' not in new_content:
        booktalk_pattern = r'(저자 북토크</strong>\s*<br><span[^>]*>)(지금 우리에게)'
        if re.search(booktalk_pattern, new_content):
            new_content = re.sub(booktalk_pattern, r'\1<strong>매월 진행되며,</strong> \2', new_content)
            changes.append("저자북토크에 '매월 진행되며' 추가 (bold)")

    # 2. 첫 세션까지 진행과정 섹션 날짜 변경
    # 3월 2일 (일) or 3월 2일(일) → 3월 1일 (일)
    if re.search(r'3월\s*2일\s*\(일\)', new_content):
        new_content = re.sub(r'3월\s*2일\s*\(일\)', '3월 1일 (일)', new_content)
        changes.append("3월 2일 (일) → 3월 1일 (일)")

    # 3월 5일 (수), 3월 6일 (목) → 3월 4일 (수), 3월 5일 (목)
    if '3월 5일 (수), 3월 6일 (목)' in new_content:
        new_content = new_content.replace('3월 5일 (수), 3월 6일 (목)', '3월 4일 (수), 3월 5일 (목)')
        changes.append("3월 5일 (수), 3월 6일 (목) → 3월 4일 (수), 3월 5일 (목)")

    # 3월 8일(토) or 3월 8일 (토) → 3월 6일 (금)
    if re.search(r'3월\s*8일\s*\(토\)', new_content):
        new_content = re.sub(r'3월\s*8일\s*\(토\)', '3월 6일 (금)', new_content)
        changes.append("3월 8일 (토) → 3월 6일 (금)")

    # 봄 시즌 → 봄시즌 (공백 제거)
    if '봄 시즌' in new_content:
        new_content = new_content.replace('봄 시즌', '봄시즌')
        changes.append("봄 시즌 → 봄시즌")

    return new_content, changes


def update_product(client, product_no, dry_run=True):
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

    print(f"상품명: {name}")
    print(f"Content 길이: {len(content)}")

    if not content:
        print("content가 비어있습니다. 스킵합니다.")
        return False

    # content 업데이트
    new_content, changes = update_content(content)

    if not changes:
        print("변경사항 없음")
        return True

    print(f"변경사항:")
    for change in changes:
        print(f"  - {change}")

    if dry_run:
        print("DRY RUN 모드 - 실제 업데이트하지 않음")
        return True

    # 실제 업데이트
    update_data = {
        'content': new_content
    }

    result = client.update_product(str(product_no), update_data)
    if result.get('code') == 200:
        print(f"상품 업데이트 성공: {name}")
        return True
    else:
        print(f"상품 업데이트 실패: {result}")
        return False


def main():
    client = ImwebAPI(API_KEY, API_SECRET)

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

    if not product_nos:
        print("\n조회된 상품이 없습니다.")
        return

    print(f"\n총 {len(product_nos)}개 상품을 업데이트합니다.")

    # dry_run=True로 먼저 테스트
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("실제 업데이트 모드로 실행합니다!")

    success_count = 0
    fail_count = 0

    for product_no in product_nos:
        try:
            if update_product(client, product_no, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.5)  # API rate limit 방지
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"완료: 성공 {success_count}개, 실패 {fail_count}개")

    if dry_run:
        print("\n실제 업데이트를 하려면 --execute 옵션을 추가하세요:")
        print("   python scripts/update_26spring_dates.py --execute")


if __name__ == '__main__':
    main()
