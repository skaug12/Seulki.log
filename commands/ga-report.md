# GA4 월별 페이지 리포트

Google Analytics 4에서 페이지별 조회수, 방문자 수, 세션 수, 이벤트 수를 월별로 조회하여 CSV 파일로 저장합니다.

## 인자 형식

```
/ga4-report <시작일> <종료일>
```

예시:
```
/ga4-report 2025-01-01 2025-12-31
/ga4-report 2025-06-01 today
```

- 시작일: YYYY-MM-DD 형식
- 종료일: YYYY-MM-DD 형식 또는 `today`

## 실행 절차

### 1단계: 인자 확인

1. `$ARGUMENTS`에서 시작일과 종료일을 파싱합니다.
2. 인자가 없거나 형식이 잘못되면 사용자에게 기간을 질문합니다.

### 2단계: Google 인증 확인

다음 명령어로 토큰 상태를 확인합니다:

```bash
cd "$HFK_VAULT" && python scripts/google_auth.py --check
```

- 토큰이 없으면 사용자에게 `python scripts/google_auth.py` 실행을 안내합니다.
- **주의**: Analytics 스코프가 처음이면 재인증이 필요합니다.

### 3단계: 리포트 조회 및 CSV 저장

CSV 파일명은 `ga4_report_<시작일>_<종료일>.csv` 형식입니다.

```bash
cd "$HFK_VAULT" && python scripts/ga4_monthly_report.py --start <시작일> --end <종료일> --csv "data/ga4_report_<시작일>_<종료일>.csv"
```

### 4단계: 결과 보고

터미널 출력과 CSV 파일을 바탕으로 사용자에게 결과를 요약합니다:

1. **월별 요약 테이블**:

| 월 | 총 조회수 | 총 방문자 | 총 세션 |
|----|----------|----------|--------|

2. **월별 상위 페이지 TOP 5** (조회수 기준)

3. CSV 저장 경로 안내

## 출력 지표

| 지표 | 설명 |
|------|------|
| 조회수 (screenPageViews) | 페이지가 표시된 횟수 |
| 방문자 수 (totalUsers) | 순 방문자 수 |
| 세션 수 (sessions) | 방문 세션 수 |
| 이벤트 수 (eventCount) | 총 이벤트(클릭 포함) 수 |

## 필요 설정

- `.env`에 `GA4_PROPERTY_ID` 설정 필요
- Google Cloud Console에서 **Google Analytics Data API** 활성화 필요
- OAuth 토큰에 `analytics.readonly` 스코프 포함 필요

## 참고

- 스크립트: `scripts/ga4_monthly_report.py`
- 인증: `scripts/google_auth.py`
- 토큰: `.google_token.json`
- CSV 저장 위치: `data/` 디렉토리

$ARGUMENTS
