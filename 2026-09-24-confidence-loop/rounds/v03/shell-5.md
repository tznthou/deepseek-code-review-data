<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及對 repo 目錄和 hook 的信任假設。最該先修的是 sync_one 中的 SQL 注入與 git checkout 的錯誤處理，以及 run_hook 的 eval 使用。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 失敗時未中止，可能導致後續操作在錯誤分支上執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:56` | 使用 eval 執行 hook 可能導致命令注入 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 且路徑未驗證，可能刪除任意檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 grep -c 的錯誤處理可能導致 total 為空字串 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能因檔名包含換行或空格而出錯 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 中，`$name` 和 `$BRANCH` 直接插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自目錄名稱，攻擊者可以建立包含單引號的 repo 目錄（例如 `'; DROP TABLE runs; --`），導致 SQL 注入。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或對輸入進行跳脫。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 失敗時未中止，可能導致後續操作在錯誤分支上執行</summary>

`git checkout $BRANCH 2>>"$LOG"` 的退出狀態未檢查。如果 checkout 失敗（例如分支不存在、工作目錄有未提交變更），腳本會繼續執行 `git merge --ff-only "origin/$BRANCH"`，可能合併到錯誤的分支或產生非預期結果。建議加上 `|| return 1` 或 `set -e` 並妥善處理錯誤。

**判斷依據**：diff 第 34 行：`git checkout $BRANCH 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:56</code> 使用 eval 執行 hook 可能導致命令注入</summary>

`eval "$hook $repo"` 將 `$hook` 和 `$repo` 的內容作為 shell 代碼執行。如果 `$hook` 路徑或 `$repo` 名稱包含惡意內容（例如 `; rm -rf /`），可能造成任意命令執行。建議改用直接執行：`"$hook" "$repo"`，並確保 hook 檔案權限受控。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 且路徑未驗證，可能刪除任意檔案</summary>

`rm -rf "$ROOT"/.cache/*` 中，`$ROOT` 來自使用者輸入，若 `$ROOT` 為 `/` 或空字串，可能刪除系統檔案。建議檢查 `$ROOT` 是否為有效目錄且非根目錄，或使用更安全的清理方式（例如 find 搭配 -delete）。

**判斷依據**：diff 第 58 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 grep -c 的錯誤處理可能導致 total 為空字串</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 失敗（例如檔案不存在），`total` 會被設為 0，但若 grep 成功但輸出為空（檔案為空），`total` 會是空字串，後續 `[ "$total" -gt 100 ]` 會出錯。建議使用 `total=$(grep -c . "$LOG" 2>/dev/null || echo 0)` 或先檢查檔案存在。

**判斷依據**：diff 第 68 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能因檔名包含換行或空格而出錯</summary>

`for d in $(ls "$ROOT")` 使用 ls 的輸出進行迴圈，若目錄名稱包含空格或換行，會導致迴圈變數 `$d` 被錯誤分割。建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 78 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2642 (cache hit 2560) ｜ completion tokens 1503 ｜ PR #13</sub>