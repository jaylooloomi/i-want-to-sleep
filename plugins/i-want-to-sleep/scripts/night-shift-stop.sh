#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Arthur Wang
# Stop hook：夜班進行中就把 Claude 推回去繼續；白天（沒有 ACTIVE 檔）完全不干擾。
# exit 0 = 允許停止；exit 2 + stderr = 阻止停止，stderr 內容會回給 Claude 當下一回合的指示。
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
P="$ROOT/.agent-pipeline"

[ -f "$P/ACTIVE" ] || exit 0          # 不是夜班 → 正常停止
# 每次 Stop 都重算測試稽核（hook 寫，不靠模型）：被刪、被 skip、斷言變少
python3 "$(dirname "$0")/test_audit.py" "$ROOT" >/dev/null 2>&1 || true
# 讓 skill 能直接呼叫 timing.py（skill 不知道 plugin 安裝路徑）
mkdir -p "$P/bin" && cp -f "$(dirname "$0")/timing.py" "$P/bin/timing.py" 2>/dev/null || true
[ -f "$P/DONE" ]   && exit 0          # 已收工 → 放行

# 可用環境變數覆寫
HOURS="${NIGHT_SHIFT_HOURS:-8}"            # 沒有 DEADLINE 檔時的預設時長（小時）
MAX_TURNS="${NIGHT_SHIFT_MAX_TURNS:-120}"  # 回合上限（兜底）

now=$(date +%s)
# DEADLINE 由 skill Step 0 依 /sleep 參數寫入；缺少時以預設時長建立
[ -f "$P/START" ] || echo "$now" > "$P/START"
if [ ! -f "$P/DEADLINE" ]; then
  echo $(( now + HOURS * 3600 )) > "$P/DEADLINE"
fi
deadline=$(cat "$P/DEADLINE" 2>/dev/null || echo 0)
remain_min=$(( (deadline - now) / 60 ))
n=$(( $(cat "$P/turns" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$P/turns"

finish() {
  local base; base=$(cat "$P/BASE" 2>/dev/null || echo main)
  echo "夜班結束條件已到（$1）。這是最後一回合：不要再開新的加分項。BASE=${base}。請 (1) 印出 git log --oneline ${base}..HEAD 與 git diff ${base} --name-only，確認 build/test 狀態；(2) 寫入 .agent-pipeline/TIMING（skill Step 6 第 0 點）並補完 .agent-pipeline/result.md；(3) git push -u origin night-shift/<date>；(4) touch .agent-pipeline/DONE 並 rm .agent-pipeline/ACTIVE；(5) 在對話裡輸出 skill Step 6 規定的「報告老闆」收工報告。完成後停止。" >&2
  echo "finishing" > "$P/STATE"
  exit 2
}

# 已要求收尾一次仍未 DONE → 放行，避免無限迴圈
if [ -f "$P/STATE" ] && grep -q finishing "$P/STATE"; then
  exit 0
fi

# 使用者喊停（/wake 或從別的終端機 touch .agent-pipeline/STOP）→ 收尾
if [ -f "$P/STOP" ]; then
  finish "使用者喊停 turns=$n"
fi

# 時間到或回合用完 → 收尾
if [ "$now" -ge "$deadline" ] || [ "$n" -ge "$MAX_TURNS" ]; then
  finish "remaining=${remain_min}min turns=$n"
fi

cat >&2 <<MSG
夜班進行中（第 $n 回合；剩餘約 ${remain_min} 分鐘，或到 $MAX_TURNS 回合為止）。依 i-want-to-sleep:night-shift-job-generator skill 繼續：
- 先確認 scope.md 第 3 節是否全部處理完；沒有就繼續收尾。
- 收尾完成後，從候選清單取下一個加分項（Score 達門檻才做；清單用完就重新調研）。
- 每回合至少執行一個工具，並印出 git status --short 與 build/test 結果。
- 每個加分項獨立 commit，完成即更新 result.md 的加分項表格。
- 收工前不 push；禁改清單見 skill。
MSG
exit 2
