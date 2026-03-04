# HFK 사진 캘린더 분류

사진 촬영 시간과 HFK 캘린더 일정을 매칭하여 이벤트별로 폴더를 자동 정리합니다.

## 사용법

```
/categorize-images-hfk
```

## 실행

1. source 폴더의 사진 목록을 확인합니다:
   - `$HFK_PHOTOS/`

2. **이미지 리사이즈 (API 제한 대응)**:
   - 모든 사진을 가로 1920px 이하로 리사이즈
   - `sips` 명령어 사용: `sips --resampleWidth 1920 {이미지파일}`
   - 가로가 1920px 이하인 이미지는 건너뜀
   - 리사이즈는 원본 파일을 직접 수정함
   ```bash
   for img in $HFK_PHOTOS/*.{jpg,jpeg,JPG,JPEG,png,PNG,webp,WEBP}; do
     if [ -f "$img" ]; then
       width=$(sips -g pixelWidth "$img" 2>/dev/null | grep pixelWidth | awk '{print $2}')
       if [ -n "$width" ] && [ "$width" -gt 1920 ]; then
         sips --resampleWidth 1920 "$img"
       fi
     fi
   done
   ```

3. 각 사진의 EXIF 데이터에서 촬영 날짜/시간을 추출합니다:
   ```bash
   # macOS에서 EXIF 촬영 시간 추출
   mdls -name kMDItemContentCreationDate "사진파일.jpg"
   # 또는
   exiftool -DateTimeOriginal "사진파일.jpg"
   ```

4. HFK 구글 캘린더에서 일정을 조회합니다:
   ```bash
   cd "$HFK_VAULT" && \
   source "$HFK_SKLEE/.venv/bin/activate" && \
   python scripts/fetch_calendar.py --json --weeks 8
   ```

5. **날짜/시간 매칭**: 사진 촬영 시간과 캘린더 일정을 매칭합니다:
   - 촬영 날짜가 일정 날짜와 동일한 경우 매칭
   - 촬영 시간이 일정 시간 범위 내인 경우 우선 매칭
   - 같은 날 여러 일정이 있으면 시간대로 구분

6. 매칭 결과를 사용자에게 보여주고 확인합니다:
   - 매칭된 일정 목록
   - 매칭되지 않은 사진 목록

7. 확인 후 일정 이름으로 폴더를 생성하고 사진을 이동합니다:
   - 폴더 경로: `$HFK_PHOTOS/photo-calendar/{YYYY-MM-DD}_{이벤트명}/`
   - 원본 사진은 이동 (복사가 아닌 이동)

---

## 폴더 구조

```
$HFK_PHOTOS/
├── (source) 분류할 원본 사진들
│   ├── DSC001.JPG
│   ├── DSC002.JPG
│   └── ...
└── photo-calendar/           # 정리된 사진
    ├── 2025-01-15_영화로운일/
    │   ├── DSC001.JPG
    │   └── DSC002.JPG
    ├── 2025-01-20_넘버앤센스/
    │   └── DSC003.JPG
    └── _unmatched/           # 매칭되지 않은 사진
        └── DSC999.JPG
```

---

## 매칭 규칙

### 날짜 매칭
1. 사진 촬영 날짜 = 캘린더 이벤트 날짜
2. 같은 날 여러 이벤트가 있는 경우:
   - 촬영 시간이 이벤트 시작~종료 시간 사이면 해당 이벤트로 분류
   - 시간이 겹치지 않으면 가장 가까운 이벤트로 분류

### 폴더명 규칙
- 형식: `{YYYY-MM-DD}_{이벤트명}`
- 이벤트명에서 특수문자 제거 (파일시스템 호환)
- 예시: `2025-01-15_영화로운일_3회차`

---

## EXIF 시간 추출 방법

```bash
# 방법 1: mdls (macOS 내장)
mdls -name kMDItemContentCreationDate -raw "photo.jpg"

# 방법 2: sips (macOS 내장)
sips -g creation "photo.jpg"

# 방법 3: exiftool (설치 필요)
exiftool -DateTimeOriginal -s3 "photo.jpg"

# 여러 파일 한번에 조회
for f in *.JPG; do
  echo "$f: $(mdls -name kMDItemContentCreationDate -raw "$f")"
done
```

---

## 사용 예시

```
/categorize-images-hfk

> $HFK_PHOTOS/ 폴더에 48개 사진이 있습니다.

> EXIF 촬영 시간 추출 중...
> - 2025-01-15: 12개 사진
> - 2025-01-18: 20개 사진
> - 2025-01-22: 16개 사진

> HFK 캘린더 일정 조회 중...

> 매칭 결과:
> - 2025-01-15 (수) 19:00 영화로운일 3회차 → 12개 사진
> - 2025-01-18 (토) 14:00 넘버앤센스 OT → 20개 사진
> - 2025-01-22 (수) 19:30 경영브릿지 2회차 → 16개 사진

> 진행하시겠습니까? (Y/N)

> 폴더 생성 및 사진 이동 중...
> - $HFK_PHOTOS/photo-calendar/2025-01-15_영화로운일_3회차/ (12개)
> - $HFK_PHOTOS/photo-calendar/2025-01-18_넘버앤센스_OT/ (20개)
> - $HFK_PHOTOS/photo-calendar/2025-01-22_경영브릿지_2회차/ (16개)

> 완료! 48개 사진이 3개 폴더로 정리되었습니다.
```

---

## 주의사항

- **이미지 리사이즈**: 가로 1920px 초과 이미지는 자동으로 리사이즈됩니다 (원본 파일 수정)
- 원본을 보존하려면 source 폴더에 넣기 전에 별도로 백업하세요
- 사진의 EXIF 데이터에 촬영 시간이 없으면 파일 생성 시간을 사용합니다
- 매칭되지 않는 사진은 `_unmatched` 폴더로 이동됩니다
- 사진은 **이동**(move)되므로 원본 폴더에서 삭제됩니다
- 동일한 폴더명이 이미 존재하면 사진을 추가합니다
- 캘린더 API 키가 유효해야 합니다 (`.env` 파일 설정 필요)

---

## 설정 요구사항

`.env` 파일에 다음 설정이 필요합니다:

```
GOOGLE_API_KEY=your_api_key_here
HFK_CALENDAR_ID=your_calendar_id@group.calendar.google.com
```

---

## 폴더 생성

최초 사용 전 폴더를 생성합니다:

```bash
mkdir -p $HFK_PHOTOS/photo-calendar
```
