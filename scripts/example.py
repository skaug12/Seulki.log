"""
IMWEB API 사용 예제
환경 변수를 사용하여 안전하게 API 인증 정보를 관리합니다
"""

import os
import json
from dotenv import load_dotenv
from imweb_api import ImwebAPI


def print_section(title: str):
    """섹션 제목 출력"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    # .env 파일에서 환경 변수 로드
    load_dotenv()

    # API 인증 정보 가져오기
    api_key = os.getenv('IMWEB_API_KEY')
    api_secret = os.getenv('IMWEB_API_SECRET')

    # 인증 정보 확인
    if not api_key or not api_secret:
        print("❌ 오류: IMWEB API 인증 정보가 설정되지 않았습니다.")
        print("📝 .env 파일을 생성하고 다음 정보를 입력하세요:")
        print("   IMWEB_API_KEY=your_api_key")
        print("   IMWEB_API_SECRET=your_api_secret")
        return

    # API 클라이언트 초기화
    client = ImwebAPI(api_key, api_secret)

    # 예제 1: 카테고리 목록 조회
    print_section("1. 카테고리 목록 조회")
    categories = client.get_categories()
    if "error" not in categories:
        print(json.dumps(categories, indent=2, ensure_ascii=False))
    else:
        print(f"오류: {categories['error']}")

    # 예제 2: 상품 목록 조회 (첫 페이지, 10개)
    print_section("2. 상품 목록 조회 (10개)")
    products = client.get_products(page=1, limit=10)
    if "error" not in products:
        print(json.dumps(products, indent=2, ensure_ascii=False))

        # 상품 개수 표시
        if "data" in products and "list" in products["data"]:
            product_count = len(products["data"]["list"])
            total = products["data"].get("total", 0)
            print(f"\n✅ {product_count}개 상품 조회됨 (전체: {total}개)")
    else:
        print(f"오류: {products['error']}")

    # 예제 3: 상품 검색
    print_section("3. 상품 검색 예제")
    keyword = input("검색할 상품명을 입력하세요 (엔터: 건너뛰기): ").strip()
    if keyword:
        search_results = client.search_products(keyword=keyword, limit=5)
        if "error" not in search_results:
            print(json.dumps(search_results, indent=2, ensure_ascii=False))
        else:
            print(f"오류: {search_results['error']}")
    else:
        print("검색을 건너뜁니다.")

    # 예제 4: 특정 상품 상세 조회
    print_section("4. 특정 상품 상세 조회")
    product_code = input("조회할 상품 코드를 입력하세요 (엔터: 건너뛰기): ").strip()
    if product_code:
        product_detail = client.get_product_detail(product_code)
        if "error" not in product_detail:
            print(json.dumps(product_detail, indent=2, ensure_ascii=False))
        else:
            print(f"오류: {product_detail['error']}")
    else:
        print("상품 상세 조회를 건너뜁니다.")

    # 예제 5: 모든 상품 가져오기 (페이징 처리)
    print_section("5. 모든 상품 가져오기 (페이징)")
    fetch_all = input("모든 상품을 가져오시겠습니까? (y/n): ").strip().lower()
    if fetch_all == 'y':
        all_products = []
        page = 1
        limit = 20

        while True:
            print(f"페이지 {page} 조회 중...")
            products = client.get_products(page=page, limit=limit)

            if "error" in products:
                print(f"오류: {products['error']}")
                break

            if "data" not in products or "list" not in products["data"]:
                print("데이터 형식이 올바르지 않습니다.")
                break

            product_list = products["data"]["list"]
            if not product_list:
                break

            all_products.extend(product_list)

            # 전체 상품 수 확인
            total = products["data"].get("total", 0)
            if len(all_products) >= total:
                break

            page += 1

        print(f"\n✅ 총 {len(all_products)}개 상품을 가져왔습니다.")

        # 결과를 파일로 저장
        save = input("결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            filename = "imweb_products.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, indent=2, ensure_ascii=False)
            print(f"✅ {filename} 파일에 저장되었습니다.")
    else:
        print("모든 상품 가져오기를 건너뜁니다.")

    print_section("완료")
    print("프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
