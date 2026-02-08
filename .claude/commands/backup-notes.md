# HFK NOTE 백업

HFK NOTE 게시판의 모든 게시글을 Obsidian 볼트로 백업합니다.

## 실행 방법

```bash
source /Users/sklee/hfk-sklee/.venv/bin/activate
python3 -u /Users/sklee/hfk-imweb/scripts/backup_notes.py --execute
```

## 결과

- **위치**: `/Users/sklee/hfk-imweb/note/`
- **공지**: `note/공지/` 폴더에 저장
- **리뷰**: `note/리뷰/` 폴더에 저장
- **파일명 형식**: `YYYYMMDD_제목.md`

## 참고

- 백업은 thehfk.org 웹사이트에서 스크래핑 방식으로 수행됩니다
- 아임웹 게시판 API가 제공되지 않아 API 방식 동기화는 불가능합니다
- 새 게시글 작성은 아임웹 관리자 페이지에서 직접 해야 합니다
