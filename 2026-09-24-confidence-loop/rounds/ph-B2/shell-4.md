<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入（repo 名稱與 branch 未經跳脫直接插入 SQL）、命令注入（eval 執行 hook 時未安全引用參數）、以及多個錯誤處理與資源管理問題（如 git 指令失敗仍繼續執行、cd 失敗未中止、ahead 變數可能為空導致 SQL 錯誤）。此外，cleanup_cache 使用 rm -rf 刪除快取目錄，若 ROOT 未正確設定可能造成意外刪除。建議優先修復 SQL 注入與命令注入問題，並加強錯誤處理。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook 時未安全引用參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | cd 失敗未中止，可能操作錯誤目錄 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 語法錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能造成意外刪除 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空格或換行會出錯 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函式外使用，可能導致非預期行為 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL 語句</summary>

在 `sync_one` 函式中，`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將破壞 SQL 語法或造成注入。雖然 branch 有正規表示式驗證，但 repo 名稱（來自 `basename "$dir"`）完全未驗證。攻擊者可建立惡意名稱的 repo 目錄，導致任意 SQL 執行。

建議使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 42 行新增此 SQL 語句，變數直接拼接。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook 時未安全引用參數</summary>

`run_hook` 函式中使用 `eval "$hook $repo"` 執行外部 hook。`$repo` 來自 `basename "$dir"`，若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），將導致任意命令執行。即使 hook 檔案本身可信，repo 名稱可能由使用者控制（例如從遠端 clone 下來的目錄名稱）。

建議避免使用 eval，改為直接執行並正確引用參數：
```bash
"$hook" "$repo"
```
若 hook 需要 shell 解析，應明確控制輸入或使用陣列傳遞參數。

**判斷依據**：diff 第 52 行新增 eval 呼叫，參數未安全處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出被重導向到 log，但未檢查其退出狀態。若 fetch 失敗（例如網路問題）或 checkout 失敗（例如 branch 不存在），腳本仍會繼續執行後續的 merge 與 SQL 寫入，可能導致錯誤的 ahead 計算或將失敗狀態寫入資料庫。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止。

**判斷依據**：diff 第 32-34 行，未見錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> cd 失敗未中止，可能操作錯誤目錄</summary>

`sync_one` 函式開頭 `cd "$dir"` 未檢查是否成功。若 `$dir` 不存在或無法進入，後續 git 指令將在錯誤的目錄執行（可能是上一個 repo 的目錄或腳本啟動目錄），造成不可預期的結果。

建議改為 `cd "$dir" || return 1` 或 `cd "$dir" || exit 1`。

**判斷依據**：diff 第 30 行，無錯誤檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 將為空字串。後續 SQL 語句 `INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, ...)` 會產生 `VALUES('repo', 'branch', , ...)` 的語法錯誤，且錯誤輸出未重導向，可能中斷腳本。

建議在取得 ahead 後檢查是否為數字，若不是則設為 0 或記錄錯誤。

**判斷依據**：diff 第 38 行，未處理空值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能造成意外刪除</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定（例如為空或指向根目錄），可能刪除不該刪除的檔案。此外，若 `.cache` 目錄不存在，`rm -rf` 不會報錯，但若 `$ROOT` 包含符號連結或特殊路徑，仍有風險。

建議檢查 `$ROOT` 是否為有效目錄，並考慮使用更安全的刪除方式（例如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

**判斷依據**：diff 第 58 行，無路徑驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空格或換行會出錯</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迭代，若 repo 目錄名稱包含空格、換行或特殊字元，將被錯誤分割。建議改用 glob：`for d in "$ROOT"/*/; do` 或使用 `find` 配合 `-print0`。

**判斷依據**：diff 第 72 行，使用 ls 輸出。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函式外使用，可能導致非預期行為</summary>

在 `main` 函式中，`local target="$ROOT/$d"` 使用了 `local`，但 `local` 只能在函式內使用。雖然在 bash 中函式外的 `local` 會被忽略，但可能造成混淆。建議移除 `local` 或改為一般變數賦值。

**判斷依據**：diff 第 74 行，local 使用於函式外。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 2165 ｜ PR #13</sub>