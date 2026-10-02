<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入（repo 名稱與 branch 名稱未經跳脫）、命令注入（run_hook 使用 eval）、以及錯誤處理不足（git 指令失敗後仍繼續執行並寫入錯誤資料）。建議先修正 SQL 注入與 eval 的使用，再考慮合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 名稱未跳脫 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗後仍繼續執行，可能寫入錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 的 total 計算可能因 grep 失敗而錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 名稱未跳脫</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 名稱來觸發。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 都來自使用者可控的輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元（例如 `; rm -rf ~`），可能導致任意命令執行。

建議避免使用 eval，改為直接執行並傳遞參數：
```bash
"$hook" "$repo"
```

**判斷依據**：diff 第 51 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗後仍繼續執行，可能寫入錯誤資料</summary>

`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但腳本未檢查其 exit code。若 fetch 失敗（例如網路問題），後續的 checkout 或 merge 可能基於過時的遠端狀態，導致 `ahead` 計算錯誤，並將不正確的資料寫入資料庫。

建議在每個 git 指令後檢查 exit code，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 33-35 行：`git fetch origin --prune 2>>"$LOG"`、`git checkout $BRANCH 2>>"$LOG"`、`git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空會導致 SQL 語法錯誤。

建議在 rev-list 失敗時設定預設值（例如 0）或中止處理。

**判斷依據**：diff 第 39 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。此外，若 `.cache` 不存在，`rm -rf` 不會報錯，但可能掩蓋路徑錯誤。

建議檢查路徑是否存在且為預期的目錄，或使用更安全的刪除方式。

**判斷依據**：diff 第 58 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 的 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 grep 失敗時會將 total 設為 0，但若 log 檔案不存在，grep 會回傳非零，導致 total 為 0，但實際上可能有其他錯誤。此外，若 log 檔案為空，grep -c 會回傳 0 且 exit code 為 1，也會觸發 total=0，但這是正確的。建議明確處理檔案不存在的情況。

**判斷依據**：diff 第 66 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1707 ｜ PR #13</sub>