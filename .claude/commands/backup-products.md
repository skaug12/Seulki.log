# Imweb 상품 백업

아임웹의 26봄주중/26봄주말 상품을 Obsidian 볼트로 백업합니다.

## 실행 방법

1. 먼저 dry run으로 확인합니다:
```bash
cd /Users/sklee/hfk-imweb && source /Users/sklee/hfk-sklee/.venv/bin/activate && python scripts/backup_to_obsidian.py
```

2. 실제 백업을 실행합니다:
```bash
cd /Users/sklee/hfk-imweb && source /Users/sklee/hfk-sklee/.venv/bin/activate && python scripts/backup_to_obsidian.py --execute
```

## 결과

- 백업 위치: `/Users/sklee/hfk-imweb/product/`
- 각 상품은 `상품명.md` 형태로 저장됩니다

## 인자

- `--dry-run` 또는 인자 없음: 백업할 내용만 확인
- `--execute`: 실제 백업 실행

$ARGUMENTS
