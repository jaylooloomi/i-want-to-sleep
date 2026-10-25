---
name: sleep
description: Start a night shift — hand this session over for N hours (default 8). Invoke explicitly as /i-want-to-sleep:sleep in Claude Code or $sleep in Codex.
argument-hint: "[hours] [以 X 為準 | 只收尾 | 只加分 | 重點 X]"
disable-model-invocation: true
---
使用者要離開一段時間，由你接手。立刻依 night-shift-job-generator skill 開始，不要再問任何問題。

參數：$ARGUMENTS
（若上面那行沒有被替換成實際文字，參數就是使用者這則訊息裡 skill 名稱後面的文字。）

- 第一個 token 若是數字 = 執行時數（小時）；沒有就用 8。
- 其餘文字是附加指示：「以 X 為準」「只收尾」「只加分」「重點 X」。

Step 0 時務必依時數寫入 .agent-pipeline/DEADLINE（epoch 秒）。
