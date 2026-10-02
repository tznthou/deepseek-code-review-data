<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 資料庫。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發執行時可能產生的問題。最優先應修復的是 SQL 注入與命令注入漏洞，其次是路徑驗證與錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能刪除任意檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗後仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:12` | 併發問題：多個實例共用同一個 SQLite 資料庫與 log 檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能因特殊檔名而失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包住後插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法，甚至可執行任意 SQL。例如 repo 目錄名稱為 `x'); DROP TABLE runs;--` 時，會刪除資料表。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式，並對輸入進行跳脫。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 由使用者提供；`$repo` 是 repo 目錄名稱。若攻擊者能控制 repo 目錄名稱（例如建立名為 `; rm -rf ~` 的目錄），或控制 `$ROOT` 下的 `.hooks/post-sync` 檔案內容，即可執行任意命令。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 hook 檔案權限受控。

**判斷依據**：diff 第 55 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能刪除任意檔案</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含符號連結或特殊字元，可能導致刪除非預期的檔案。例如 `$ROOT` 為 `/` 時，會嘗試刪除 `/.cache/*`，可能影響系統。此外，若 `.cache` 是符號連結，`rm -rf` 會跟隨連結刪除目標內容。

建議先驗證 `$ROOT` 是絕對路徑且不為根目錄，並使用 `find` 搭配 `-delete` 或限制刪除範圍。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗後仍繼續執行</summary>

`sync_one` 中，`git fetch`、`git checkout`、`git merge` 的輸出被重導向到 log，但未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時的遠端狀態，導致錯誤的同步結果。此外，`git rev-list --count` 的錯誤輸出被丟棄，若指令失敗，`ahead` 可能為空，導致 SQL 插入失敗。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 33-35 行：`git fetch origin --prune 2>>"$LOG"`、`git checkout $BRANCH 2>>"$LOG"`、`git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:12</code> 併發問題：多個實例共用同一個 SQLite 資料庫與 log 檔案</summary>

腳本使用固定的 `/tmp/repo_sync.db` 與 `/tmp/repo_sync.log`。若同時執行多個實例（例如不同 branch），會互相干擾：SQLite 寫入可能因鎖定而失敗，log 內容會混雜。此外，`summarize` 中的 `tail` 與 `mv` 操作也可能影響其他實例。

建議使用唯一的名稱（例如加入 PID 或時間戳），或使用鎖定機制確保單一實例執行。

**判斷依據**：diff 第 12-13 行：`DB=/tmp/repo_sync.db`、`LOG=/tmp/repo_sync.log`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能因特殊檔名而失敗</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈。若目錄名稱包含空格、換行或特殊字元，會被錯誤分割。此外，`ls` 的輸出可能包含非目錄項目，需額外檢查。

建議改用 `for d in "$ROOT"/*/; do` 並搭配 `basename`，或使用 `find` 搭配 `-mindepth 1 -maxdepth 1 -type d`。

**判斷依據**：diff 第 84 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 1408) ｜ completion tokens 1820 ｜ PR #13</sub>