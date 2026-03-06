import requests
import json
import time
from typing import Optional, Dict, List


class ClovaSpeechAPI:
    """CLOVA Speech API 클라이언트 (음성 인식/STT)"""

    def __init__(self, api_key: str, invoke_url: Optional[str] = None):
        """
        CLOVA Speech API 초기화

        Args:
            api_key: CLOVA Speech API Secret Key
            invoke_url: CLOVA Speech Invoke URL (선택, 기본값 사용 가능)
        """
        self.api_key = api_key
        self.invoke_url = invoke_url or "https://clovaspeech-gw.ncloud.com/recog/v1/stt"

    def _get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        return {
            "Content-Type": "application/json",
            "X-CLOVASPEECH-API-KEY": self.api_key
        }

    def recognize_url(self, audio_url: str, language: str = "ko-KR",
                      completion: str = "sync") -> Dict:
        """
        URL로 음성 파일 인식

        Args:
            audio_url: 음성 파일 URL
            language: 인식 언어 (ko-KR, en-US, ja, zh-cn 등)
            completion: 처리 방식 (sync: 동기, async: 비동기)

        Returns:
            인식 결과
        """
        url = f"{self.invoke_url}/recognizer/url"

        payload = {
            "url": audio_url,
            "language": language,
            "completion": completion
        }

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = f"{e} - Response: {response.text[:500]}"
            except:
                pass
            print(f"API 요청 실패: {error_detail}")
            return {"error": error_detail}

    def recognize_file(self, file_path: str, language: str = "ko-KR",
                       completion: str = "sync") -> Dict:
        """
        로컬 파일로 음성 인식

        Args:
            file_path: 로컬 음성 파일 경로
            language: 인식 언어
            completion: 처리 방식

        Returns:
            인식 결과
        """
        url = f"{self.invoke_url}/recognizer/upload"

        headers = {
            "X-CLOVASPEECH-API-KEY": self.api_key
        }

        params = {
            "language": language,
            "completion": completion
        }

        try:
            with open(file_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    files=files
                )
            response.raise_for_status()
            return response.json()
        except FileNotFoundError:
            return {"error": f"파일을 찾을 수 없습니다: {file_path}"}
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = f"{e} - Response: {response.text[:500]}"
            except:
                pass
            print(f"API 요청 실패: {error_detail}")
            return {"error": error_detail}

    def recognize_with_speakers(self, audio_url: str, language: str = "ko-KR",
                                 enable_diarization: bool = True,
                                 speaker_count: int = 2) -> Dict:
        """
        화자 분리 포함 음성 인식

        Args:
            audio_url: 음성 파일 URL
            language: 인식 언어
            enable_diarization: 화자 분리 활성화
            speaker_count: 예상 화자 수

        Returns:
            화자별 인식 결과
        """
        url = f"{self.invoke_url}/recognizer/url"

        payload = {
            "url": audio_url,
            "language": language,
            "completion": "sync",
            "diarization": {
                "enable": enable_diarization,
                "speakerCountMin": 1,
                "speakerCountMax": speaker_count
            }
        }

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = f"{e} - Response: {response.text[:500]}"
            except:
                pass
            print(f"API 요청 실패: {error_detail}")
            return {"error": error_detail}

    def test_connection(self) -> bool:
        """
        API 연결 테스트

        Returns:
            연결 성공 여부
        """
        print("CLOVA Speech API 연결 테스트 중...")

        # 간단한 헤더 검증을 위한 요청
        url = f"{self.invoke_url}/recognizer/url"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json={"url": "", "language": "ko-KR"}
            )

            # 400 에러는 파라미터 오류로 API 키는 유효함
            if response.status_code in [200, 400]:
                print("API 키 인증 성공")
                return True
            elif response.status_code == 401:
                print("API 키 인증 실패: 유효하지 않은 API 키")
                return False
            else:
                print(f"연결 테스트 결과: {response.status_code}")
                print(f"응답: {response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"연결 실패: {e}")
            return False


def main():
    """사용 예제"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # API 클라이언트 초기화
    api_key = os.getenv('CLOVA_SPEECH_API_KEY')
    invoke_url = os.getenv('CLOVA_SPEECH_INVOKE_URL')

    if not api_key:
        print("CLOVA_SPEECH_API_KEY가 설정되지 않았습니다.")
        print(".env 파일에 CLOVA_SPEECH_API_KEY를 추가해주세요.")
        return

    client = ClovaSpeechAPI(api_key, invoke_url)

    # 1. 연결 테스트
    print("=== API 연결 테스트 ===")
    if client.test_connection():
        print("연결 성공!")
    else:
        print("연결 실패")
        return

    # 2. URL로 음성 인식 예제 (실제 URL 필요)
    # audio_url = "https://example.com/audio.mp3"
    # result = client.recognize_url(audio_url)
    # print(json.dumps(result, indent=2, ensure_ascii=False))

    # 3. 로컬 파일 음성 인식 예제 (실제 파일 필요)
    # result = client.recognize_file("audio.mp3")
    # print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
