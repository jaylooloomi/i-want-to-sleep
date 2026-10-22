#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit)：夜班時禁止寫入禁改清單路徑。
set -u
P="${CLAUDE_PROJECT_DIR:-$PWD}/.agent-pipeline"
[ -f "$P/ACTIVE" ] || exit 0

input=$(cat)
path=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)
[ -n "$path" ] || exit 0

if echo "$path" | grep -Eq '(\.gitlab-ci\.yml$|\.github/workflows/|/[Mm]igrations?/|appsettings[^/]*\.json$|/\.env|web\.config$|app\.config$|\.csproj$|package\.json$|package-lock\.json$|pnpm-lock\.yaml$|yarn\.lock$|requirements[^/]*\.txt$|Directory\.Packages\.props$)'; then
  echo "夜班防線阻擋：$path 在禁改清單（CI 設定 / migration / 設定檔 / 依賴清單）。請記錄到 result.md「需要你決定的事」。" >&2
  exit 2
fi
exit 0
