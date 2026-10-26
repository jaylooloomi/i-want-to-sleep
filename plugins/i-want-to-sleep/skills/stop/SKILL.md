---
name: stop
description: End a running night shift early — finish or commit the current item, then wrap up and report. Same as wake. Invoke explicitly as /i-want-to-sleep:stop in Claude Code or $stop in Codex.
argument-hint: "[立刻 | now]"
disable-model-invocation: true
---
使用者要提前結束夜班。依 night-shift-job-generator skill 的「提前結束」規則執行，不要問問題。

參數：$ARGUMENTS
（若上面那行沒有被替換成實際文字，參數就是使用者這則訊息裡 skill 名稱後面的文字。）

- 沒有參數：先 `touch .agent-pipeline/STOP`，把目前正在做的那一項做完並 commit（不開新項目），然後執行 Step 6 收工。
- 含「立刻」或「now」：先 `touch .agent-pipeline/STOP`，目前的變更直接 commit（訊息加 `[WIP-STOPPED]`），然後立即執行 Step 6 收工。

結束原因寫「使用者喊停」。
