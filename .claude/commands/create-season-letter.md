# 시즌레터 작성

입력받은 기간의 일정을 Google Calendar에서 조회하고, 지난 레터를 참고하여 시즌 레터 초안을 Obsidian 마크다운 파일로 생성합니다.

## 인자 형식

```
/create-season-letter <시작일> <종료일>
```

예시:
```
/create-season-letter 2026-03-08 2026-03-22
```

- 시작일/종료일: 레터에 포함할 팀 세션 기간 (YYYY-MM-DD)

## 실행 절차

### 0단계: 시즌 및 레터 번호 파악

`/Users/sklee/hfk-imweb/note/공지/` 디렉토리의 파일명을 스캔합니다.

- 파일명 패턴: `{Year} {Season}시즌 레터 #{N}. {Topic}.md`
- 시즌 판단 기준: 봄(3~5월), 여름(6~8월), 가을(9~11월), 겨울(12~2월)
- 인자의 시작일 기준으로 현재 시즌 결정
- 해당 시즌의 최고 레터 번호 확인 → 새 레터 번호 = 최고 번호 + 1

### 1단계: Google Calendar 조회

**해당 기간의 일정 조회:**
```bash
gcalcli --calendar "HFK 캘린더" agenda "<시작일>" "<종료일>" --tsv --details location
```

**회차 계산을 위한 시즌 전체 일정 조회:**
현재 시즌 시작월 1일부터 종료일까지의 `[팀]` 이벤트를 조회합니다.
```bash
gcalcli --calendar "HFK 캘린더" agenda "<시즌시작월1일>" "<종료일>" --tsv --details location
```

TSV 컬럼: `start_date`, `start_time`, `end_date`, `end_time`, `title`, `location`

### 2단계: 일정 파싱 및 그룹핑

1. `[팀]` 이벤트 필터링 → 세션 안내 섹션용
2. `[이벤트]` 이벤트 별도 수집 → 이벤트 안내 섹션용
3. `[게더링]`, `[클럽]` 등은 제외
4. 장소별 그룹핑:
   - location에 "소정동" 포함 → 소정동
   - 그 외 (빈 값 포함) → 오아시스 덕수궁
5. 각 그룹 내 날짜순 → 시간순 정렬
6. 회차 계산: 시즌 전체 일정에서 해당 팀의 이벤트를 날짜순 정렬, 순번 = 회차
7. 각 항목 포맷: `{M}월 {D}일 ({요일}) {HH:MM}-{HH:MM} {팀명} {N}회차`

**중요: 파싱 결과를 사용자에게 보여주고 확인합니다.**
- 장소 매핑이 올바른지
- 회차 번호가 맞는지
- 빠지거나 추가된 팀이 없는지

### 3단계: 지난 레터 참고

`/Users/sklee/hfk-imweb/note/공지/`에서 현재 시즌의 최근 2~3개 레터를 읽습니다.
- 어조와 문체 파악 (따뜻하고 친근하면서 전문적인 톤)
- 이미 다룬 주제 확인
- 현재 시즌 맥락 파악
- 헤더 이미지 URL 확인 (직전 레터에서 가져옴)

### 4단계: 주제 선정 및 콘텐츠 생성

레터 번호에 따른 주제 후보:

| 번호 | 주제 후보 |
|------|----------|
| 1 | 시즌 오픈 (슬랙/카톡 안내, 첫 일정) |
| 2 | 멤버 베네핏 (공간 소개, 폴인, 클럽 신청) |
| 3 | 첫 세션/첫 이벤트 리뷰 |
| 4-6 | 비하인드, 팀 어드벤처, 중간 서베이, 멤버 스포트라이트 |
| 7-8 | 컨퍼런스, 인사이트, 독서의 계절, 시즌 중반 이야기 |
| 9-10 | 다음 시즌 오픈 (재등록 시작) |
| 10-11 | 재등록 마감, 연말파티 예고 |
| 12-13 | 마지막 이벤트, wrap-up, 선물/파티 |

AskUserQuestion으로 주제를 확인한 뒤, 선택된 주제에 맞는 1~3개 콘텐츠 섹션을 작성합니다.
- 지난 레터의 어조를 따름
- 각 섹션은 200~400자 내외
- HFK 커뮤니티 맥락에 맞는 내용

### 5단계: 레터 조립

아래 형식에 맞춰 레터를 조립합니다. (참조: `2025 겨울시즌 레터 #11.md`)

**YAML frontmatter + Obsidian 메타:**
```
---
category: 공지
date: ''
idx: ''
images:
- {헤더이미지URL}
last_synced: ''
status: draft
title: '{Year} {Season}시즌 레터 #{N}. {Topic}'
---

# {Year} {Season}시즌 레터 #{N}. {Topic}

> **카테고리**: 공지
> **작성일**:

---

![](헤더이미지URL)
```

**HTML 본문 구조:**

제목 + 목차:
```html
<p><strong><span style="font-size: 22px;">{Year} {Season}시즌 레터 #{N}. {Topic}</span></strong></p>

<ol>
	<li>{토픽섹션1 제목}</li>
	<li>{토픽섹션2 제목}</li>
	<li>장소별 각 팀 세션 안내</li>
	<li>주요 이벤트 안내</li>
</ol>
```

섹션 구분자:
```html
<p><br></p>
<hr>
<p><br></p>
```

섹션 제목:
```html
<p><strong><span style="font-size: 22px;">{섹션제목}</span></strong></p>
```

장소별 세션 안내 (2열 테이블):
```html
<table style="width: 100%; border-collapse: collapse;">
	<tbody>
		<tr>
			<td style="width: 50%; padding: 15px; vertical-align: top;">

				<p><strong><a href="https://naver.me/59jN0Mvd">오아시스 덕수궁</a></strong></p>
				<p style="font-size: 13px; color: #666;">2016년, 멤버들과 설계부터 제작까지 함께 만들고 채운 공간입니다.</p>
				<hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">

				<ul style="padding-left: 20px; margin: 0; line-height: 1.8;">
					<li>{M월 D일 (요일) HH:MM-HH:MM 팀명 N회차}</li>
				</ul>
			</td>
			<td style="width: 50%; padding: 15px; vertical-align: top;">

				<p><strong><a href="https://naver.me/5Y1r6hsD">[소정동]</a></strong></p>
				<p style="font-size: 13px; color: #666;">덕수궁을 바라보며 창의적인 프로젝트를 진행하기 위해 마련한 공간입니다.</p>
				<hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">

				<ul style="padding-left: 20px; margin: 0; line-height: 1.8;">
					<li>{M월 D일 (요일) HH:MM-HH:MM 팀명 N회차}</li>
				</ul>
			</td>
		</tr>
	</tbody>
</table>
```

이벤트 안내:
```html
<p><strong><span style="font-size: 22px;">주요 이벤트 안내</span></strong></p>

<p>HFK 멤버십은 깊이 있는 성장을 위한 팀 활동, 생산적인 여가를 위한 이벤트 활동으로 구성되어 있으며, 이벤트는 {Season}시즌의 모든 팀 멤버가 신청 가능합니다. ﹒<strong>[신청하기]</strong>버튼을 누르시면 신청 페이지로 이동합니다. 별도의 참석 리마인드 문자는 전송되지 않습니다. ﹒타인의 성장을 위해 전일 취소, 당일 취소, 당일 노쇼는 지양해주세요. 취소시 슬랙 공지에 사유를 댓글로 남겨주세요. 온라인 참석은 어렵습니다.</p>

<p><br></p>

<p style="text-align: center; padding: 20px; background-color: #f5f5f5;">
	<a href="https://hfk.imweb.me" style="display: inline-block; padding: 12px 30px; background-color: #222; color: #fff; text-decoration: none; font-weight: bold; font-size: 14px;">{Season}시즌 이벤트 신청하기</a>
</p>
```

### 6단계: 사용자 확인 및 저장

1. 완성된 초안을 사용자에게 보여주고 리뷰
2. 수정 요청 반영
3. 파일 저장: `/Users/sklee/hfk-imweb/note/공지/{Year} {Season}시즌 레터 #{N}. {Topic}.md`

## 데이터 소스

- Google Calendar: `gcalcli --calendar "HFK 캘린더"` (일정 조회, 장소 확인)
- 지난 레터: `/Users/sklee/hfk-imweb/note/공지/` (스타일 참고, 번호 파악, 헤더 이미지)
- 팀 데이터: `/Users/sklee/hfk-sklee/archive/data/teams_structured_dataset.json` (보조 참고)
- 출력 형식 참조: `2025 겨울시즌 레터 #11.md` (HTML 작성 형식)

## 알려진 한계

- 캘린더 이벤트에 location이 비어있으면 기본 오아시스 덕수궁으로 처리 (실제와 다를 수 있음)
- 회차 번호는 시즌 내 팀별 이벤트 순서로 계산 (취소된 세션이 있으면 번호가 어긋날 수 있음)
- 헤더 이미지 URL은 직전 레터에서 가져오며, 새 이미지가 필요하면 수동 교체 필요
- `idx` 필드는 빈 값 (웹사이트 게시 후 채워짐)
- 콘텐츠 섹션은 AI 초안이므로 반드시 사람이 리뷰 후 게시

$ARGUMENTS
