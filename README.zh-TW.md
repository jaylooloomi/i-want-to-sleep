<h1 align="center">i-want-to-sleep</h1>

<p align="center">
  <b>說一句「我要睡覺了」，醒來看到做完的工作、測過的分支、一頁報告。</b><br>
  一個讓 Claude Code 接手你 session N 小時的 plugin。
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/version-0.4.0-informational" alt="version">
  <img src="https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.139-orange" alt="Claude Code ≥ 2.1.139">
  <img src="https://img.shields.io/badge/harness-%E5%83%85%20Claude%20Code-lightgrey" alt="僅 Claude Code">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-green" alt="English"></a>
</p>

<p align="center"><img src="docs/hero-zh.png" alt="左：白天，想睡的章魚坐在筆電前。/sleep 8。右：夜班，同一隻章魚戴安全帽，八隻觸手拿著扳手、鍵盤、咖啡、測試通過徽章、git 分支、放大鏡、筆記本並打字，終端機顯示 tests passed。" width="900"></p>

## 安裝

照著做，三步。

### 第 1 步：複製下面整段，貼給 Claude Code

```
安裝 Claude Code plugin：
https://github.com/jaylooloomi/i-want-to-sleep

(1) 依序執行：
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi --scope user
claude plugin list

(2) 把 "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP": "0" 合併進
~/.claude/settings.json 的 "env" 物件
（檔案或物件不存在就建，其他既有設定保留）。

做完告訴我，然後停止。
```

### 第 2 步：重開 Claude Code（跳過權限確認）

```bash
claude --dangerously-skip-permissions
```

第一次會跳一個風險確認，按接受。每晚啟動都加這個 flag——這就是你同意「今晚不問我」的動作。

### 第 3 步：在有工作進行中的 session 裡輸入

```
/i-want-to-sleep:sleep 8
```

8 小時後回來看報告。

<details>
<summary><b>只想裝在單一 repo？</b></summary>

第 1 步 (1) 的 `--scope user` 換成 `--scope local`。user scope 是這台機器所有專案都啟用，而且證據檢查 hook 每個 session 每回合會多一次小模型呼叫；local 只在當前 repo。
</details>

<details>
<summary><b>不想用 agent，自己做</b></summary>

```bash
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi          # 加 --scope local 可限單一 repo
```

或一行：

```bash
curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
```

然後設環境變數（二選一）並啟動：

```bash
# A. 寫進 Claude Code 設定（一勞永逸）
#   ~/.claude/settings.json → "env": { "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP": "0" }
# B. 每次 export
export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0

claude --dangerously-skip-permissions
```
</details>

<details>
<summary><b>這些設定在做什麼</b></summary>

| 設定 | 作用 |
|---|---|
| `--dangerously-skip-permissions` | 半夜沒人按確認。不想每次打，可在 repo 的 `.claude/settings.local.json` 寫 `"permissions": { "defaultMode": "bypassPermissions" }`；auto mode 也可以 |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0`（`~/.claude/settings.json` 的 `env`） | Claude Code 預設連續 8 次 stop-hook 續跑就強制結束回合；`0` 取消。plugin 自己有時限與回合上限 |
| `NIGHT_SHIFT_HOURS`（選填，預設 8） | `/sleep` 沒給數字時的時長 |
| `NIGHT_SHIFT_MAX_TURNS`（選填，預設 120） | 回合數兜底 |

權限模式在 session 開啟後就固定了，所以第 1 步做完一定要重開，這是唯一 agent 替你做不了的事。

另外：push 憑證只需能推到 `night-shift/*`，請在 server 端保護 `main`；機器不要睡眠；訂閱方案開「額度重置後繼續」。
</details>

<details>
<summary><b>試用 / 更新 / 移除</b></summary>

```bash
# 試用不安裝
git clone https://github.com/jaylooloomi/i-want-to-sleep.git
claude plugin validate ./i-want-to-sleep
claude --plugin-dir ./i-want-to-sleep/plugins/i-want-to-sleep

# 更新
claude plugin marketplace update jaylooloomi
claude plugin update i-want-to-sleep@jaylooloomi

# 移除
claude plugin uninstall i-want-to-sleep@jaylooloomi
claude plugin marketplace remove jaylooloomi
```

需要 Claude Code v2.1.139 以上。
</details>

## 使用

第一次跑之前先看你在哪條分支。夜班分支是從**你當下的 HEAD** 開出去的，早上的報告以那條分支為比較基準，MR 也該對它開——不是 main。如果你 checkout 在一條不相干的長期分支上，先切換或收掉。

```
/i-want-to-sleep:sleep               # 8 小時（預設）
/i-want-to-sleep:sleep 2             # 2 小時，白天也能用
/i-want-to-sleep:sleep 8 以「用 SQLite 版本為準」
/i-want-to-sleep:sleep 1 只收尾
```

第一個數字是時數，後面的文字會當指示交給 skill。直接說「我要睡覺了」「幫我做 3 小時」也會觸發。

### 早上

1. 看 session 裡的收工報告（做了什麼、參考來源、測試狀態、檔案、需要你決定的事）。細節在 `.agent-pipeline/result.md`。
2. 從 `night-shift/<date>` 開 MR，**目標是你出發的那條分支**（記在 `.agent-pipeline/BASE`）。每個加分項是獨立 commit。
3. 方向不對？在同一個 session 直接說。
4. 合併後刪 `.agent-pipeline/`。

## 為什麼

半夜十二點你停下來，功能做到一半。模型其實可以繼續——context 它有、測試它會跑——但每一回合結尾都是「還有什麼需要嗎？」，沒人在那裡說「有」。

這個 plugin 把那個停頓拿掉，把開著的 session 變成有時限、有防線的自主執行：

| 沒有它 | 有它 |
|---|---|
| 你停，工作就停 | 工作照你指定的小時數繼續 |
| 隔夜 context 不見 | 對話被壓成 `scope.md` 當合約 |
| 「自主」agent 做到離題 | 加分項必須接回你的原始需求、有評分、有門檻 |
| agent 直接 push main、裝套件、改 CI | 被 PreToolUse hook 硬擋，不是靠提示詞 |
| 早上面對 2,000 行 diff | 一個項目一個 commit；要的合併，不要的 `git revert` |

## 運作方式

```
/sleep 8
   │
   ▼
Step 0  記錄 BASE = 當前分支；從它開 night-shift/<date>；ACTIVE 旗標；DEADLINE = 現在 + 8h
Step 1  讀整段對話 → scope.md（原始需求 / 已完成 / 未完成 / 已否決）
Step 2  做完每個未完成項目 — 各自 commit，build + 單元測試，重試 3 次
Step 3  調研競品與頂尖專案，找能服務原始需求的點子
Step 4  評分 (Impact × Urgency) / (Effort × Blast)；低於 2 的跳過
Step 5  實作勝出者並寫測試 — 獨立 commit（bonus-01、bonus-02 …）
   ▲                         │
   └── 回到 Step 4 ◄─────────┘   直到時限
Step 6  push 分支、寫 result.md、在對話裡貼收工報告
```

讓它無人看管也能跑、而且不讓模型自己批改自己作業的三個機制：

- **Stop hook** — 只要 `.agent-pipeline/ACTIVE` 存在，Claude 每次想結束回合都會被推回去並拿到下一步指示。時限到了要求收工一次，之後放行。
- **PreToolUse hooks** — 確定性的 shell script（不經模型），擋住 push 到 `night-shift/*` 以外的分支、`merge` / `rebase` / `reset --hard` / `--force`、`rm -rf`、安裝套件、修改 CI 設定／migration／設定檔／依賴清單。

- **小模型審查層** — 三個位置由另一個便宜的模型（Haiku）檢查主模型，而不是讓它自我認證；這跟 Claude Code `/goal` 用小模型當評估者是同一個想法：

  | 位置 | 誰 | 做什麼 |
  |---|---|---|
  | scope.md 寫完後 | `scope-reviewer` 子代理 | 重讀對話，指出合約哪裡誤讀使用者；它標不確定的項目改成 `[存疑]` 跳過 |
  | 每個加分項之前 | `scorer` 子代理 | 給候選打分；主模型必須採用結果，只能往下不能往上 |
  | 每回合結束 | prompt 型 Stop hook | 檢查這回合有沒有用工具、有沒有印 `git status`、聲稱測試通過時有沒有指令輸出；缺哪一樣就指名退回 |

確定性 hook 在 `ACTIVE` 不存在時不動作。證據檢查 hook 在沒有夜班時會直接回 ok，但每個 session 每回合結束仍會多一次小模型呼叫。

## 相容性

| 執行環境 | 狀態 |
|---|---|
| Claude Code（CLI、桌面版、Remote Control）≥ 2.1.139 | ✅ 支援 |
| claude.ai 網頁 / 手機聊天 | ❌ 無法無人看管地跑 session |
| OpenAI Codex CLI、Cursor、Gemini CLI、Copilot CLI … | ❌ 尚未——skill、`/sleep` 指令、兩種 hook 目前都打包成 Claude Code plugin |

這個 plugin 沒有用 `/goal`，它建立在 Claude Code 的 Stop 與 PreToolUse hook 上。Codex、Cursor、Gemini CLI、Copilot CLI 都有等價的 stop hook 機制（跨環境範例見 [goal-loop](https://github.com/bodecloud/goal-loop)），所以移植可行：流程（`SKILL.md`）原樣搬過去，兩個 shell 防線改成各家的 hook 格式。歡迎 PR。

## 內容物

| 路徑 | 作用 |
|---|---|
| `plugins/i-want-to-sleep/skills/night-shift-job-generator/SKILL.md` | 流程：scope → 收尾 → 調研 → 評分 → 實作 → 報告 |
| `plugins/i-want-to-sleep/commands/sleep.md` | `/i-want-to-sleep:sleep [hours] [指示]` |
| `plugins/i-want-to-sleep/hooks/hooks.json` | 註冊四個 hook（3 個 command、1 個 prompt） |
| `plugins/i-want-to-sleep/scripts/night-shift-stop.sh` | Stop hook：推回去繼續；時限到要求收工 |
| `plugins/i-want-to-sleep/scripts/guard-bash.sh` | PreToolUse：shell 指令防線 |
| `plugins/i-want-to-sleep/scripts/guard-write.sh` | PreToolUse：檔案寫入防線 |
| `plugins/i-want-to-sleep/agents/scope-reviewer.md` | Haiku 子代理：scope.md 第二雙眼睛 |
| `plugins/i-want-to-sleep/agents/scorer.md` | Haiku 子代理：獨立候選評分 |
| `.claude-plugin/marketplace.json` | 讓這個 repo 可直接當 marketplace 安裝 |
| `install.sh` | 一行安裝腳本 |

## 常見問題

**它會 push 到 `main` 嗎？**
不會。Bash 防線只放行 push 到 `night-shift/*`，且不允許 `--force` / `--delete`。但還是請在 server 端保護 `main`——防線是黑名單，黑名單都繞得過。

**它會裝套件嗎？**
不會。`dotnet add package`、`npm install <pkg>`、`pip install` 之類都被擋。需要新套件的點子會寫進 `result.md`「需要你決定的事」。

**什麼擋住它離題？**
每個加分候選都必須寫成「因為需求是 X，所以頂尖做法會順便做 Y」並附來源。由另一個 Haiku 子代理打分——主模型不能給自己的點子評分——低於 2 跳過。

**時限到了但 build 是壞的怎麼辦？**
以 `[WIP-FAILED]` commit 現況，在 `result.md` 說明卡點，報告照寫。不會 force push 也不會 revert。

**它記得前幾晚嗎？**
不記得，刻意的。每次只讀當前對話和當前 repo，Step 0 會清掉 `.agent-pipeline/`。

**白天能用嗎？**
能。`/sleep 2` 就是接手兩小時。名字是玩笑，時限不是。

## 限制

- 防線是 pattern 黑名單，為了不誤殺正常指令偏保守；有心的模型找得到繞法。真正的安全網是分支隔離＋受保護的 `main`。
- 收工報告的格式是 skill 指示；context 半夜被壓縮時可能走樣，以 `result.md` 為準。
- 尚未大規模實戰。第一次跑請盯前幾回合。

## 貢獻

歡迎 issue 與 PR。開 PR 前跑 `claude plugin validate .`。把流程移植到其他環境的話開個 issue，相容性表會連過去。

## 授權

[MIT](LICENSE)
