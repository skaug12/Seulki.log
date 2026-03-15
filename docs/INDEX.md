# HFK 프로젝트 파일 구조

## 워크스페이스 개요

```
~/
├── Seulki.log/              ← git: 스킬 + 스크립트
│   ├── .claude/commands/    ← Claude Code 스킬
│   ├── scripts/             ← Python 스크립트
│   ├── data/                ← 운영 데이터
│   ├── docs/                ← 문서
│   └── archive/             ← 보관 파일
│
├── hfk-imweb/ → (symlink)   ← iCloud: Obsidian vault
│   ├── product/             ← 상품 노트
│   ├── note/                ← HFK NOTE
│   ├── images/              ← 이미지
│   ├── daily/               ← 데일리 작업 일지
│   ├── mcp-servers/         ← MCP 서버
│   ├── templates/           ← 템플릿
│   └── scripts/             ← Obsidian용 스크립트
│
└── .claude/commands/ → (symlink) ← 글로벌 스킬
```

---

## Seulki.log (스킬/스크립트)

```
Seulki.log/
├── .claude/commands/           ← Claude Code 스킬 (32개)
├── scripts/                    ← Python 스크립트
│   ├── imweb_api.py            ← 아임웹 API 클라이언트
│   ├── content_converter.py    ← 콘텐츠 변환 유틸
│   ├── clova_speech_api.py     ← 클로바 음성 API
│   ├── sync_to_imweb.py        ← Obsidian → 아임웹
│   ├── sync_team_file.py       ← 팀 파일 동기화
│   ├── edit_team.py            ← 팀 정보 수정
│   ├── schedule_slack_notices.py
│   ├── restore_products.py
│   ├── update_26spring_dates.py
│   ├── update_schedule_from_calendar.py
│   ├── test_clova_speech.py
│   └── test_connection.py      ← API 연결 테스트
├── data/                       ← 운영 데이터
│   ├── teams/                  ← 팀별 JSON
│   └── *.csv                   ← CSV 데이터
├── docs/                       ← 문서
│   ├── INDEX.md                ← 이 파일
│   ├── SYNC_GUIDE.md           ← 동기화 가이드
│   └── 새 컴퓨터 셋업.md       ← 셋업 가이드
├── archive/                    ← 보관 파일
├── setup.sh                    ← 셋업 스크립트
├── .env                        ← API 키 (비공개)
├── .mcp.json                   ← MCP 서버 설정
└── requirements.txt            ← Python 패키지
```

---

## hfk-imweb (Obsidian vault, iCloud)

```
hfk-imweb/
├── product/                ← 상품 노트
│   ├── 26봄주중/
│   ├── 26봄주말/
│   ├── 25겨울주중/
│   ├── 25겨울주말/
│   ├── 추가등록/
│   ├── 이벤트/
│   └── 시즌오프/
├── note/                   ← HFK NOTE
│   ├── 공지/
│   ├── 리뷰/
│   ├── 녹취/
│   └── ...
├── daily/                  ← 데일리 작업 일지
├── images/                 ← 이미지
│   ├── source/             ← 분류 전 이미지
│   └── photo-calendar/     ← 사진 캘린더
├── mcp-servers/            ← MCP 서버
│   └── imweb/              ← 아임웹 MCP
├── templates/              ← 템플릿
├── docs/                   ← Obsidian 문서
└── .google_credentials.json ← Google 인증
```

---

## 동기화 방식

| 대상 | 경로 | 방식 |
|------|------|------|
| 스킬/스크립트 | `~/Seulki.log/` | git |
| 콘텐츠 | `~/hfk-imweb/` | iCloud (Obsidian) |
| MCP 서버 | `~/hfk-imweb/mcp-servers/` | iCloud |
| 인증 파일 | `~/hfk-imweb/.google_*` | iCloud |
| API 키 | `~/Seulki.log/.env` | 수동 복사 |
| venv | `~/Seulki.log/.venv/` | 재생성 |

---

## 주요 문서

- [새 컴퓨터 셋업.md](./새%20컴퓨터%20셋업.md)
- [SYNC_GUIDE.md](./SYNC_GUIDE.md)
