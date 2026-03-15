# HFK 데일리 에이전트

하루 마무리 시 실행. 작업 내역 자동 수집 → 미리알림 관리 → 커밋/푸시까지 한 번에 처리합니다.

## 실행 워크플로우

### Step 1: 작업 내역 자동 수집

1. `$HOME/Seulki.log/daily/YYYY-MM-DD.md` 확인 (없으면 생성, 있으면 읽기)
2. 아래 3가지 소스에서 오늘 작업 내역을 **모두** 자동 수집:

   **a) Git 커밋 이력**
   ```bash
   cd $HOME/Seulki.log
   git log --since="$(date +%Y-%m-%d)T00:00" --until="$(date +%Y-%m-%d)T23:59" --oneline --all --name-only
   ```

   **b) 현재 활성 대화**
   - 이 대화에서 수행한 작업, 사용한 스킬/커맨드, 의사결정 사항 정리

   **c) 오늘의 Past Conversations 전체 검색**
   - `~/.claude/projects/*/sessions-index.json`에서 오늘 날짜(`modified` 또는 `created`)에 해당하는 세션 필터링
   - 세션 인덱스에 오늘 날짜가 없으면 파일시스템 mtime으로 fallback:
     ```bash
     touch -t YYYYMMDD0000 /tmp/today_marker
     find ~/.claude/projects -maxdepth 2 -name "*.jsonl" -newer /tmp/today_marker -not -path "*/subagents/*"
     ```
   - 각 세션 JSONL에서 user 메시지와 assistant tool_use를 파싱하여 작업 내역 추출:
     ```bash
     python3 -c "
     import json
     for l in open('SESSION_FILE'):
         d = json.loads(l)
         role = d.get('role','')
         if role == 'user':
             msg = d.get('message',{})
             content = msg.get('content','') if isinstance(msg, dict) else ''
             if isinstance(content, list):
                 for c in content:
                     if isinstance(c, dict) and c.get('type')=='text':
                         print('USER:', c['text'][:300])
             elif isinstance(content, str):
                 print('USER:', content[:300])
         elif role == 'assistant':
             msg = d.get('message',{})
             content = msg.get('content','') if isinstance(msg, dict) else ''
             if isinstance(content, list):
                 for c in content:
                     if isinstance(c, dict) and c.get('type')=='tool_use':
                         print('TOOL:', c.get('name',''), json.dumps(c.get('input',{}), ensure_ascii=False)[:200])
     "
     ```
   - 세션별로 주제, 수행 작업, 생성/수정 파일, 산출물을 요약

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
