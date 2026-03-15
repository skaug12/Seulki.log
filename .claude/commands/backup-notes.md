# HFK NOTE 백업

thehfk.org의 NOTE 게시판 글을 Obsidian에 백업합니다.

## 사용법

```
/backup-notes
```

## 실행

1. 사용자에게 백업 범위를 질문합니다:
   - 전체 백업 (모든 게시글)
   - 최근 N개만 백업

2. 확인 후 백업 스크립트를 실행합니다:
   ```bash
   cd "$HFK_VAULT" && \
   source "$HFK_SKLEE/.venv/bin/activate" && \
   python scripts/backup_notes.py --execute
   ```

3. 실행 결과를 사용자에게 알려줍니다.

---

## 스크립트 동작

### 백업 프로세스
1. thehfk.org/note 페이지에서 모든 게시글 ID 수집 (최대 20페이지)
2. 각 게시글 상세 페이지 접근하여 정보 추출:
   - 제목, 카테고리, 작성일
   - 본문 내용 (HTML → Markdown 변환)
   - 이미지 URL (최대 10개)
3. 공지/리뷰 카테고리로 분류
4. Markdown 파일로 저장

### 저장 위치
- 공지: `note/공지/`
- 리뷰: `note/리뷰/`

### 파일명 형식
- `{날짜}_{제목}.md`
- 예: `20250115_AAR밋업_보난자커피.md`

---

## 생성되는 노트 구조

```markdown
---
idx: '게시글ID'
title: '제목'
category: '공지' 또는 '리뷰'
date: '2025.01.15'
status: synced
last_synced: '2025-01-29 10:00:00'
images:
  - https://cdn.imweb.me/...
---

# 제목

> **카테고리**: 공지
> **작성일**: 2025.01.15

---

본문 내용...

![](이미지URL)

...
```

---

## 주의사항

- 아임웹 게시판 API가 없어 **웹 스크래핑** 방식으로 수집합니다
- Obsidian → 아임웹 동기화는 **불가능**합니다 (읽기 전용)
- 새 게시글 작성은 아임웹 관리자에서 직접 해야 합니다
- 기존 파일이 있으면 덮어씁니다
- Rate limiting으로 인해 전체 백업 시 시간이 걸릴 수 있습니다

---

## 결과 확인

백업 완료 후 Obsidian에서 확인:
1. `/note/공지/` 또는 `/note/리뷰/` 폴더 열기
2. 각 노트의 frontmatter에서 `last_synced` 날짜 확인

---

## iCloud 동기화 지연 해결

생성된 파일이 Obsidian에서 안 보이는 경우:
1. Finder에서 `/note/리뷰/` 폴더 열기 (동기화 유도)
2. Obsidian에서 `Cmd + R`로 새로고침
3. 또는 Obsidian 재시작
