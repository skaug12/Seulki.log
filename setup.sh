#!/bin/bash
# Seulki.log 새 컴퓨터 셋업 스크립트
# 사용법: cd ~/Seulki.log && bash setup.sh

set -e

echo "=== Seulki.log 셋업 ==="

# 1. iCloud Obsidian vault symlink
ICLOUD_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/hfk-imweb"
if [ -d "$ICLOUD_VAULT" ]; then
  ln -sf "$ICLOUD_VAULT" "$HOME/hfk-imweb"
  echo "[OK] ~/hfk-imweb → iCloud Obsidian vault"
else
  echo "[SKIP] iCloud vault not found: $ICLOUD_VAULT"
  echo "       Obsidian에서 iCloud 동기화를 먼저 설정하세요"
fi

# 2. Claude Code global commands symlink
mkdir -p "$HOME/.claude"
ln -sf "$HOME/Seulki.log/.claude/commands" "$HOME/.claude/commands"
echo "[OK] ~/.claude/commands → ~/Seulki.log/.claude/commands"

# 3. Python venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "[OK] Python venv 생성"
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo "[OK] Python 패키지 설치 완료"

# 4. 필수 파일 확인
echo ""
echo "=== 수동 확인 필요 ==="

if [ ! -f ".env" ]; then
  echo "[!] .env 파일이 없습니다. 기존 컴퓨터에서 복사하세요:"
  echo "    scp <기존컴퓨터>:~/Seulki.log/.env ~/Seulki.log/.env"
fi

if [ ! -f "$HOME/hfk-imweb/.google_credentials.json" ]; then
  echo "[!] Google 인증 파일이 없습니다 (iCloud 동기화 대기 중일 수 있음)"
fi

echo ""
echo "=== 셋업 완료 ==="
echo "구조:"
echo "  ~/Seulki.log/           ← 스킬 + 스크립트 (git)"
echo "  ~/hfk-imweb/            ← 콘텐츠 + 인증 (iCloud)"
echo "  ~/.claude/commands/     ← 글로벌 스킬 (symlink)"
