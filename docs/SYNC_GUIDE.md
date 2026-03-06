# GitHub 동기화 가이드

이 문서는 hfk-sklee 프로젝트를 GitHub와 동기화하는 방법을 설명합니다.

## 📊 현재 상태

- ✅ Git 저장소 초기화됨
- ✅ GitHub 원격 저장소 연결됨: https://github.com/skaug12/Seulki.log
- ✅ GitHub CLI 인증 완료 (skaug12)
- ✅ main 브랜치 푸시 완료

## 🔄 기본 동기화 작업

### 1. GitHub에서 최신 코드 가져오기 (Pull)

다른 곳에서 작업한 내용을 로컬로 가져옵니다.

```bash
cd /Users/sklee/hfk-sklee
git pull origin main
```

### 2. 로컬 변경사항 GitHub에 올리기 (Push)

로컬에서 작업한 내용을 GitHub에 업로드합니다.

```bash
# 변경된 파일 확인
git status

# 모든 변경사항 스테이징
git add .

# 커밋 생성
git commit -m "작업 내용 설명"

# GitHub에 푸시
git push origin main
```

## 🚀 자주 사용하는 워크플로우

### 작업 시작 전 (항상!)

```bash
cd /Users/sklee/hfk-sklee
source venv/bin/activate
git pull origin main  # 최신 코드 받기
```

### 작업 완료 후

```bash
git status                    # 변경사항 확인
git add .                     # 모든 변경사항 추가
git commit -m "변경 내용"     # 커밋
git push origin main          # GitHub에 푸시
```

## 📝 실전 예제

### 예제 1: 새로운 스크립트 추가

```bash
# 1. 최신 코드 받기
git pull origin main

# 2. 가상 환경 활성화
source venv/bin/activate

# 3. 새 파일 작성
# scripts/new_script.py 파일 생성 및 작업

# 4. 테스트
python scripts/new_script.py

# 5. Git에 추가 및 커밋
git add scripts/new_script.py
git commit -m "Add new script for data analysis"

# 6. GitHub에 푸시
git push origin main
```

### 예제 2: API 클라이언트 수정

```bash
# 1. 최신 코드 받기
git pull origin main

# 2. imweb_api.py 수정

# 3. 변경사항 확인
git diff imweb_api.py

# 4. 커밋 및 푸시
git add imweb_api.py
git commit -m "Update API client: add order retrieval function"
git push origin main
```

### 예제 3: 데이터 내보내기 후 기록

```bash
# 1. 데이터 내보내기
python scripts/export_products_debug.py

# 2. 새로 생성된 JSON 파일은 .gitignore에 의해 제외됨
# 3. 스크립트 변경사항만 커밋
git add scripts/
git commit -m "Update export script with better error handling"
git push origin main
```

## 🔍 유용한 Git 명령어

### 현재 상태 확인

```bash
# 변경된 파일 확인
git status

# 변경 내용 상세 보기
git diff

# 커밋 히스토리 보기
git log --oneline -10

# 원격 저장소 정보 확인
git remote -v
```

### 특정 파일만 커밋

```bash
# 특정 파일만 추가
git add scripts/export_all_products.py

# 여러 파일 추가
git add scripts/*.py

# 커밋 및 푸시
git commit -m "Update export scripts"
git push origin main
```

### 변경사항 취소

```bash
# 스테이징 취소 (git add 취소)
git reset HEAD <파일명>

# 파일 변경사항 되돌리기 (주의!)
git checkout -- <파일명>

# 마지막 커밋 메시지 수정
git commit --amend -m "새로운 커밋 메시지"
```

## 🌿 브랜치 작업 (선택사항)

큰 기능 추가 시 브랜치를 사용하면 안전합니다.

```bash
# 새 브랜치 생성 및 전환
git checkout -b feature/new-feature

# 작업 후 커밋
git add .
git commit -m "Add new feature"

# GitHub에 브랜치 푸시
git push origin feature/new-feature

# main 브랜치로 돌아가기
git checkout main

# 브랜치 병합 (로컬)
git merge feature/new-feature

# 또는 GitHub에서 Pull Request 생성
```

## 🔔 자동 동기화 (선택사항)

매일 자동으로 백업하려면 cron job 설정:

```bash
# crontab 편집
crontab -e

# 매일 오후 6시에 자동 커밋 및 푸시
0 18 * * * cd /Users/sklee/hfk-sklee && git add . && git commit -m "Auto backup $(date +\%Y-\%m-\%d)" && git push origin main
```

## ⚠️ 주의사항

### 절대 커밋하면 안 되는 것

- `.env` 파일 (API 키 포함) - 이미 .gitignore에 포함됨 ✅
- `venv/` 디렉토리 - 이미 .gitignore에 포함됨 ✅
- 개인 정보나 민감한 데이터

### .gitignore가 보호하는 파일들

```
.env              # API 인증 정보
venv/             # 가상 환경
*.json            # 데이터 파일
__pycache__/      # Python 캐시
.DS_Store         # macOS 파일
```

## 🆘 문제 해결

### Push 실패: "remote contains work that you do not have"

```bash
# 먼저 pull로 최신 코드 받기
git pull origin main

# 충돌 해결 후 다시 푸시
git push origin main
```

### 인증 오류

```bash
# GitHub CLI 재인증
gh auth login --web

# Git credential helper 재설정
gh auth setup-git
```

### 커밋 실수했을 때

```bash
# 마지막 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 완전히 되돌리기 (주의!)
git reset --hard HEAD~1
```

## 📱 GitHub 웹에서 확인

- **저장소**: https://github.com/skaug12/Seulki.log
- **커밋 히스토리**: https://github.com/skaug12/Seulki.log/commits/main
- **코드 브라우저**: https://github.com/skaug12/Seulki.log/tree/main

## 🎯 빠른 명령어 모음

```bash
# 매일 작업 시작
cd /Users/sklee/hfk-sklee
source venv/bin/activate
git pull

# 작업 완료 후
git add .
git commit -m "오늘의 작업 내용"
git push

# 상태 확인
git status
git log --oneline -5
```

---

더 자세한 내용은 [Git 공식 문서](https://git-scm.com/doc)를 참고하세요.
