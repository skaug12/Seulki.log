# HFK-SKLEE - IMWEB API 연동 프로젝트

IMWEB 쇼핑몰의 상품 데이터를 Python으로 가져오고 관리하는 프로젝트입니다.

## 📁 프로젝트 구조

```
hfk-sklee/
├── .env                    # API 인증 정보 (보안 - Git 제외)
├── .env.example           # 환경 변수 템플릿
├── .gitignore             # Git 제외 파일 목록
├── README.md              # 프로젝트 문서
├── requirements.txt       # Python 패키지 의존성
├── imweb_api.py          # IMWEB API 클라이언트 라이브러리
├── venv/                  # Python 가상 환경
├── data/                  # 내보낸 상품 데이터 (JSON)
│   └── imweb_products_*.json
└── scripts/               # 실행 스크립트
    ├── example.py                 # 대화형 예제
    ├── test_connection.py         # API 연결 테스트
    ├── export_all_products.py     # 모든 상품 내보내기
    └── export_products_debug.py   # 디버그 모드 내보내기
```

## 🚀 빠른 시작

### 1. 가상 환경 활성화

```bash
source venv/bin/activate
```

### 2. 패키지 설치 (이미 설치됨)

```bash
pip install -r requirements.txt
```

### 3. API 인증 정보 확인

`.env` 파일에 IMWEB API 인증 정보가 설정되어 있습니다.

### 4. 스크립트 실행

#### API 연결 테스트
```bash
python scripts/test_connection.py
```

#### 모든 상품 데이터 내보내기
```bash
python scripts/export_products_debug.py
```

#### 대화형 예제 실행
```bash
python scripts/example.py
```

## 📚 주요 기능

### ImwebAPI 클라이언트

`imweb_api.py`는 IMWEB API와 통신하기 위한 Python 클라이언트입니다.

```python
from imweb_api import ImwebAPI
import os
from dotenv import load_dotenv

load_dotenv()

# API 클라이언트 초기화
client = ImwebAPI(
    api_key=os.getenv('IMWEB_API_KEY'),
    api_secret=os.getenv('IMWEB_API_SECRET')
)

# 상품 목록 조회
products = client.get_products(page=1, limit=20)

# 상품 검색
results = client.search_products(keyword="검색어", limit=10)

# 특정 상품 상세 정보
product = client.get_product_detail("상품코드")

# 카테고리 목록 조회
categories = client.get_categories()
```

## 📊 데이터 현황

- **전체 상품 수**: 160개
- **최근 내보내기**: `data/imweb_products_20260122_171322.json`
- **파일 크기**: 7.4 MB

## 🛠️ 개발 가이드

### API 클라이언트 수정

`imweb_api.py`를 수정하여 새로운 API 엔드포인트를 추가할 수 있습니다.

### 새 스크립트 추가

`scripts/` 디렉토리에 새로운 Python 스크립트를 추가할 수 있습니다.

```python
# scripts/my_script.py
import sys
sys.path.append('..')  # 상위 디렉토리의 imweb_api.py 접근

from imweb_api import ImwebAPI
# ... 코드 작성
```

## ⚠️ 주의사항

### API 호출 제한

IMWEB API는 호출 빈도 제한이 있을 수 있습니다. 대량 데이터를 조회할 때는:
- 페이지당 20~50개 제한 권장
- 각 요청 사이 0.5~1초 지연 추가

### 보안

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API Key와 Secret은 안전하게 보관하세요

## 📖 IMWEB API 문서

- [IMWEB 개발자 센터](https://developers.imweb.me/)
- [API 인증 가이드](https://old-developers.imweb.me/getstarted/token)

## 🔧 문제 해결

### 인증 오류 (401, -2)
- API Key와 Secret이 정확한지 확인
- Access Token 발급이 성공했는지 확인

### 데이터 조회 실패
- 네트워크 연결 확인
- API 호출 제한에 걸렸는지 확인 (지연 추가)

### 가상 환경 활성화 안됨
```bash
# 가상 환경 재생성
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 버전 히스토리

### v1.0.0 (2026-01-22)
- ✅ IMWEB API 클라이언트 구현
- ✅ Access Token 자동 발급
- ✅ 상품 데이터 조회 및 내보내기
- ✅ 페이징 처리 및 API 호출 제한 대응
- ✅ 160개 상품 데이터 수집 완료

## 👤 작성자

HFK-SKLEE

## 📄 라이선스

이 프로젝트는 개인 프로젝트입니다.
