# HFK 콘텐츠 제작 에이전트

이벤트 후기 생성부터 아임웹 HTML 변환까지 콘텐츠 제작 워크플로우를 실행합니다.

## 사용법

```
/run-content-ops [녹취파일경로]
```

## 실행 워크플로우

### Step 1: 녹취 기반 후기 생성 (generate-event-review 또는 generate-team-review)

1. $ARGUMENTS에서 녹취 파일 경로를 확인합니다
2. 사용자에게 리뷰 유형을 질문합니다:
   - **이벤트 리뷰** → `/generate-event-review` 실행
   - **팀 리뷰** → `/generate-team-review` 실행
3. HFK 작성 원칙에 따라 후기를 생성합니다
4. `$HFK_VAULT/note/리뷰/` 에 Markdown 파일로 저장

**사용자 확인**: 생성된 후기 내용 검토

### Step 2: HTML 변환 (convert-to-imweb) [선택]

사용자에게 아임웹 HTML로 변환할지 질문합니다:
- "예" → Markdown을 아임웹 NOTE 게시판용 HTML로 변환
  - YAML frontmatter 처리
  - 스타일링 적용
  - 결과 HTML을 클립보드에 복사하거나 파일로 저장
- "아니오" → 종료

## 인자 없이 실행한 경우

녹취 파일 경로가 없으면:
1. 사용자에게 녹취 파일 경로를 질문합니다
2. 또는 기존 `note/리뷰/` 파일 중 HTML 변환이 필요한 것을 선택

## 완료 요약

- 생성된 후기 파일 경로
- 변환된 HTML (있는 경우)

$ARGUMENTS
