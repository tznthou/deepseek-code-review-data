<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（透過 eval 執行 hook）、路徑處理不當（ls 解析、rm -rf 使用變數）、以及錯誤處理不足（git 指令失敗仍繼續執行）。建議優先修正 SQL 注入與 eval 的使用，並強化錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook 路徑，可能被惡意 repo 名稱利用 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | rm -rf 使用變數路徑，若 ROOT 為空或錯誤可能刪除重要檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未檢查，可能導致後續操作在錯誤狀態下執行 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 插入 NULL 或錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`name` 與 `BRANCH` 直接以字串串接方式插入 SQL 語句，若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'; DROP TABLE runs; --` 時，會執行多餘的 SQL 指令。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行跳脫。

**判斷依據**：第 42 行直接將變數插入 SQL 字串，未見任何跳脫或參數化處理。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook 路徑，可能被惡意 repo 名稱利用</summary>

`eval "$hook $repo"` 會將 `$repo` 的內容當作 shell 指令的一部分執行。若 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），將導致任意指令執行。建議避免使用 eval，改為直接執行 `"$hook" "$repo"`，並確保 hook 路徑安全。

**判斷依據**：第 52 行使用 eval 執行包含變數的字串，且 repo 名稱來自目錄名稱，可能包含惡意字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> rm -rf 使用變數路徑，若 ROOT 為空或錯誤可能刪除重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未設定或為空字串，將展開為 `rm -rf /.cache/*`，可能刪除系統檔案。建議在使用前檢查 `$ROOT` 是否為空，並使用更安全的路徑處理方式。

**判斷依據**：第 58 行直接使用 `$ROOT` 變數，未檢查是否為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若目錄名稱包含空白或換行，將導致錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：第 69 行使用 `ls` 並依賴 word splitting，未使用 null 分隔或 glob。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未檢查，可能導致後續操作在錯誤狀態下執行</summary>

`git fetch`、`git checkout`、`git merge` 的失敗僅將 stderr 重導至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?` 或使用 `set -e`。

**判斷依據**：第 32-34 行連續執行 git 指令，未見任何錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 插入 NULL 或錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，`ahead` 可能為空字串，後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時可能產生 `NULL` 或語法錯誤。建議在取得 ahead 後檢查是否為數字，或設定預設值。

**判斷依據**：第 36 行未處理 git 指令失敗時 ahead 可能為空的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2696 (cache hit 768) ｜ completion tokens 1442 ｜ PR #13</sub>