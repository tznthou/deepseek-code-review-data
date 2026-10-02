<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（透過 eval 執行 hook）、路徑處理不當（ls 解析、rm -rf 使用變數）、以及錯誤處理不足。建議先修正安全性問題，再考慮合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗時腳本仍繼續執行 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未初始化：`ahead` 可能為空導致 SQL 錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能受檔名影響 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或使用 `sqlite3` 的 `-cmd` 與 `.parameter` 指令。

**判斷依據**：第 43 行直接將變數嵌入 SQL 字串，且 `$name` 來自 `basename "$dir"`，`$dir` 來自 `ls "$ROOT"` 的輸出，皆為外部可控。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$hook` 為 `$ROOT/.hooks/post-sync`，`$repo` 為 repo 名稱。若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），將導致任意命令執行。建議改用陣列方式執行：`"$hook" "$repo"`，並避免使用 `eval`。

**判斷依據**：第 52 行使用 `eval` 執行包含變數的字串，且 `$repo` 來自 `$d`，為 `ls` 輸出，可能包含惡意內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未設定或為空，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `.cache` 不存在，`rm` 會報錯但腳本仍繼續。建議先檢查 `$ROOT` 是否為空，並使用 `find` 或 `rm -rf -- "$ROOT/.cache"` 後再重建目錄。

**判斷依據**：第 58 行直接使用變數拼接路徑，且未檢查 `$ROOT` 是否為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗時腳本仍繼續執行</summary>

`sync_one` 中所有 `git` 指令的 stderr 都被重導至 `$LOG`，但未檢查退出碼。若 `git fetch` 或 `git checkout` 失敗（例如網路問題、branch 不存在），腳本仍會繼續執行後續指令，可能導致錯誤的資料寫入資料庫。建議在每個關鍵指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

**判斷依據**：第 34-36 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未初始化：`ahead` 可能為空導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入時會產生語法錯誤。建議在取得 `ahead` 後檢查是否為數字，或設定預設值 0。

**判斷依據**：第 39 行未處理 `git rev-list` 失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能受檔名影響</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白或換行，將被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：第 72 行使用 `ls` 輸出進行 word splitting。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1539 ｜ PR #13</sub>