<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復 SQL 注入與命令注入漏洞，並改善錯誤處理與路徑驗證。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`cleanup_cache` 使用 `rm -rf` 且路徑未驗證 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗未中止，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 路徑遍歷：`for d in $(ls "$ROOT")` 未處理特殊檔名 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:94` | 效能問題：每個 repo 都執行 `git fetch`，可能造成大量網路請求 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行跳脫（如 `sqlite3` 的 `:memory:` 或 `printf '%q'`）。

**判斷依據**：diff 第 41 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 直接拼接。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$hook` 來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 由使用者提供，可能包含惡意內容。攻擊者可控制 `$ROOT` 路徑，使 `$hook` 指向任意可執行檔，並注入額外命令。建議避免使用 `eval`，改為直接執行 `"$hook" "$repo"`，並驗證 `$hook` 為預期的腳本。

**判斷依據**：diff 第 48 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`cleanup_cache` 使用 `rm -rf` 且路徑未驗證</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 為空或包含特殊字元，可能導致刪除非預期檔案。例如，若 `$ROOT` 為 `/`，則會嘗試刪除 `/.cache/*`，可能造成系統損壞。建議檢查 `$ROOT` 是否為有效目錄，並使用更安全的刪除方式（如 `find` 搭配 `-delete`）。

**判斷依據**：diff 第 53 行：`rm -rf "$ROOT"/.cache/*`，未對 `$ROOT` 進行驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗未中止，可能導致資料不一致</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 等指令僅將 stderr 重定向至 log，未檢查退出碼。若 `git fetch` 失敗（如網路問題），後續 `git merge` 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 30-32 行：連續執行 git 指令，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 路徑遍歷：`for d in $(ls "$ROOT")` 未處理特殊檔名</summary>

`main` 使用 `for d in $(ls "$ROOT")` 迭代目錄內容，若檔名包含空格或換行，將被錯誤分割。此外，若 `$ROOT` 包含惡意檔名（如 `..`），可能導致路徑遍歷。建議使用 `find` 或 `for d in "$ROOT"/*` 並正確引用變數。

**判斷依據**：diff 第 72 行：`for d in $(ls "$ROOT"); do`，未處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:94</code> 效能問題：每個 repo 都執行 `git fetch`，可能造成大量網路請求</summary>

若 repo 數量眾多，逐一 `git fetch` 可能耗時較長，且無平行處理。建議考慮使用 `xargs -P` 或平行工具來加速，或至少提供進度提示。

**判斷依據**：diff 第 74 行：在迴圈中呼叫 `sync_one`，其中包含 `git fetch`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1583 ｜ PR #13</sub>