"""
IMWEB API 연결 테스트
"""

import os
from dotenv import load_dotenv
from imweb_api import ImwebAPI
import json

# 환경 변수 로드
load_dotenv()

# API 클라이언트 초기화
api_key = os.getenv('IMWEB_API_KEY')
api_secret = os.getenv('IMWEB_API_SECRET')

print("=" * 60)
print("  IMWEB API 연결 테스트")
print("=" * 60)
print(f"\nAPI Key: {api_key[:20]}...")
print(f"Secret Key: {api_secret[:10]}...")

client = ImwebAPI(api_key, api_secret)

# 1. 카테고리 조회 테스트
print("\n\n[1] 카테고리 목록 조회 중...")
categories = client.get_categories()
if "error" not in categories:
    print("✅ 카테고리 조회 성공!")
    print(json.dumps(categories, indent=2, ensure_ascii=False))
else:
    print(f"❌ 오류: {categories['error']}")

# 2. 상품 목록 조회 테스트
print("\n\n[2] 상품 목록 조회 중 (최대 5개)...")
products = client.get_products(page=1, limit=5)
if "error" not in products:
    print("✅ 상품 조회 성공!")
    print(json.dumps(products, indent=2, ensure_ascii=False))

    if "data" in products and "list" in products["data"]:
        product_list = products["data"]["list"]
        total = products["data"].get("total", 0)
        print(f"\n📊 조회된 상품: {len(product_list)}개")
        print(f"📊 전체 상품: {total}개")

        if product_list:
            print("\n상품 목록:")
            for idx, product in enumerate(product_list, 1):
                prod_name = product.get('name', 'N/A')
                prod_code = product.get('prod_code', 'N/A')
                price = product.get('price', 0)
                print(f"  {idx}. {prod_name} (코드: {prod_code}, 가격: {price:,}원)")
else:
    print(f"❌ 오류: {products['error']}")

print("\n" + "=" * 60)
print("  테스트 완료!")
print("=" * 60)
