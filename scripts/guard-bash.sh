#!/usr/bin/env bash
# PreToolUse(Bash)：只在夜班（ACTIVE 存在）時啟用。exit 2 = 阻擋，stderr 回給 Claude。
set -u
P="${CLAUDE_PROJECT_DIR:-$PWD}/.agent-pipeline"
[ -f "$P/ACTIVE" ] || exit 0

input=$(cat)
cmd=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null || true)
[ -n "$cmd" ] || exit 0

deny() {
  echo "夜班防線阻擋：$1。夜班不允許此動作；改用其他方式，或記錄到 result.md「需要你決定的事」。" >&2
  exit 2
}

# 1. 危險 git / 檔案操作
echo "$cmd" | grep -Eq 'git[[:space:]]+push'                                        && deny "git push"
echo "$cmd" | grep -Eq 'git[[:space:]]+(merge|rebase)'                              && deny "git merge/rebase"
echo "$cmd" | grep -Eq 'git[[:space:]]+reset[[:space:]]+--hard'                     && deny "git reset --hard"
echo "$cmd" | grep -Eq 'git[[:space:]].*(--force|[[:space:]]-f([[:space:]]|$))'     && deny "git --force"
echo "$cmd" | grep -Eq 'git[[:space:]]+(checkout|switch)[[:space:]]+(main|master|develop)([[:space:]]|$)' && deny "切換到主分支"
echo "$cmd" | grep -Eq 'rm[[:space:]]+-[A-Za-z]*(rf|fr)'                            && deny "rm -rf"

# 2. 新增第三方套件（依賴決策留給早上）
echo "$cmd" | grep -Eq '(dotnet[[:space:]]+add[[:space:]]+package|npm[[:space:]]+(install|i|add)[[:space:]]+[^-]|pnpm[[:space:]]+add|yarn[[:space:]]+add|pip3?[[:space:]]+install|nuget[[:space:]]+install)' && deny "新增第三方套件"

# 3. 透過 shell 改禁改清單（sed -i / tee / 重導向 / mv / cp 等繞法）
if echo "$cmd" | grep -Eq '(sed[[:space:]]+-i|tee[[:space:]]|>[[:space:]]*[^&>]|mv[[:space:]]|cp[[:space:]])'; then
  echo "$cmd" | grep -Eq '(\.gitlab-ci\.yml|\.github/workflows|[Mm]igrations?/|appsettings[^[:space:]]*\.json|\.env|web\.config|app\.config|\.csproj|package\.json|requirements[^[:space:]]*\.txt|Directory\.Packages\.props)' && deny "透過 shell 修改禁改清單中的檔案"
fi

exit 0
