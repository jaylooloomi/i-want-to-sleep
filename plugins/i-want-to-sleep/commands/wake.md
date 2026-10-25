---
description: 提前結束夜班 — 收尾並交報告（加「立刻」則不等目前項目做完）
argument-hint: [立刻 | now]
---
使用者要提前結束夜班。依 i-want-to-sleep:night-shift-job-generator skill 的「提前結束」規則執行，不要問問題。

參數：$ARGUMENTS
- 沒有參數：先 `touch .agent-pipeline/STOP`，把目前正在做的那一項做完並 commit（不開新項目），然後執行 Step 6 收工。
- 含「立刻」或「now」：先 `touch .agent-pipeline/STOP`，目前的變更直接 commit（訊息加 `[WIP-STOPPED]`），然後立即執行 Step 6 收工。

結束原因寫「使用者喊停」。
