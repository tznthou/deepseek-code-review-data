<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（透過 eval 執行 hook）、錯誤處理不足（git 指令失敗仍繼續執行）、以及使用全域變數與 ls 解析目錄等可維護性問題。最該先修的是 SQL 注入與 eval 的 hook 執行方式。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook 時未安全處理參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未檢查，可能導致錯誤結果或資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算在 merge 失敗時可能得到錯誤值 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:47` | ahead 可能為空字串，導致 SQL 語法錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄可能因檔名包含換行或空格而失敗 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函式外使用，可能導致非預期行為 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法甚至執行任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行單引號跳脫。

**判斷依據**：第 43 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook 時未安全處理參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$repo` 是 repo 名稱（來自目錄名稱）。若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），可能導致任意命令執行。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 53 行使用 eval 執行字串，且參數未經跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未檢查，可能導致錯誤結果或資料不一致</summary>

`git fetch`、`git checkout`、`git merge` 的輸出被重導到 log，但未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout/merge 可能基於過時的遠端分支，甚至 merge 失敗後仍繼續執行，導致 SQLite 記錄不正確的 ahead 值。建議每個 git 指令後檢查 `$?` 或使用 `set -e`（但需注意 set -e 對管線的影響）。

**判斷依據**：第 37-39 行未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算在 merge 失敗時可能得到錯誤值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 merge 失敗（例如衝突），HEAD 可能停留在舊位置，導致 ahead 計算不準確。且 stderr 被丟棄，無法得知錯誤。建議在 merge 成功後才計算 ahead，並檢查 rev-list 的退出碼。

**判斷依據**：第 41 行未檢查 merge 是否成功。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:47</code> ahead 可能為空字串，導致 SQL 語法錯誤</summary>

若 `git rev-list` 失敗（例如 HEAD 不存在），`ahead` 會是空字串，插入 SQL 時會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 錯誤。建議在插入前檢查 ahead 是否為數字，或設定預設值 0。

**判斷依據**：第 45 行直接使用可能為空的 ahead。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查路徑是否為預期的快取目錄，或使用更安全的刪除方式（如 find 搭配 -delete）。

**判斷依據**：第 59 行使用 rm -rf 且無防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會導致迴圈變數被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：第 72 行使用 ls 輸出進行迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函式外使用，可能導致非預期行為</summary>

`local target="$ROOT/$d"` 在 `main` 函式內使用，但 `local` 只能在函式內使用，此處合法但可能造成混淆。建議改用一般變數賦值。

**判斷依據**：第 74 行在 main 函式內使用 local，但 main 本身是函式，所以合法，但風格不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1760 ｜ PR #13</sub>