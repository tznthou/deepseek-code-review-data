<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及變數未加引號可能導致的意外行為。最優先應修復 SQL 注入與 eval 的使用，並加強錯誤處理與日誌記錄。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook 且未驗證參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用 rm -rf 可能刪除任意檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未加引號可能導致意外展開 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:43` | ahead 可能為空導致數值比較錯誤 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | ls 輸出未排序且未處理特殊檔名 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 注入。例如 repo 目錄名為 `x'); DROP TABLE runs;--` 時，會執行任意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式並正確跳脫。

**判斷依據**：diff 第 47 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook 且未驗證參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱為 `; rm -rf /`），將導致任意命令執行。建議改用直接執行 `"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時狀態執行，導致錯誤結果。建議在每個 git 指令後檢查 `$?` 並在失敗時中止該 repo 的同步。

**判斷依據**：diff 第 33-35 行：三個 git 指令均未檢查退出碼

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用 rm -rf 可能刪除任意檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用 `*` 萬用字元，或改用 `find` 搭配 `-delete` 並限制深度。

**判斷依據**：diff 第 63 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未加引號可能導致意外展開</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 中，若 `$BRANCH` 包含特殊字元（雖然已驗證格式，但可能包含 `..` 等），可能導致 rev-list 參數解析錯誤。建議對所有變數使用引號，並考慮使用 `--` 分隔選項與參數。

**判斷依據**：diff 第 39 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:43</code> ahead 可能為空導致數值比較錯誤</summary>

若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 可能為空字串，後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而中止腳本。建議先檢查 `ahead` 是否為數字，或設定預設值 0。

**判斷依據**：diff 第 41 行：`if [ "$ahead" -gt 0 ]; then`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> ls 輸出未排序且未處理特殊檔名</summary>

`for d in $(ls "$ROOT")` 會受到 `ls` 的別名或環境影響，且檔名包含空白或換行時會出錯。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 73 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1638 ｜ PR #13</sub>