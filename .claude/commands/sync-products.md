# Obsidian 상품 동기화

Obsidian 볼트의 상품 노트를 아임웹으로 동기화합니다.

## 실행 방법

1. 먼저 dry run으로 확인합니다:
```bash
cd /Users/sklee/hfk-imweb && source /Users/sklee/hfk-sklee/.venv/bin/activate && python scripts/sync_to_imweb.py
```

2. 실제 동기화를 실행합니다:
```bash
cd /Users/sklee/hfk-imweb && source /Users/sklee/hfk-sklee/.venv/bin/activate && python scripts/sync_to_imweb.py --execute
```

## 노트 형식

Obsidian 노트는 다음과 같은 YAML frontmatter를 포함해야 합니다:
```yaml
---
product_no: "123"
name: "상품명"
category: "26봄주중"
schedule: "화요일 19:30-22:00 (3개월)"
status: "draft"  # draft, synced
---
```

## 상태 설명

- `draft`: 수정된 상태, 동기화 필요
- `synced`: 아임웹과 동기화된 상태

노트를 수정한 후 status를 `draft`로 변경하면 다음 동기화 시 업데이트됩니다.

## 인자

- `--dry-run` 또는 인자 없음: 동기화할 내용만 확인
- `--execute`: 실제 동기화 실행

$ARGUMENTS
