# HFK 데일리 에이전트

하루 마무리 시 실행. 작업 내역 자동 수집 → 미리알림 관리 → 커밋/푸시까지 한 번에 처리합니다.

## 실행 워크플로우

### Step 1: 작업 내역 자동 수집

1. `$HOME/Seulki.log/daily/YYYY-MM-DD.md` 확인 (없으면 생성, 있으면 읽기)
2. 아래 소스에서 오늘 작업 내역을 자동 수집:

   **a) Git 커밋 이력**
   ```bash
   cd $HOME/Seulki.log
   git log --since="$(date +%Y-%m-%d)T00:00" --until="$(date +%Y-%m-%d)T23:59" --oneline --all
   ```
   - 커밋 메시지 + 변경 파일 목록 추출

   **b) 대화 내역 기반**
   - 현재 대화에서 수행한 작업을 시간순 정리
   - 사용한 스킬/커맨드 목록
   - 주요 의사결정 사항

   **c) 산출물**
   - 생성/수정된 파일 목록
   - 새 스킬, 커맨드, 설정 파일
   - 외부 시스템 작업 (미리알림, Slack 등)

3. 기존 내용과 중복 없이 병합하여 아래 형식으로 기록:

   ```markdown
   # YYYY-MM-DD 작업 일지

   ## 오늘 완료한 작업

   - 작업 1
   - 작업 2

   ## 산출물

   | 유형 | 파일/항목 | 설명 |
   |------|-----------|------|
   | 스킬 | `commands/example.md` | 새로 생성 |
   | 코드 | `src/bot.py` | 기능 추가 |

   ## 대화 요약

   - 주요 논의/결정 사항 (1-3줄)

   ---

   ## 메모

   ```

4. 결과를 보여주고 추가/수정 여부 확인

### Step 2: 미리알림 관리

1. MCP Apple Reminders `list` → "HFK" 리스트 조회
2. 완료/미완료 항목 표시
3. 새 To-Do 추가 여부 확인 → MCP `create` / `bulk_create`

### Step 3: 요약 출력

- 기록된 작업 수
- 미리알림 현황 (완료/미완료)
- 새로 추가된 To-Do 수

### Step 4: git push

```bash
cd $HOME/Seulki.log
git add daily/
git commit -m "daily: $(date +%Y-%m-%d)"
git push origin main
```
