"""
IMWEB 모든 상품 데이터를 JSON 파일로 저장
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from imweb_api import ImwebAPI

# 환경 변수 로드
load_dotenv()

def export_all_products():
    """모든 상품 데이터를 JSON 파일로 저장"""

    # API 클라이언트 초기화
    api_key = os.getenv('IMWEB_API_KEY')
    api_secret = os.getenv('IMWEB_API_SECRET')

    if not api_key or not api_secret:
        print("❌ API 인증 정보가 설정되지 않았습니다.")
        return

    print("=" * 70)
    print("  IMWEB 모든 상품 데이터 내보내기")
    print("=" * 70)

    client = ImwebAPI(api_key, api_secret)

    all_products = []
    page = 1
    limit = 50  # 한 번에 50개씩 가져오기

    print(f"\n📦 상품 데이터 조회 시작...\n")

    while True:
        print(f"페이지 {page} 조회 중...", end=" ")

        products_response = client.get_products(page=page, limit=limit)

        if "error" in products_response:
            print(f"\n❌ 오류 발생: {products_response['error']}")
            break

        if "data" not in products_response:
            print(f"\n⚠️  'data' 키가 없습니다. 현재까지 {len(all_products)}개 저장됨")
            break

        data = products_response["data"]

        # data가 딕셔너리가 아니면 리스트일 수 있음
        if isinstance(data, list):
            product_list = data
        elif isinstance(data, dict) and "list" in data:
            product_list = data["list"]
        else:
            print(f"\n⚠️  예상치 못한 데이터 형식. 현재까지 {len(all_products)}개 저장됨")
            break

        if not product_list:
            print("완료 (더 이상 데이터 없음)")
            break

        all_products.extend(product_list)
        print(f"✅ {len(product_list)}개 상품 조회됨 (누적: {len(all_products)}개)")

        # 페이징 정보 확인 (data가 딕셔너리일 때만)
        if isinstance(data, dict) and "pagenation" in data:
            pagenation = data["pagenation"]
            total_count = int(pagenation.get("data_count", 0))
            current_page = int(pagenation.get("current_page", page))
            total_page = int(pagenation.get("total_page", 0))

            print(f"   → 진행률: {current_page}/{total_page} 페이지 ({len(all_products)}/{total_count})")

            # 모든 상품을 가져왔는지 확인
            if len(all_products) >= total_count or current_page >= total_page:
                print("\n✅ 모든 상품 조회 완료!")
                break

        # API 호출 제한을 피하기 위한 짧은 지연
        time.sleep(0.5)
        page += 1

    if not all_products:
        print("\n❌ 조회된 상품이 없습니다.")
        return

    # JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"imweb_products_{timestamp}.json"

    print(f"\n💾 파일 저장 중: {filename}")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print(f"✅ 저장 완료!")

    # 요약 정보 출력
    print("\n" + "=" * 70)
    print("  저장 완료")
    print("=" * 70)
    print(f"📊 총 상품 수: {len(all_products)}개")
    print(f"📁 파일명: {filename}")

    # 파일 크기 확인
    file_size = os.path.getsize(filename)
    if file_size < 1024:
        size_str = f"{file_size} bytes"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"

    print(f"📏 파일 크기: {size_str}")

    # 상품 정보 샘플 출력
    print(f"\n📦 상품 예시 (처음 5개):")
    for idx, product in enumerate(all_products[:5], 1):
        name = product.get('name', 'N/A')
        price = product.get('price', 0)
        category = product.get('custom_prod_code', 'N/A')
        print(f"  {idx}. {name} - {price:,}원 (코드: {category})")

    # 추가 통계
    print(f"\n📈 가격 통계:")
    prices = [p.get('price', 0) for p in all_products if p.get('price')]
    if prices:
        print(f"   최저가: {min(prices):,}원")
        print(f"   최고가: {max(prices):,}원")
        print(f"   평균가: {sum(prices) // len(prices):,}원")

    print("\n" + "=" * 70)

    # CSV 파일로도 저장할지 물어보기
    print("\n💡 팁: CSV 파일로도 저장하려면 'python export_to_csv.py' 를 실행하세요")

    return filename

if __name__ == "__main__":
    try:
        export_all_products()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
