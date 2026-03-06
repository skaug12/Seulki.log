# HFK 프로젝트 파일 구조

프로젝트의 모든 파일을 쉽게 찾을 수 있는 인덱스입니다.

---

## 프로젝트 구조 개요

```
~/
├── hfk.code-workspace      ← VSCode 워크스페이스 파일
├── hfk-sklee/              ← 스크립트 및 개발 파일
└── hfk-imweb/              ← Obsidian 볼트 (콘텐츠)
```

---

## hfk-sklee (스크립트 프로젝트)

```
hfk-sklee/
├── .claude/
│   └── commands/           ← Claude Code 스킬 정의
│       ├── backup-notes.md
│       ├── backup-products.md
│       ├── categorize-images.md
│       ├── sync-products.md
│       └── update-schedule.md
├── .venv/                  ← Python 가상환경
├── docs/                   ← 문서
│   ├── INDEX.md            ← 이 파일
│   └── SYNC_GUIDE.md       ← 동기화 가이드
├── scripts/                ← 실행 스크립트
│   ├── edit_team.py        ← 팀 정보 수정
│   ├── sync_team_file.py   ← 팀 파일 동기화
│   ├── sync_to_imweb.py    ← Obsidian → 아임웹
│   ├── update_26spring_dates.py
│   ├── update_schedule_from_calendar.py
│   ├── test_clova_speech.py
│   └── test_connection.py  ← API 연결 테스트
├── archive/                ← 보관용 파일
│   ├── data/               ← 과거 데이터 백업
│   └── scripts/            ← 사용하지 않는 스크립트
├── imweb_api.py            ← 아임웹 API 클라이언트
├── content_converter.py    ← 콘텐츠 변환 유틸
├── clova_speech_api.py     ← 클로바 음성 API
├── .env                    ← API 키 (비공개)
├── .env.example            ← API 키 템플릿
├── requirements.txt        ← Python 의존성
└── README.md               ← 프로젝트 설명
```

---

## hfk-imweb (Obsidian 볼트)

```
hfk-imweb/
├── .obsidian/              ← Obsidian 설정
├── docs/                   ← 문서
│   └── SKILL_GUIDE.md      ← 스킬 사용 가이드
├── product/                ← 상품 노트
│   ├── 26봄주중/           ← 현재 시즌
│   ├── 26봄주말/
│   ├── 25겨울주중/         ← 지난 시즌
│   ├── 25겨울주말/
│   ├── ...
│   ├── 추가등록/
│   ├── 이벤트/
│   └── 시즌오프/
├── note/                   ← HFK NOTE 백업
│   ├── 공지/
│   └── 리뷰/
├── images/                 ← 이미지
│   ├── source/             ← 분류 전 이미지
│   └── 팀_테마_참고.md     ← 팀별 이미지 가이드
├── templates/              ← 템플릿
│   ├── 공지 템플릿.md
│   └── 리뷰 템플릿.md
└── scripts/                ← Obsidian용 스크립트
    ├── backup_to_obsidian.py
    ├── sync_to_imweb.py
    └── backup_notes.py
```

---

## 주요 파일 빠른 링크

### 스킬 (Claude Code)
- [backup-products.md](../.claude/commands/backup-products.md)
- [sync-products.md](../.claude/commands/sync-products.md)
- [backup-notes.md](../.claude/commands/backup-notes.md)
- [categorize-images.md](../.claude/commands/categorize-images.md)
- [update-schedule.md](../.claude/commands/update-schedule.md)

### 문서
- [SKILL_GUIDE.md](/Users/sklee/hfk-imweb/docs/SKILL_GUIDE.md) - 스킬 사용법
- [SYNC_GUIDE.md](./SYNC_GUIDE.md) - 동기화 가이드

### 설정
- [.env](../.env) - API 키 (비공개)
- [requirements.txt](../requirements.txt) - Python 패키지

---

## 카테고리별 상품 폴더

| 시즌 | 폴더 |
|------|------|
| 26봄주중 | `/product/26봄주중/` |
| 26봄주말 | `/product/26봄주말/` |
| 25겨울주중 | `/product/25겨울주중/` |
| 25겨울주말 | `/product/25겨울주말/` |
| 25여름주중 | `/product/25여름주중/` |
| 25여름주말 | `/product/25여름주말/` |
| 25봄주중 | `/product/25봄주중/` |
| 25봄주말 | `/product/25봄주말/` |
| 24겨울주중 | `/product/24겨울주중/` |
| 24겨울주말 | `/product/24겨울주말/` |
| 24가을주중 | `/product/24가을주중/` |
| 24가을주말 | `/product/24가을주말/` |

---

## Archive (보관 파일)

더 이상 사용하지 않는 파일은 `archive/` 폴더에 보관됩니다.

- `archive/data/` - 과거 JSON/HTML 데이터 백업
- `archive/scripts/` - 이전 버전 스크립트
