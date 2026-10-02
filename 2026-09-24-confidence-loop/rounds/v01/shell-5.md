<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（透過 eval 執行 hook）、路徑處理不當（ls 解析、rm -rf 使用變數）以及錯誤處理不足。建議優先修正 SQL 注入與 eval 的使用，並強化輸入驗證與錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook 路徑，可能被惡意 repo 名稱利用 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：rm -rf 使用變數，若 ROOT 為空或包含特殊字元可能造成災難 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 路徑處理不當：使用 ls 解析目錄，檔名包含空白或換行會出錯 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 插入 NULL 或錯誤 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如，若 repo 名稱為 `x'; DROP TABLE runs;--`，則會執行 `INSERT INTO runs VALUES('x'; DROP TABLE runs;--', ...)`，導致資料表被刪除。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或對輸入進行跳脫。

**判斷依據**：第 42 行直接將變數插入 SQL 字串，且 `$name` 來自 `basename "$dir"`，`$BRANCH` 來自使用者輸入（雖有格式驗證，但允許單引號以外的字元，且未跳脫）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook 路徑，可能被惡意 repo 名稱利用</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$repo` 是 repo 名稱（來自目錄名稱）。若 repo 名稱包含 shell 特殊字元（如 `;`、`$(...)`），將可執行任意命令。例如，repo 名稱為 `x; rm -rf /` 時，eval 會執行 `$hook x; rm -rf /`。建議改用陣列方式執行，或對 `$repo` 進行嚴格驗證（僅允許安全字元）。

**判斷依據**：第 50 行使用 eval，且 `$repo` 來自 `$d`（目錄名稱），未經任何驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：rm -rf 使用變數，若 ROOT 為空或包含特殊字元可能造成災難</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未設定或為空，則會變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 包含空白或特殊字元，可能導致非預期行為。建議檢查 `$ROOT` 是否為空，並使用 `--` 分隔選項，或改用 `find` 搭配 `-delete`。

**判斷依據**：第 55 行直接使用 `$ROOT`，且 `$ROOT` 來自命令列參數，未驗證是否為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 路徑處理不當：使用 ls 解析目錄，檔名包含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若目錄名稱包含空白或換行，將無法正確處理。建議改用 glob 或 `find` 搭配 `-print0` 和 `while read -d ''`。

**判斷依據**：第 72 行使用 `$(ls ...)`，未考慮特殊檔名。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 寫入 log，未檢查退出碼。若 fetch 失敗，後續的 merge 可能基於過時的遠端分支，導致錯誤的 ahead 計數。建議在每個 git 指令後檢查 `$?`，失敗時中止該 repo 的處理。

**判斷依據**：第 34-36 行未檢查 git 指令的退出碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 插入 NULL 或錯誤</summary>

`ahead=$(git rev-list --count ...)` 若 git 指令失敗（例如 branch 不存在），`ahead` 可能為空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因 `-gt` 需要整數而報錯，且 SQL 插入時可能產生 `INSERT INTO runs VALUES(..., , ...)` 的語法錯誤。建議在 git 指令失敗時設定預設值（如 0）或中止。

**判斷依據**：第 38 行未檢查 git rev-list 的退出碼，且未處理空值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2696 (cache hit 2688) ｜ completion tokens 1612 ｜ PR #13</sub>