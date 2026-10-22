# i-want-to-sleep

說「我要睡覺了」，Claude Code 接手：開分支 → 收尾對話中未完成的項目 → 持續調研並實作加分項 → 早上留一頁審閱簡報。

## 零件

| 檔案 | 作用 |
|---|---|
| `skills/night-shift-job-generator/SKILL.md` | 怎麼做：scope → 收尾 → 調研 → 評分 → 實作 → result |
| `commands/sleep.md` | `/i-want-to-sleep:sleep` 一個指令觸發 |
| `hooks/hooks.json` + `scripts/night-shift-stop.sh` | Stop hook：夜班中把 Claude 推回去繼續；時間到或回合用完就要求收工 |
| `scripts/guard-bash.sh` / `guard-write.sh` | PreToolUse 硬防線：擋 push / 危險 git / 套件安裝 / 禁改清單 |

所有 hook 只在 `.agent-pipeline/ACTIVE` 存在時生效，白天不干擾。

## 安裝

```bash
# 試用（不安裝）
claude --plugin-dir /path/to/i-want-to-sleep

# 驗證 manifest
claude plugin validate /path/to/i-want-to-sleep
```

正式安裝可加進你自己的 marketplace，或持續用 `--plugin-dir`。

## 每晚啟動前（plugin 管不到，要自己設）

| 項目 | 做法 | 為什麼 |
|---|---|---|
| 權限 | `claude --dangerously-skip-permissions` 或 auto mode | 半夜沒人按確認 |
| Stop hook 上限 | `export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` | 預設連續 8 次就強制結束回合；0 = 不限制（本 plugin 自己有時間與回合上限兜底） |
| 停止時間 / 回合上限 | `export NIGHT_SHIFT_STOP_AT=06:30`、`NIGHT_SHIFT_MAX_TURNS=120`（選填） | 預設 06:30 / 120 回合 |
| push 能力 | `git remote set-url --push origin no_push` 或用無 push 權限的 credential | hook 失效時的最後兜底 |
| 機器 | 不睡眠；訂閱額度開「等額度重置後繼續」 | 撞用量上限會暫停 |

## 使用

在正在進行的 Claude Code 對話裡：

```
/i-want-to-sleep:sleep
/i-want-to-sleep:sleep 以「用 SQLite 版本為準」
/i-want-to-sleep:sleep 只收尾
```

或直接說「我要睡覺了」。

## 早上

1. 看 `.agent-pipeline/result.md`。
2. `git log --oneline main..HEAD`，逐個加分項決定 merge 或 `git revert`。
3. 合併後刪 `.agent-pipeline/`。

## 限制

- 只在 Claude Code（CLI / 桌面版 / Remote Control）可用；claude.ai 聊天視窗無法整晚執行。
- 禁改清單用路徑 pattern 攔，保守版，可能誤殺；被擋的動作會記在 result.md。
- 尚未實跑驗證。第一晚請在場看前幾回合，確認 Stop hook 有把它推回去。
