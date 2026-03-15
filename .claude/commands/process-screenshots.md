# 스크린샷 OCR → 옵시디언 노트 변환

Photos 앱의 스크린샷과 inbox 폴더의 이미지를 OCR 처리하여 옵시디언 노트로 저장합니다.

## 사용법

```
/process-screenshots
```

## 실행 단계

### Step 1: Photos 앱에서 스크린샷 내보내기

AppleScript로 Photos 앱에서 "스크린샷" / "Screenshot" 검색 결과를 inbox 폴더로 내보냅니다.

```bash
INBOX="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Screenshots-inbox"
mkdir -p "$INBOX"
```

```applescript
set exportFolder to POSIX file "<inbox 경로>" as alias
tell application "Photos"
    export (search for "스크린샷") to exportFolder
    export (search for "Screenshot") to exportFolder
end tell
```

### Step 2: 미처리 파일 확인

처리 완료 목록(`~/screenshot-ocr-venv/config/processed.json`)과 inbox 파일을 비교하여 미처리 건수를 사용자에게 보여줍니다.

AskUserQuestion으로 진행 여부를 확인합니다:
- header: "스크린샷 처리"
- question: "N건의 미처리 스크린샷을 OCR 처리할까요?"
- options: "진행", "취소"

### Step 3: OCR 처리 실행

기존 스크립트를 실행합니다:

```bash
source ~/screenshot-ocr-venv/bin/activate && \
cd ~/screenshot-ocr-venv && \
python3 screenshot_to_obsidian.py --process-existing 2>&1
```

### Step 4: 결과 요약

처리 로그(`~/screenshot-ocr-venv/screenshot_ocr.log`)에서 결과를 파싱하여 보고합니다:
- 처리 성공/실패 건수
- 카테고리별 분류 현황 (웹, 채팅, 문서, 설정, 에러, 기타 등)
- 장소 감지된 항목 수
- 리마인더 추가된 항목 수
- 실패한 파일 목록 (있을 경우)

## 경로 정보

| 항목 | 경로 |
|------|------|
| 스크립트 | `~/screenshot-ocr-venv/screenshot_to_obsidian.py` |
| venv | `~/screenshot-ocr-venv/` |
| inbox (모바일) | `~/Library/Mobile Documents/com~apple~CloudDocs/Screenshots-inbox/` |
| 옵시디언 볼트 | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Screenshots/` |
| 처리 로그 | `~/screenshot-ocr-venv/screenshot_ocr.log` |
| 처리 완료 목록 | `~/screenshot-ocr-venv/config/processed.json` |
| 장소 CSV | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Screenshots/locations.csv` |
| Google Sheets | Screenshots 시트 (ID: 1p-R1yU357v0UMSifnB-Gw3gQZuDEqVU2mr30Q4U9xpY) |

## 참고

- Claude Haiku로 OCR + 분류 (카테고리: 코드, 터미널, 채팅, 웹, 문서, 설정, 디자인, 에러, 데이터, 기타)
- 5MB 초과 이미지는 자동 리사이즈 (1600px)
- 장소 감지 시 CSV + Google Sheets 자동 기록
- 리마인더 감지 시 Apple 미리알림 자동 추가
- 이미 처리된 파일은 자동 스킵 (processed.json 기반)
