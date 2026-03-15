# Seulki.log

HFK 운영 자동화를 위한 Claude Code 스킬 + 스크립트 저장소.

## 셋업

```bash
git clone https://github.com/skaug12/Seulki.log.git ~/Seulki.log
cd ~/Seulki.log && bash setup.sh
```

자세한 내용: [docs/새 컴퓨터 셋업.md](docs/새%20컴퓨터%20셋업.md)

## 구조

```
.claude/commands/   ← Claude Code 스킬 (32개)
scripts/            ← Python 스크립트
data/               ← 운영 데이터
docs/               ← 문서
setup.sh            ← 셋업 스크립트
```

## Commands

`.claude/commands/` 폴더의 `.md` 파일들이 Claude Code에서 `/command-name` 형태로 사용 가능합니다.

글로벌 사용을 위해 `setup.sh`가 `~/.claude/commands`로 symlink를 생성합니다.
