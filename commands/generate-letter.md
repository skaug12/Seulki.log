# HFK 시즌레터 생성

공지 볼트의 레터 템플릿을 기반으로 HFK(Harvard Business Review Forum Korea) 시즌레터를 자동 생성합니다.

## 사용법

```
/generate-letter [시즌] [레터번호] [제목]
```

예시:
```
/generate-letter 2025겨울 8 겨울의 한 가운데
```

## 실행

$ARGUMENTS를 파싱하여 시즌레터를 생성합니다.

1. 인자를 파싱합니다: [시즌] [레터번호] [제목]
2. 사용자에게 레터에 포함할 섹션 주제들을 질문합니다 (목차 구성)
3. 각 섹션별 내용을 질문하거나 기존 정보를 활용합니다
4. **팀 세션 안내 섹션이 있으면**: 구글 캘린더 API로 일정을 자동 조회합니다
5. 아래 템플릿과 작성 원칙에 따라 시즌레터를 생성합니다
6. 결과를 HTML 형식으로 출력합니다

---

## 구글 캘린더 연동

팀 세션 안내 섹션은 구글 캘린더 API를 통해 자동으로 일정을 가져올 수 있습니다.

### 캘린더 일정 조회

MCP Google Calendar 도구를 사용합니다:
- `list-events`: 기간 내 이벤트 목록 조회
- `search-events`: 팀명 키워드로 검색

### 자동 일정 조회 로직

- **지난 일정 제외**: 오늘 날짜 기준으로 과거 일정은 표시하지 않음
- **1주 단위 조회**: 기본적으로 오늘부터 7일간의 일정을 가져옴
- **장소 자동 분류**: 일정 제목/장소에 "오아시스", "덕수궁", "소정동" 등의 키워드가 있으면 자동 분류

### 스킬 실행 시 동작

팀 세션 안내 섹션을 포함하는 경우:

1. MCP `list-events` 도구로 해당 기간의 HFK 캘린더 일정을 가져옵니다
2. 장소별(오아시스 덕수궁/소정동)로 분류하여 HTML 테이블을 생성합니다
3. 일정이 없는 경우 "일정 없음"으로 표시됩니다

---

## 시즌레터 템플릿

### 기본 구조

```html
<p><strong><img src="https://cdn.imweb.me/upload/S20240629fee25a0bc999e/6fb64155a248d.png" class="fr-fic fr-dii"></strong></p>

<p><strong><br></strong></p>

<p><strong><span style="font-size: 22px;">[시즌] 레터 #[번호]. [제목]</span></strong></p>

<ol>
	<li>[목차 항목 1]</li>
	<li>[목차 항목 2]</li>
	<li>[목차 항목 3]</li>
	<!-- 필요한 만큼 추가 -->
</ol>

<p style="text-align: left;">
	<br>
</p>
<hr>

<!-- 각 섹션 반복 -->
<p>
	<br>
</p>

<p><strong><span style="font-size: 22px;">[섹션 제목]</span></strong></p>

<p>[섹션 내용]</p>

<p>
	<br>
</p>
<hr>

<!-- 다음 섹션... -->
```

### 섹션 유형별 템플릿

#### 1. 일반 텍스트 섹션

```html
<p>
	<br>
</p>

<p><strong><span style="font-size: 22px;">[섹션 제목]</span></strong></p>

<p>[본문 내용 - 여러 문단 가능]</p>

<p><u>[강조하고 싶은 핵심 내용]</u></p>

<p><strong>[굵게 강조할 공지사항]</strong></p>

<p>
	<br>
</p>
<hr>
```

#### 2. 링크가 포함된 섹션

```html
<p>
	<br>
</p>

<p><a href="[URL]" rel="noopener noreferrer" target="_blank"><strong><span style="font-size: 22px;">[링크 텍스트]</span></strong></a><strong><span style="font-size: 22px;">[나머지 제목]</span></strong></p>

<p>[본문 내용]</p>

<p style="text-align: left;">
	<a href="[URL]" rel="noopener noreferrer" target="_blank"><img class="fr-dii" src="[이미지 URL]"></a>
</p>

<p>
	<br>
</p>
<hr>
```

#### 3. 유튜브 영상 섹션

```html
<p><span class="fr-video fr-deletable fr-fvc fr-dvb fr-draggable fr-fvl" contenteditable="false" draggable="true"><iframe width="640" height="360" src="https://www.youtube.com/embed/[VIDEO_ID]?&wmode=opaque" frameborder="0" allowfullscreen="" class="fr-draggable"></iframe></span><em>[영상 설명]</em></p>
```

#### 4. 장소별 팀 세션 안내 (2열 테이블)

```html
<p>
	<br>
</p>

<p><strong><span style="font-size: 22px;">장소별 각 팀 세션 안내</span></strong></p>

<p>웹사이트 하단<strong>&nbsp;[<a href="https://hfk.imweb.me/36">캘린더</a>]&nbsp;</strong>페이지에서 HFK의 팀, 이벤트 전체 일정을 확인하실 수 있습니다. HFK에서의 성장이 휘발되지 않도록 모임이 끝나기 전 슬랙에서 4L 리뷰를 꼭 남겨주세요!&nbsp;</p>

<p>
	<br>
</p>

<table class="noBorder m-table-style" style="width: 100%;">
	<tbody>
		<tr>
			<td style="width: 50%; vertical-align: top;">

				<p><strong><a href="https://naver.me/59jN0Mvd">오아시스 덕수궁</a></strong></p>

				<p>2016년, 멤버들과 설계부터 제작까지 함께 만들고 채운 공간입니다. 평일 저녁에는 HFK 멤버들이 퇴근 후 모여 팀별 모임을 가지고 주말에는 와인 파티를 열거나 영화를 보기도 합니다.</p>
				<hr>

				<ul>
					<li>[날짜] ([요일]) [시간] [팀명] [회차]</li>
					<!-- 일정 항목 반복 -->
				</ul>
				<br>
			</td>
			<td style="width: 50%; vertical-align: top;">

				<p><strong>[<a href="https://naver.me/5Y1r6hsD">소정동</a>]</strong></p>

				<p>덕수궁을 바라보며 창의적인 프로젝트를 진행하기 위해 마련한 공간입니다. 고즈넉한 경치로부터 영감을 받을 수 있습니다. 등록 중인 HFK 멤버는 한 시즌동안 1회 공간비 50% 할인을 받을 수 있습니다.&nbsp;</p>
				<hr>

				<ul>
					<li>[날짜] ([요일]) [시간] [팀명] [회차]</li>
					<!-- 일정 항목 반복 -->
				</ul>
				<br>
			</td>
		</tr>
	</tbody>
</table>
<hr>
```

#### 5. 주요 이벤트 안내 (이미지+설명 테이블)

```html
<p>
	<br>
</p>

<p><strong><span style="font-size: 22px;">주요 이벤트 안내</span></strong></p>

<p>HFK 멤버십은 깊이 있는 성장을 위한 팀 활동, 생산적인 여가를 위한 이벤트 활동으로 구성되어 있으며, <u>이벤트는 겨울시즌의 모든 팀 멤버가 신청 가능합니다.&nbsp;</u></p>

<p>﹒[신청하기]버튼을 누르시면 신청 페이지로 이동합니다. 별도의 참석 리마인드 문자는 전송되지 않습니다.&nbsp;</p>

<p>﹒<strong>타인의 성장을 위해 전일 취소, 당일 취소, 당일 노쇼는 지양해주세요.&nbsp;</strong>취소시 슬랙 공지에 사유를 댓글로 남겨주세요. 온라인 참석은 어렵습니다.
	<br>
	<br>
</p>

<p><a class="btn btn-primary" href="https://thehfk.org/event" rel="noopener noreferrer" target="_blank">겨울시즌 이벤트 신청하기</a></p>

<p>
	<br>
</p>

<table class="noBorder m-table-style" style="width: 100%;">
	<tbody>
		<tr>
			<td style="width: 50%; vertical-align: top;">

				<p style="text-align: left;"><img class="fr-dii" src="[이벤트 이미지 URL]"></p>
				<br>
			</td>
			<td style="width: 50%; vertical-align: top;">

				<p><strong>[이모지] &nbsp;[이벤트 제목]</strong></p>

				<p>[이벤트 설명]</p>

				<ul>
					<li>일시: [날짜] ([요일]) [시간]</li>
					<li>장소: [장소명]</li>
					<li>대상: [대상]</li>
					<li>신청 방법: 웹사이트의 [<a href="https://thehfk.org/event">멤버 이벤트</a>] 페이지에서 신청 내용 작성</li>
					<li>참석/대기 발표: [날짜] ([요일]) [시간] HFK 슬랙 공지에 댓글로 안내</li>
				</ul>

				<p>
					<br>
				</p>
			</td>
		</tr>
		<!-- 추가 이벤트는 새로운 <tr> 추가 -->
	</tbody>
</table>
```

---

## 작성 원칙

### 문체
- 친근하면서도 전문적인 톤
- ~해요, ~합니다 혼용 가능
- 멤버들에게 직접 말하는 듯한 어조
- 이모지 적절히 사용 (섹션당 1-2개)

### 강조 스타일
- `<strong>`: 중요 공지사항, 날짜, 마감 등
- `<u>`: 핵심 메시지, 꼭 전달하고 싶은 내용
- `<em>`: 부가 설명, 캡션

### 링크 처리
- 외부 링크: `rel="noopener noreferrer" target="_blank"` 필수
- 내부 링크 (HFK 웹사이트): 상대 경로 또는 전체 URL

### 구분선
- 각 섹션 사이에 `<hr>` 사용
- 섹션 시작 전 `<br>` 태그로 여백 확보

### 주요 상수 URL
- 캘린더: https://hfk.imweb.me/36
- 이벤트 신청: https://thehfk.org/event
- 오아시스 덕수궁: https://naver.me/59jN0Mvd
- 소정동: https://naver.me/5Y1r6hsD
- 링크드인: https://www.linkedin.com/showcase/thehfk/
- 유튜브: https://www.youtube.com/@HFK
- 헤더 이미지: https://cdn.imweb.me/upload/S20240629fee25a0bc999e/6fb64155a248d.png

---

## 생성 프로세스

1. **인자 확인**: 시즌, 레터번호, 제목이 제공되었는지 확인
2. **목차 구성**: 사용자에게 포함할 섹션들을 질문
3. **섹션별 정보 수집**: 각 섹션에 필요한 정보 수집
   - 일반 섹션: 제목과 본문 내용
   - 팀 세션 안내: 장소별 일정 목록
   - 이벤트 안내: 이벤트 제목, 설명, 일시, 장소, 대상, 이미지 URL
4. **HTML 생성**: 템플릿에 맞춰 HTML 코드 생성
5. **출력**: 완성된 HTML을 코드 블록으로 출력

### 사용자 질문 예시

```
레터에 포함할 섹션들을 알려주세요. (예: 링크드인 소식, 팀 게더링 안내, 연탄봉사 예고, 팀 세션 안내, 이벤트 안내)
```

```
"[섹션명]" 섹션의 내용을 알려주세요:
- 주요 메시지는 무엇인가요?
- 강조하고 싶은 내용이 있나요?
- 관련 링크나 이미지가 있나요?
```

---

## 주의사항

- HTML 태그 형식을 정확히 유지
- 테이블 스타일 클래스 (`noBorder m-table-style`) 유지
- 이미지 클래스 (`fr-fic fr-dii` 또는 `fr-dii`) 유지
- 빈 줄은 `<p><br></p>` 형태로 표현
- 인라인 스타일은 원본 템플릿 형식 유지
