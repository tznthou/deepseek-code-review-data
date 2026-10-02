<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及併發與效能問題。最優先應修復的是 SQL 注入與命令注入漏洞，其次是補上錯誤處理與改用更安全的迴圈方式。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 `ls` 輸出進行迴圈，可能因檔名包含空白或換行而失敗 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 無條件刪除快取目錄，可能誤刪重要檔案 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | `ahead` 變數可能為空，導致 SQL 插入空值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，會造成 SQL 語法錯誤或注入。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式，並對輸入進行跳脫。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經處理直接嵌入 SQL。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 函式使用 `eval "$hook $repo"`，其中 `$hook` 是 `$ROOT/.hooks/post-sync`，而 `$ROOT` 來自使用者輸入，`$repo` 是 repo 名稱。若 `$ROOT` 或 repo 名稱包含 shell 特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。例如，若 repo 名稱為 `x; rm -rf /`，則會執行 `rm -rf /`。建議避免使用 `eval`，改為直接執行 `"$hook" "$repo"`，並確保 hook 路徑與參數經過驗證。

**判斷依據**：diff 第 54 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 函式中的 `git fetch`、`git checkout`、`git merge` 指令僅將 stderr 重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續的 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 31-33 行：三個 git 指令均未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 輸出進行迴圈，可能因檔名包含空白或換行而失敗</summary>

`main` 函式中的 `for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空白、換行或特殊字元，會導致迴圈分割錯誤。建議改用 `find` 或 glob 搭配 null 分隔符，例如 `while IFS= read -r -d '' d; do ... done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)`。

**判斷依據**：diff 第 69 行：`for d in $(ls "$ROOT"); do`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 無條件刪除快取目錄，可能誤刪重要檔案</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 設定錯誤（例如 `/`），可能刪除大量檔案。建議加入防護，例如檢查 `$ROOT` 是否為有效路徑，或限制刪除範圍。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 變數可能為空，導致 SQL 插入空值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串，後續的 SQL 插入會變成 `INSERT INTO runs VALUES('name', 'branch', , datetime('now'))`，造成 SQL 錯誤。建議在指令失敗時設定預設值（例如 0）或跳過該 repo。

**判斷依據**：diff 第 38 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 1536) ｜ completion tokens 1640 ｜ PR #13</sub>