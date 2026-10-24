---
description: 接手跑 N 小時（預設 8）— 依 night-shift-job-generator skill 收尾並持續加分
argument-hint: [hours] [以 X 為準 | 只收尾 | 只加分 | 重點 X]
---
使用者要離開一段時間，由你接手。立刻依 i-want-to-sleep:night-shift-job-generator skill 開始，不要再問任何問題。

參數：$ARGUMENTS
- 第一個 token 若是數字 = 執行時數（小時）；沒有就用 8。
- 其餘文字是附加指示（例如「以 X 為準」「只收尾」「只加分」「重點 效能」）。

Step 0 時務必依時數寫入 .agent-pipeline/DEADLINE（epoch 秒）。
