# Obsidian 마크다운 → Imweb HTML 변환

Obsidian 마크다운(.md) 파일을 읽어 Imweb NOTE 게시판에 붙여넣을 수 있는 HTML 코드로 변환합니다.

## 인자 형식

```
/convert-to-imweb <파일경로>
```

예시:
```
/convert-to-imweb /Users/sklee/hfk-imweb/note/공지/2026 봄시즌 레터 #1. 시즌 오픈.md
```

- 파일경로: 변환할 Obsidian .md 파일의 절대경로

## 실행 절차

### 1단계: 파일 읽기 및 파싱

$ARGUMENTS에서 파일 경로를 추출하여 파일을 읽습니다.

파일 구조:
```
---
category: 공지
date: ''
idx: ''
images:
- https://cdn.imweb.me/...
status: draft
title: '...'
---

# 제목

> **카테고리**: 공지
> **작성일**:

---

![](이미지URL)

{본문 콘텐츠}
```

1. YAML frontmatter (`---` ~ `---`) 파싱 → title, images, category 추출
2. Obsidian 메타 블록 분리 (H1 제목, blockquote 메타, `---` 구분선, 헤더 이미지)
3. 본문 콘텐츠 추출

### 2단계: 본문 콘텐츠 분류

본문이 이미 HTML인지 마크다운인지 판별합니다.

- `<p>`, `<table>`, `<div>` 등 HTML 태그가 포함 → **HTML 모드** (이미 변환된 콘텐츠)
- HTML 태그 없이 순수 마크다운 → **마크다운 모드** (변환 필요)
- 혼합 → **혼합 모드** (마크다운 부분만 변환)

### 3단계: 마크다운 → HTML 변환

마크다운 모드 또는 혼합 모드일 때, 아래 규칙으로 변환합니다.

**Imweb HTML 변환 규칙:**

| 마크다운 | Imweb HTML |
|---------|-----------|
| `# 제목` | `<p><strong><span style="font-size: 26px;">{제목}</span></strong></p>` |
| `## 제목` | `<p><strong><span style="font-size: 22px;">{제목}</span></strong></p>` |
| `### 제목` | `<p><strong><span style="font-size: 18px;">{제목}</span></strong></p>` |
| `**굵게**` | `<strong>{텍스트}</strong>` |
| `*기울임*` | `<em>{텍스트}</em>` |
| `[링크](URL)` | `<a href="URL">{링크텍스트}</a>` |
| `![](이미지URL)` | `<p><img src="이미지URL" style="width: 100%;"></p>` |
| `- 리스트` | `<ul><li>{항목}</li></ul>` |
| `1. 순서` | `<ol><li>{항목}</li></ol>` |
| `> 인용` | `<blockquote><p>{텍스트}</p></blockquote>` |
| `---` | `<p><br></p><hr><p><br></p>` |
| 빈 줄 | `<p><br></p>` |
| 일반 텍스트 | `<p>{텍스트}</p>` |

**스타일 기본값:**
- 본문 텍스트: `font-size: 16px; color: #333; line-height: 1.8;`
- H2 제목에는 섹션 구분선 추가: `<p><br></p><hr><p><br></p>` (앞에)
- 이미지: `width: 100%` (반응형)

### 4단계: HTML 코드 출력

변환 결과를 두 가지 형태로 출력합니다:

**A. Imweb 게시용 HTML (본문만)**
- YAML frontmatter, Obsidian 메타 블록 제외
- 순수 HTML 본문만 출력
- Imweb NOTE 에디터의 "코드 보기" 모드에 붙여넣기 가능

**B. 전체 Obsidian 파일 (HTML 본문 포함)**
- 기존 .md 파일의 마크다운 본문을 HTML로 교체한 버전
- YAML frontmatter 유지
- Obsidian 메타 블록 유지

AskUserQuestion으로 출력 방식을 확인합니다:
- header: "출력 방식"
- options:
  - "HTML만 출력" — Imweb에 바로 붙여넣을 HTML 코드만 화면에 표시
  - "파일 덮어쓰기" — 원본 .md 파일의 본문을 HTML로 교체하여 저장
  - "새 파일 저장" — `{원본파일명}_imweb.html`로 별도 저장

### 5단계: 결과 확인

- 변환된 HTML을 사용자에게 보여줍니다
- 수정 요청이 있으면 반영합니다

## 참고

- Imweb 에디터는 Froala 기반이므로 `class="fr-fic fr-dii"` 속성이 이미지에 필요할 수 있음
- 기존 HTML이 포함된 파일(예: `status: draft` 레터)은 HTML 모드로 자동 처리되어 변환 없이 추출만 수행
- 변환 참조 형식: `/Users/sklee/hfk-imweb/note/공지/2025 겨울시즌 레터 #11.md`

$ARGUMENTS
