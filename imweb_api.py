import requests
import json
from typing import Optional, Dict, List


class ImwebAPI:
    """IMWEB API 클라이언트"""

    def __init__(self, api_key: str, api_secret: str):
        """
        IMWEB API 초기화

        Args:
            api_key: IMWEB API Key
            api_secret: IMWEB API Secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.imweb.me/v2"
        self.access_token = None
        self._get_access_token()

    def _get_access_token(self):
        """API Key와 Secret으로 Access Token 발급"""
        url = f"{self.base_url}/auth"

        payload = {
            "key": self.api_key,
            "secret": self.api_secret
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 200 and "access_token" in data:
                self.access_token = data["access_token"]
                print(f"✅ Access Token 발급 성공")
            else:
                print(f"❌ Access Token 발급 실패: {data}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Access Token 발급 중 오류: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """API 요청에 필요한 헤더 생성"""
        return {
            "Content-Type": "application/json",
            "access-token": self.access_token
        }

    def get_products(self, page: int = 1, limit: int = 20, category: Optional[str] = None) -> Dict:
        """
        상품 목록 조회

        Args:
            page: 페이지 번호 (기본값: 1)
            limit: 페이지당 상품 수 (기본값: 20, 최대: 100)
            category: 카테고리 코드 (선택사항)

        Returns:
            상품 목록 데이터
        """
        url = f"{self.base_url}/shop/products"

        params = {
            "page": page,
            "limit": limit
        }

        if category:
            params["category"] = category

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = f"{e} - Response: {response.text[:200]}"
            except:
                pass
            print(f"API 요청 실패: {error_detail}")
            return {"error": error_detail}

    def get_product_detail(self, product_code: str) -> Dict:
        """
        특정 상품의 상세 정보 조회

        Args:
            product_code: 상품 코드

        Returns:
            상품 상세 데이터
        """
        url = f"{self.base_url}/shop/products/{product_code}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return {"error": str(e)}

    def get_categories(self) -> Dict:
        """
        카테고리 목록 조회

        Returns:
            카테고리 목록 데이터
        """
        url = f"{self.base_url}/shop/categories"

        try:
            response = requests.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return {"error": str(e)}

    def search_products(self, keyword: str, page: int = 1, limit: int = 20) -> Dict:
        """
        상품 검색

        Args:
            keyword: 검색 키워드
            page: 페이지 번호
            limit: 페이지당 상품 수

        Returns:
            검색 결과 데이터
        """
        url = f"{self.base_url}/shop/products"

        params = {
            "keyword": keyword,
            "page": page,
            "limit": limit
        }

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = f"{e} - Response: {response.text[:200]}"
            except:
                pass
            print(f"API 요청 실패: {error_detail}")
            return {"error": error_detail}


def main():
    """사용 예제"""
    # IMWEB API 인증 정보 설정
    API_KEY = "your_api_key_here"
    API_SECRET = "your_api_secret_here"

    # API 클라이언트 초기화
    client = ImwebAPI(API_KEY, API_SECRET)

    # 1. 상품 목록 조회
    print("=== 상품 목록 조회 ===")
    products = client.get_products(page=1, limit=10)
    print(json.dumps(products, indent=2, ensure_ascii=False))

    # 2. 카테고리 목록 조회
    print("\n=== 카테고리 목록 조회 ===")
    categories = client.get_categories()
    print(json.dumps(categories, indent=2, ensure_ascii=False))

    # 3. 상품 검색
    print("\n=== 상품 검색 ===")
    search_results = client.search_products(keyword="테스트", limit=5)
    print(json.dumps(search_results, indent=2, ensure_ascii=False))

    # 4. 특정 상품 상세 조회 (상품 코드 필요)
    # product_detail = client.get_product_detail("PRODUCT_CODE")
    # print(json.dumps(product_detail, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
