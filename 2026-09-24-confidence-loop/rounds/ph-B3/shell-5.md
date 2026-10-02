<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個 Bash 腳本，用於批次同步多個 Git 儲存庫並將結果寫入 SQLite。主要風險在於 SQL 注入（repo 名稱與 branch 名稱未經參數化直接插入 SQL）、命令注入（run_hook 使用 eval）、以及多個錯誤處理與併發問題（如 git 指令失敗仍繼續執行、ahead 變數可能為空導致 SQL 錯誤）。建議優先修復 SQL 注入與 eval 的使用，並加強錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 名稱未經參數化直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：run_hook 使用 eval 執行未受信任的參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能導致錯誤結果 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 語法錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 名稱未經參數化直接插入 SQL</summary>

`sync_one` 函數中，`$name` 與 `$BRANCH` 直接拼接進 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號或 SQL 特殊字元，可能導致 SQL 注入，進而破壞資料庫或執行任意 SQL。例如，若 repo 名稱為 `x'; DROP TABLE runs;--`，則會執行惡意 SQL。

建議改用 sqlite3 的參數綁定功能，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或使用 `--` 分隔參數。

**判斷依據**：diff 第 45 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：run_hook 使用 eval 執行未受信任的參數</summary>

`run_hook` 函數使用 `eval "$hook $repo"`，其中 `$repo` 來自 repo 目錄名稱（由 `ls` 取得）。若目錄名稱包含 shell 特殊字元（如 `; rm -rf ~`），可能導致任意命令執行。

建議避免使用 eval，改用直接執行並傳遞參數：
```bash
"$hook" "$repo"
```
若 hook 需要 shell 解析，應明確限制輸入或使用其他安全機制。

**判斷依據**：diff 第 55 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能導致錯誤結果</summary>

`sync_one` 中，`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向至 log，但腳本仍繼續執行。若 fetch 失敗（例如網路問題），後續的 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。此外，若 checkout 失敗（例如 branch 不存在），merge 可能失敗，但腳本仍會計算 ahead 並寫入資料庫。

建議在每個 git 指令後檢查退出碼，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 36-38 行：git 指令僅重導向 stderr，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git rev-list 失敗（例如 branch 不存在），ahead 將為空字串。後續的 SQL 插入會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 語法錯誤。

建議在執行 SQL 前檢查 ahead 是否為數字，或設定預設值（如 0）。

**判斷依據**：diff 第 41 行：ahead 可能為空，且未做檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。此外，若 `.cache` 目錄不存在，`rm -rf` 不會報錯，但若路徑錯誤可能造成嚴重後果。

建議檢查 `.cache` 是否存在且為目錄，並考慮使用更安全的刪除方式（如 find 搭配 -delete）。

**判斷依據**：diff 第 63 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 因檔案不存在而失敗，total 會被設為 0，但若檔案存在但為空，grep 回傳 1，也會觸發 `|| total=0`，導致 total 被設為 0，但實際上檔案可能有內容（例如空行）。這可能影響後續的判斷。

建議改用 `wc -l` 或先檢查檔案是否存在。

**判斷依據**：diff 第 73 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1705 ｜ PR #13</sub>