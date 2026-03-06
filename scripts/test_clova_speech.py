#!/usr/bin/env python3
"""CLOVA Speech API 연결 테스트 스크립트"""

import sys
import os

# 상위 디렉토리 모듈 import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from clova_speech_api import ClovaSpeechAPI

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


def main():
    print("=" * 50)
    print("CLOVA Speech API 연결 테스트")
    print("=" * 50)

    # 환경 변수 확인
    api_key = os.getenv('CLOVA_SPEECH_API_KEY')
    invoke_url = os.getenv('CLOVA_SPEECH_INVOKE_URL')

    print(f"\nAPI Key: {api_key[:20]}..." if api_key else "API Key: 설정되지 않음")
    print(f"Invoke URL: {invoke_url}" if invoke_url else "Invoke URL: 기본값 사용")

    if not api_key:
        print("\n.env 파일에 CLOVA_SPEECH_API_KEY를 설정해주세요.")
        return

    # API 클라이언트 초기화
    client = ClovaSpeechAPI(api_key, invoke_url)

    # 연결 테스트
    print("\n" + "-" * 50)
    print("API 연결 테스트 시작...")
    print("-" * 50)

    if client.test_connection():
        print("\nCLOVA Speech API 연결 성공!")
        print("\n사용 가능한 기능:")
        print("  - recognize_url(): URL로 음성 파일 인식")
        print("  - recognize_file(): 로컬 파일 음성 인식")
        print("  - recognize_with_speakers(): 화자 분리 포함 인식")
    else:
        print("\nCLOVA Speech API 연결 실패")
        print("\n확인 사항:")
        print("  1. API Key가 올바른지 확인")
        print("  2. Invoke URL이 올바른지 확인")
        print("  3. 네이버 클라우드 플랫폼에서 CLOVA Speech 서비스 활성화 여부 확인")


if __name__ == "__main__":
    main()
