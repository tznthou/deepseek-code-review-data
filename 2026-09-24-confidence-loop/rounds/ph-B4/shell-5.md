<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個 bash 腳本，用於批次同步多個 git repo 並將結果寫入 sqlite。主要風險在於 SQL 注入（repo 名稱未跳脫）、命令注入（eval 執行 hook）、路徑處理不當（ls 解析、rm -rf 使用變數）、以及錯誤處理不足（git 指令失敗仍繼續）。建議先修正 SQL 注入與 eval 的使用，並加強錯誤處理與日誌記錄。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱未跳脫 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | rm -rf 使用未驗證的變數 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | ls 解析目錄名稱可能失敗 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 可能為空導致 sqlite 錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱未跳脫</summary>

`name` 來自目錄名稱，可能包含單引號等特殊字元，直接拼接進 SQL 語句會造成 SQL 注入。攻擊者可建立名為 `x'); DROP TABLE runs;--` 的 repo 目錄，導致資料庫被破壞。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 44 行直接將變數插入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook</summary>

`eval "$hook $repo"` 會將 `$repo` 的內容當作 shell 指令執行。若 repo 名稱包含惡意內容（例如 `$(rm -rf ~)`），可能造成任意命令執行。建議改用直接執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 51 行使用 eval 執行包含變數的字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> rm -rf 使用未驗證的變數</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或包含特殊字元，可能導致意外刪除。例如 `ROOT` 為 `/` 時會嘗試刪除 `/.cache/*`，風險極高。建議先檢查 `$ROOT` 非空且為絕對路徑，並避免使用萬用字元，或改用 `find` 搭配 `-delete`。

**判斷依據**：第 56 行直接使用變數拼接路徑並執行 rm -rf。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> ls 解析目錄名稱可能失敗</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空白或換行，會被拆成多個參數，導致後續路徑錯誤。建議改用 `for d in "$ROOT"/*/; do` 並去除尾隨斜線，或使用 `find`。

**判斷依據**：第 70 行使用 ls 輸出進行迴圈，未處理特殊字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止</summary>

`git fetch`、`git checkout`、`git merge` 失敗時僅將錯誤寫入 log，腳本仍繼續執行，可能導致後續操作基於錯誤狀態。例如 checkout 失敗後仍執行 merge，可能合併錯誤分支。建議在每個 git 指令後檢查 exit code，失敗即 return 或 exit。

**判斷依據**：第 34-36 行未檢查 git 指令的 exit code。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空導致 sqlite 錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若指令失敗，`ahead` 可能為空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議在取得 ahead 後檢查是否為數字，否則設為 0 或跳過。

**判斷依據**：第 39 行未處理指令失敗的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1362 ｜ PR #13</sub>