---
name: night-shift-job-generator
description: 接手代理。當使用者說「我要睡覺了」「你接手」「幫我做 N 小時」「自己找事做」「night shift」或下 /sleep [hours] 指令時，一定要使用此技能。它會開分支、把當前對話壓成合約（scope.md）、先做完對話中尚未完成的承諾項目，再以原始需求為錨持續調研競品與頂尖做法、評分、實作加分項，一個接一個直到早上，並維護一頁審閱簡報（result.md）。每夜獨立，不讀前幾夜的結果。
---

# Night Shift：收尾 → 持續加分 → 到早上

## 定位

- **一次性**：狀態只來自**當前對話**和**當前 repo**；對話沒有可用工作時，改用 repo 本身的 TODO、失敗測試、roadmap 當錨點（Repo 模式）。本夜若發現 `.agent-pipeline/` 已有舊檔，直接清掉重來。
- **收尾優先於加分，無條件**。承諾過的事沒有優先級可議。
- **加分項不停**：做完一個就挑下一個，直到 Stop hook 宣布時數用完或回合用完。白天也能用：`/sleep 2` 就是接手兩小時。
- **為審閱而設計**：早上使用者只有 30 分鐘。每個加分項獨立 commit、可獨立 revert、result.md 一眼看懂。
- **機制說明**：你不需要自己維持迴圈。只要 `.agent-pipeline/ACTIVE` 存在且 `DONE` 不存在，plugin 的 Stop hook 會在你每次想停下時把你推回來。你的工作是照下面的順序做，並在每回合留下證據。

## 執行環境差異（Claude Code / Codex）

- **子代理**：`scope-reviewer`、`scorer`、`reporter` 是 Claude Code 子代理。在沒有它們的環境（例如 Codex），改用環境提供的子代理／平行 agent 功能，把對應的 `agents/*.md` 內容當指示交給它；若完全沒有子代理能力，自己另開一個獨立步驟照該檔案執行，並在 result.md 對應段落註明「未經獨立審查」。
- **指令**：Claude Code 用 `/i-want-to-sleep:sleep`、`/i-want-to-sleep:wake`；Codex 用 `$sleep`、`$wake`。使用者直接說「我要睡覺了」「接手 N 小時」「停，收工」也一樣觸發，時數從句子裡取。
- **證據檢查 hook**：Codex 會跳過 prompt 型 hook，所以「每回合必做」的證據協議在 Codex 上只能靠你自律，照做。

## 執行順序

### Step 0 — 開分支、立旗標

```bash
git status --porcelain | grep -q . && git stash push -m "night-shift pre-stash"
BASE=$(git branch --show-current)                 # 夜班從「現在所在的分支」開出去
git checkout -b night-shift/$(date +%Y-%m-%d)
rm -rf .agent-pipeline && mkdir -p .agent-pipeline
echo "$BASE" > .agent-pipeline/BASE               # 之後所有 diff / log 都以它為基底，不是 main
touch .agent-pipeline/ACTIVE
HOURS=<來自 /sleep 參數的數字，預設 8>
date +%s > .agent-pipeline/START
echo $(( $(date +%s) + HOURS * 3600 )) > .agent-pipeline/DEADLINE
```

- DEADLINE 是 Stop hook 判斷收工的唯一時間依據；一定要寫，寫錯整晚不會停。
- **測試基線**：開分支後、動任何程式碼前，跑一次完整的單元測試，寫入 `.agent-pipeline/TESTS-START.md`：用的指令、通過／失敗／略過數、每個失敗測試的名稱。這是「交接時就已經壞的」證據，收工時拿來對照。
- BASE 是早上報告的比較基準。凡是本文件寫 `$BASE` 的地方，一律讀 `.agent-pipeline/BASE`，不要寫死 main。
- 有 stash 的變更要寫進 result.md「需要你決定的事」。
- 整晚只在這條分支上。禁止 merge / rebase / reset --hard / --force；push 只在收工時推到這條分支（PreToolUse hook 會擋其他目標，但不要去試）。

### Step 1 — 萃取合約：`.agent-pipeline/scope.md`

回讀**整段對話**，寫出四節。寫錯整晚白做，所以寧可多花一回合。

**對話裡沒有可用的工作時（Repo 模式）**：剛開的新 session、對話只有觸發句、或對話內容與這個 repo 無關 → 改從 repo 本身找錨點，依序蒐集：

```bash
git grep -nE "TODO|FIXME|HACK|XXX" -- ':!.agent-pipeline' | head -50     # 開發者留的待辦
git log --since=30.days --oneline -i -E --grep "wip|暫時|temp|todo|未完成" # 半成品
```
再加上：被 skip / 標 xfail / 目前失敗的測試（跑一次測試看）、README 或 docs 裡的 roadmap／待做清單。

寫 scope.md 時：
- 第 1 節寫「Repo 模式：依 repo 現有方向推進」，下一行列出你判斷的專案目的（一句話，依 README）。
- 第 2 節寫「無（新 session）」。
- 第 3 節放蒐集到的項目，**每項附出處**（檔案:行號 或 commit hash），最多 10 項，挑最具體、最可驗證的；模糊的 TODO（例如「之後重構」）不收。
- 第 4 節寫「無」。
- scope-reviewer 在 Repo 模式下改為檢查：每項出處是否真實存在、是否確實未完成。
- 一個可用錨點都找不到 → 只調研不實作：做 Step 3–4 寫出候選與分數，在 result.md 說明「repo 沒有可錨定的工作」，直接收工。


```markdown
# Scope（YYYY-MM-DD 夜）

## 1. 原始需求
（以使用者「最後一次」修正為準；若被改過，註明改自哪一版。
 使用者在 /sleep 參數給了「以 X 為準」→ 直接採用。）

## 2. 已完成
- …（附檔案或 commit）

## 3. 未完成（收尾清單，依對話先後）
- …（要做什麼 / 驗收標準 / 對話中是否卡住過）

## 4. 已否決
- …（使用者明確說過「不要」「先不管」「不這樣做」的作法）
```

判讀規則：
- 「先不管 X」→ 第 4 節，不是第 3 節。
- 需求被改過 → 舊需求衍生的未完成項目作廢。
- 無法判斷是否仍要做 → 第 3 節末尾標 `[存疑]`，收尾時跳過。

寫完後，**交給 `i-want-to-sleep:scope-reviewer` 子代理複核**（用 Agent/Task 工具呼叫，給它 scope.md 路徑與對話摘要）。它只回報不一致之處：
- `VERDICT: OK` → 繼續。
- `VERDICT: ISSUES` → 依它引用的使用者原話修正 scope.md；它標 `UNCERTAIN` 的項目一律改成 `[存疑]`。不與它爭論：它看的是使用者說了什麼，不是你的理解。

commit：`chore(night-shift): scope`

### Step 2 — 收尾：逐項做完第 3 節

- 依序做，**每項獨立 commit**：`feat|fix(night-shift): <一句話>`。
- 不評分、不挑選。
- 每項完成後 build ＋ 跑相關單元測試。
- 單項失敗重試 3 次仍失敗 → commit 現況，訊息加 `[WIP-FAILED]`，result.md 記錄卡點，跳下一項。
- `[存疑]` 跳過。需要用到第 4 節被否決的作法才能完成 → 不做，記錄。
- `/sleep 只收尾` → 做完這步直接跳 Step 6 收工。
- `/sleep 只加分` → 整步跳過（見下方參數說明）。

### Step 3 — 調研加分候選

先執行 `git log --since=30.days --oneline > .agent-pipeline/recent-commits.md`（scorer 用它剔除已做過的東西）。

以 scope.md 第 1 節為唯一錨點，調研做同類東西的競品 / 頂尖開源專案 / 業界標準做法，產出 3–8 個候選，寫進 `.agent-pipeline/candidates.md`。每個候選**必須**符合這個句型，寫不出來就丟：

> 因為原始需求是 **X**，所以頂尖做法會順便做 **Y**；目前的成果 **沒有 / 只有部分**。

- 每個候選必須記下參考來源（競品名稱、開源專案或文章連結），沒有來源的不算調研成果。
- 與第 4 節（已否決）重疊 → 丟。
- 是「讓專案看起來更專業」而非「讓原始需求做得更好」→ 丟（例：幫回測腳本加 Docker 和 CI）。
- 抄的是功能行為與設計，不是程式碼、UI 素材、文案。GPL / AGPL 程式碼一律不搬。
- 需要新增第三方套件的候選 → 不做，寫進 result.md「需要你決定的事」。

### Step 4 — 評分、挑一個（由 scorer 子代理打分）

**你不給自己的候選打分。** 把 scope.md、candidates.md、recent-commits.md 交給 `i-want-to-sleep:scorer` 子代理，它回傳一張分數表與 `TOP`。評分定義（供你理解，不供你改分）：

| 欄位 | 定義 |
|---|---|
| Impact | 對原始需求目標的實質提升 |
| Urgency | 不做的話使用者最可能先踩到的坑 |
| Effort | 實作複雜度 |
| Blast | 影響既有功能的範圍 |

```
Score = (Impact × Urgency) / (Effort × Blast)
```

- 採用 scorer 的 `TOP`。你唯一能做的覆寫是**往下**：若 TOP 違反圍欄（禁改清單、規模），跳到下一名並在 result.md 註明原因。不得把分數改高、不得跳過 scorer。
- `TOP: none`（全部 < 2）→ 不做。在 result.md「判斷不值得做」把整張表貼上，回到 Step 3 重新調研。連續兩輪 `TOP: none` → 回報並要求收工（touch DONE）。
- 可審閱門檻：預估 ≤ 5 檔、≤ 300 行淨增。超過 → 切片，本輪只做第 1 片（獨立可編譯、獨立可測、合併後不破壞現有功能），其餘各片寫回 candidates.md 當後續候選。
- 把 scorer 的分數表原樣存進 `.agent-pipeline/scores-NN.md`，result.md 的 Score 欄引用它。

### Step 5 — 實作加分項

- 單一方案。先在 result.md 該項的行裡寫要動的檔案與測試案例，附否決的替代作法 2 個各 1 行。不做多方案投票。
- **隔離規則**：每個加分項只改自己新增的檔案，或改既有檔案中自己的區塊；不得改前一個加分項建立的東西。真的要改 → 視為前一項的續做，沿用其編號，不開新項。前後端混合功能守不住時，合併成一個項目，不硬拆。
- 寫 code ＋ 單元測試；build、跑測試。失敗重試 3 次仍失敗 → commit `[WIP-FAILED]`，記錄卡點，進下一個候選。
- commit：`feat(night-shift/bonus-NN): <一句話>`，NN 從 01 遞增。收尾與加分**絕不**混在同一 commit。
- 完成後立刻更新 result.md 的加分項表格，然後回到 Step 4 取下一個候選（清單用完回 Step 3）。

### Step 6 — 收工：`.agent-pipeline/result.md`

Stop hook 會在時間到或回合用完時要求收尾；收到那則指示後，或 `/sleep 只收尾` 做完後：

0. 寫入時間紀錄（報告要用，不可省略）：
   ```bash
   python3 -c "import time;P='.agent-pipeline/';s=int(open(P+'START').read());d=int(open(P+'DEADLINE').read());e=int(time.time());open(P+'END','w').write(str(e));f=lambda t:time.strftime('%Y-%m-%d %H:%M',time.localtime(t));h=lambda x:f'{x//3600}h{x%3600//60:02d}m';r=d-e;open(P+'TIMING','w').write(f'開始 {f(s)}｜結束 {f(e)}｜實際執行 {h(e-s)}／預定 {h(d-s)}'+(f'｜提早 {h(r)} 收工' if r>60 else '')+'\n')"
   cat .agent-pipeline/TIMING
   ```
1. 用 TESTS-START.md 同一個指令再跑一次完整測試，寫入 `.agent-pipeline/TESTS-END.md`（同樣格式）。
2. 印出 `git log --oneline $BASE..HEAD`、`git diff $BASE --name-only`、最後一次 build/test 結果（`$BASE` 讀自 `.agent-pipeline/BASE`）。
2. 補完 result.md（格式如下）。
3. commit `docs(night-shift): result`。
4. `git push -u origin night-shift/<date>`（只允許這條分支；hook 會擋其他目標）。
5. `touch .agent-pipeline/DONE && rm .agent-pipeline/ACTIVE`。
6. **呼叫 `i-want-to-sleep:reporter` 子代理**，把它回傳的報告**原樣**貼在對話裡（這是使用者早上第一眼看到的東西；交給子代理是為了 context 被壓縮後你仍不會漏格式）。它的格式：

```
報告老闆，夜間任務已完成。

收尾：N 項完成、M 項失敗（見 result.md）
加分項：
  1. <名稱> — 參考 <來源>，<一句話做了什麼>，單元測試 ✅/❌
  2. …
修改檔案：<數量> 個（清單見 git diff <BASE> --name-only）
分支：night-shift/<date>，基於 <BASE>（已 push；MR 請對 <BASE> 開，不是 main）
需要你決定：<條數>（見 result.md）
結束原因：時間到 / 回合用完 / 無候選
```

然後停止。

```markdown
# Night Shift Result（YYYY-MM-DD）

## 收尾
| 項目 | 狀態 | commit | 備註 |
|---|---|---|---|

## 加分項（每行一個，可獨立 revert）
| # | 名稱 | commit | Score | 參考來源（競品 / 專案 / 文章） | 做了什麼 | 驗證指令 | 測試狀態 | 否決的替代作法 |
|---|---|---|---|---|---|---|---|---|

## 判斷不值得做
- （名稱 / 分數 / 一句原因）

## 測試對照
| | 通過 | 失敗 | 略過 |
|---|---|---|---|
| 交接時（TESTS-START） | | | |
| 收工時（TESTS-END） | | | |

交接時就失敗的測試：…（逐一列出，標明收工時是否已修）
收工時新增的失敗：…（應為零；不為零要說明）
測試稽核：原樣貼上 `.agent-pipeline/test-audit.md`（由 hook 產生，列出被刪除的測試檔、淨減的測試案例與斷言、新增的 skip/xfail），每條補一句理由；不得刪改。

## 提案（只提案模式，或判斷不該擅自實作的候選）
| 名稱 | Score | 參考來源 | 預估規模 | 為什麼值得做 |
|---|---|---|---|---|

## 被防線擋下的動作
（逐行對應 `.agent-pipeline/blocked.log`，由 hook 寫入，不得刪改。每行補上：當時想做什麼、被擋後怎麼處理。沒有就寫「無」。）
| 時間 | 規則 | 指令／檔案 | 當時想做什麼 | 後來怎麼做 |
|---|---|---|---|---|

## 需要你決定的事
- （存疑項目、被否決作法擋住的收尾、需要新套件的候選、stash 的變更、被防線擋下的動作）

## 統計
- 回合數、commit 數、檔案數、淨增行數、最後 build/test 結果、結束原因（時間到 / 回合用完 / 無候選）
```

result.md 從 Step 1 起就要存在並隨時更新，不要留到最後才寫——context 可能在半夜被壓縮，檔案是唯一可靠的記憶。

## 提前結束

使用者下 `/i-want-to-sleep:wake`、在對話裡說「醒來」「停」「先到這裡」「stop」「wake up」，或從別的終端機 `touch .agent-pipeline/STOP`：

1. 若 STOP 檔還不存在，`touch .agent-pipeline/STOP`（Stop hook 看到它就只允許收工）。
2. 不開新項目。正在做的那一項：使用者說「立刻 / now」→ 直接 commit 現況，訊息加 `[WIP-STOPPED]`；否則做完它再 commit。
3. 執行 Step 6 收工（TIMING、result.md、push、報告）。結束原因寫「使用者喊停」。

## 每回合必做（證據協議）

每回合結束前印出 `git status --short`，以及該回合若有 build/test 則印出結果摘要。這是給早上的使用者看的，也避免「連續幾回合沒用工具」被系統判定無進度而停機。

另有一個小模型的 Stop hook 每回合檢查：這回合有沒有用工具、有沒有印 git status、聲稱測試通過時 transcript 裡有沒有對應輸出、開新加分項前有沒有先 commit 前一個。它只指出缺哪一樣證據，不判斷工作做完沒。被它擋下就補上那樣東西，不要辯解。

## 硬性圍欄

| 類別 | 規則 |
|---|---|
| Git | 只在 `night-shift/*` 分支；push 只允許到該分支；禁 merge / rebase / reset --hard / --force / 切回主分支 |
| 禁改清單 | CI 設定、資料庫 migration、`appsettings*` / `*.config` / `.env*`、`*.csproj` / `package.json` / lock 檔 / `requirements*` |
| 依賴 | 禁止新增第三方套件 |
| 規模 | 單一加分項 ≤ 5 檔、≤ 300 行淨增；超過就切片 |
| 測試 | 只跑不碰資料庫、網路、外部服務的單元測試 |
| 品質門檻 | Score < 2 不做 |

PreToolUse hook 會實際阻擋 Git / 禁改清單 / 套件安裝，並把每次阻擋寫進 `.agent-pipeline/blocked.log`。被擋就在 result.md「被防線擋下的動作」補上意圖與處理方式，不要繞。

## /sleep 參數

- `<數字>`（第一個 token）：執行時數，預設 8。例：`/sleep 2`、`/sleep 8 只收尾`。
- `以 X 為準`：scope.md 第 1 節直接採用。
- `只收尾`：跳過 Step 3–5。
- `只提案`（或 `propose only`）：Step 2 照做（你交代的事做完）；Step 3–4 只跑一輪，候選與分數寫進 result.md「提案」段落，**不實作任何加分項**，然後直接 Step 6 收工。範圍邊界與時數無關。
- `只加分`：跳過 Step 2。scope.md 第 3 節照寫，但不做，原樣列進 result.md「需要你決定的事」。
- `重點 X`（或 `focus on X`）：寫進 scope.md 第 1 節末行「本次重點：X」。Step 3 只調研與 X 有關的候選；scorer 的 Impact 以「對 X 的提升」評分。原始需求不變。

## 不要做的事

- 不讀前幾夜的任何檔案。
- 不做三方案投票。
- 不自己給候選打分、不改 scorer 的分數。
- 不略過 scope-reviewer。
- 收工報告由 reporter 產生，不自己寫。
- 不把收尾和加分混在同一 commit。
- 不為了「看起來更專業」加東西。
- 不做接不回原始需求的加分項。
- 不在做完一個加分項後停下來——除非 Stop hook 要你收工。
