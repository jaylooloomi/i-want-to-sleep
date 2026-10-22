#!/usr/bin/env bash
# Stop hook：夜班進行中就把 Claude 推回去繼續；白天（沒有 ACTIVE 檔）完全不干擾。
# exit 0 = 允許停止；exit 2 + stderr = 阻止停止，stderr 內容會回給 Claude 當下一回合的指示。
set -u
P="${CLAUDE_PROJECT_DIR:-$PWD}/.agent-pipeline"

[ -f "$P/ACTIVE" ] || exit 0          # 不是夜班 → 正常停止
[ -f "$P/DONE" ]   && exit 0          # 已收工 → 放行

# 可用環境變數覆寫
STOP_AT="${NIGHT_SHIFT_STOP_AT:-06:30}"   # HH:MM，到此時間強制收工
MAX_TURNS="${NIGHT_SHIFT_MAX_TURNS:-120}" # 回合上限（兜底）

now=$(date +%H:%M)
n=$(( $(cat "$P/turns" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$P/turns"

finish() {
  echo "夜班結束條件已到（$1）。這是最後一回合：不要再開新的加分項。請 (1) 印出 git log --oneline main..HEAD 與 git diff main --name-only，確認 build/test 狀態；(2) 補完 .agent-pipeline/result.md；(3) 執行 touch .agent-pipeline/DONE 並 rm .agent-pipeline/ACTIVE。完成後停止。" >&2
  echo "finishing" > "$P/STATE"
  exit 2
}

# 已要求收尾一次仍未 DONE → 放行，避免無限迴圈
if [ -f "$P/STATE" ] && grep -q finishing "$P/STATE"; then
  exit 0
fi

# 時間到（限早上時段，避免晚上 22:00 > 06:30 誤判）或回合用完 → 收尾
if { [[ "$now" > "$STOP_AT" ]] && [[ "$now" < "12:00" ]]; } || [ "$n" -ge "$MAX_TURNS" ]; then
  finish "time=$now turns=$n"
fi

cat >&2 <<MSG
夜班進行中（第 $n 回合；到 $STOP_AT 或 $MAX_TURNS 回合為止）。依 i-want-to-sleep:night-shift-job-generator skill 繼續：
- 先確認 scope.md 第 3 節是否全部處理完；沒有就繼續收尾。
- 收尾完成後，從候選清單取下一個加分項（Score 達門檻才做；清單用完就重新調研）。
- 每回合至少執行一個工具，並印出 git status --short 與 build/test 結果。
- 每個加分項獨立 commit，完成即更新 result.md 的加分項表格。
- 禁止 push；禁改清單見 skill。
MSG
exit 2
