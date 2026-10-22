# i-want-to-sleep

[English](README.md)

<p align="center"><img src="docs/hero.png" alt="左：白天，想睡的章魚坐在筆電前。/sleep 8。右：夜班，同一隻章魚戴安全帽，八隻觸手拿著扳手、鍵盤、咖啡、測試通過徽章、git 分支、放大鏡、筆記本並打字，終端機顯示 tests passed。" width="900"></p>

說「我要睡覺了」（或 `/i-want-to-sleep:sleep 8`），Claude Code 接手 N 小時：開分支 → 收尾對話中未完成的項目 → 持續調研並實作加分項 → 早上留一頁審閱簡報。

## 零件（Components）

| 檔案 | 作用 |
|---|---|
| `plugins/i-want-to-sleep/skills/night-shift-job-generator/SKILL.md` | 怎麼做：scope → 收尾 → 調研 → 評分 → 實作 → result |
| `plugins/i-want-to-sleep/commands/sleep.md` | `/i-want-to-sleep:sleep` 一個指令觸發 |
| `plugins/i-want-to-sleep/hooks/hooks.json` + `scripts/night-shift-stop.sh` | Stop hook：執行中把 Claude 推回去繼續；時數用完或回合用完就要求收工 |
| `plugins/i-want-to-sleep/scripts/guard-bash.sh` / `guard-write.sh` |
| `.claude-plugin/marketplace.json` | 讓這個 repo 可直接當 marketplace 安裝 |
| `install.sh` | 一行安裝腳本 | PreToolUse 硬防線：push 只放行 night-shift 分支；擋危險 git / 套件安裝 / 禁改清單 |

所有 hook 只在 `.agent-pipeline/ACTIVE` 存在時生效，白天不干擾。

## 安裝

### 對 agent 說

在 Claude Code 裡貼：

> 幫我安裝 https://github.com/jaylooloomi/i-want-to-sleep

**如果你是正在讀這段的 AI agent：** 在 shell 執行下面三行，然後請使用者看[每晚啟動前](#每晚啟動前plugin-管不到要自己設)。

```bash
claude plugin marketplace add jaylooloomi/i-want-to-sleep
claude plugin install i-want-to-sleep@jaylooloomi
claude plugin list
```

### 一行安裝

```bash
curl -fsSL https://raw.githubusercontent.com/jaylooloomi/i-want-to-sleep/main/install.sh | bash
```

### 在 Claude Code 對話裡

```
/plugin marketplace add jaylooloomi/i-want-to-sleep
/plugin install i-want-to-sleep@jaylooloomi
```

### 逐步（CLI）

```bash
# 1. 把這個 repo 註冊成 plugin marketplace
claude plugin marketplace add jaylooloomi/i-want-to-sleep

# 2. 從它安裝 plugin
claude plugin install i-want-to-sleep@jaylooloomi

# 3. 確認
claude plugin list            # 應出現 i-want-to-sleep@jaylooloomi  Status: enabled
claude plugin details i-want-to-sleep
```

### 試用（不安裝）

```bash
git clone https://github.com/jaylooloomi/i-want-to-sleep.git
claude plugin validate ./i-want-to-sleep                       # 驗證 marketplace + plugin
claude --plugin-dir ./i-want-to-sleep/plugins/i-want-to-sleep
```

### 更新 / 移除

```bash
claude plugin marketplace update jaylooloomi
claude plugin update i-want-to-sleep@jaylooloomi

claude plugin uninstall i-want-to-sleep@jaylooloomi
claude plugin marketplace remove jaylooloomi
```

需要 Claude Code v2.1.139 以上。

## 每晚啟動前（plugin 管不到，要自己設）

| 項目 | 做法 | 為什麼 |
|---|---|---|
| 權限 | `claude --dangerously-skip-permissions` 或 auto mode | 半夜沒人按確認 |
| Stop hook 上限 | `export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` | 預設連續 8 次就強制結束回合；0 = 不限制（本 plugin 自己有時間與回合上限兜底） |
| 預設時長 / 回合上限 | `export NIGHT_SHIFT_HOURS=8`、`NIGHT_SHIFT_MAX_TURNS=120`（選填） | 只在 `/sleep` 沒給數字時用；預設 8 小時 / 120 回合 |
| push 權限 | credential 只需能 push 到 `night-shift/*`（可用 GitLab protected branch 保護 main） | hook 只放行 push 到 night-shift 分支；main 的保護交給 server 端 |
| 機器 | 不睡眠；訂閱額度開「等額度重置後繼續」 | 撞用量上限會暫停 |

## 使用

在正在進行的 Claude Code 對話裡：

```
/i-want-to-sleep:sleep            # 8 小時（預設）
/i-want-to-sleep:sleep 2          # 2 小時，白天也能用
/i-want-to-sleep:sleep 8 以「用 SQLite 版本為準」
/i-want-to-sleep:sleep 1 只收尾
```

第一個數字 = 執行時數。或直接說「我要睡覺了」「幫我做 3 小時」。

## 早上

1. 打開對話視窗看「報告老闆」收工報告；細節在 `.agent-pipeline/result.md`。
2. 分支已 push，在 GitLab/GitHub 開 MR 看 diff；逐個加分項決定 merge 或 `git revert`。
   方向不對 → 直接在同一個對話下指令修改。
3. 合併後刪 `.agent-pipeline/`。

## 限制

- 只在 Claude Code（CLI / 桌面版 / Remote Control）可用；claude.ai 聊天視窗無法整晚執行。
- 禁改清單用路徑 pattern 攔，保守版，可能誤殺；被擋的動作會記在 result.md。
- 尚未實跑驗證。第一晚請在場看前幾回合，確認 Stop hook 有把它推回去。
