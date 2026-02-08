# 26봄 캘린더 일정 업데이트

Google Calendar의 HFK 캘린더에서 "26봄" 이벤트를 가져와 아임웹 26봄주중/26봄주말 상품의 세션 날짜를 업데이트합니다.

## 실행 방법

1. 먼저 dry run으로 변경사항을 확인합니다:
```bash
cd /Users/sklee/hfk-sklee && source .venv/bin/activate && python scripts/update_schedule_from_calendar.py
```

2. 변경사항이 올바르면 실제 업데이트를 실행합니다:
```bash
cd /Users/sklee/hfk-sklee && source .venv/bin/activate && python scripts/update_schedule_from_calendar.py --execute
```

## 주의사항

- 캘린더에 "[팀] 26봄 상품명" 형식의 이벤트가 있어야 합니다
- 최소 5개 이상의 세션이 등록된 상품만 업데이트됩니다
- 캘린더에 일정이 없는 상품은 스킵됩니다

## 인자

- `--dry-run` 또는 인자 없음: 변경사항만 확인 (기본값)
- `--execute`: 실제 업데이트 실행

$ARGUMENTS
