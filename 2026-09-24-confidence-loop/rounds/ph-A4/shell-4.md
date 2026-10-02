<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足、並發安全性以及資源清理不當。最優先應修復 SQL 注入與命令注入問題，並加強錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git fetch`、`checkout`、`merge` 失敗時腳本仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 任意檔案刪除：`cleanup_cache` 使用未經驗證的路徑執行 `rm -rf` | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 未處理 `git rev-list` 失敗：`ahead` 可能為空導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:12` | 並發安全性：多個實例同時執行時會互相干擾 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，無法處理包含空格或特殊字元的目錄名稱 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | `local` 使用於函數外，可能導致非預期行為 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或注入攻擊。攻擊者可透過建立惡意名稱的 repo 目錄或 branch 來執行任意 SQL 指令，例如刪除資料表或竄改資料。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-quote` 選項或手動跳脫單引號。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`。變數 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 路徑來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 由使用者輸入決定；`$repo` 為 repo 名稱，可能包含 shell 特殊字元。若攻擊者能控制 `$ROOT` 或 repo 名稱，即可注入任意命令。例如 repo 名稱為 `; rm -rf /` 時，`eval` 將執行惡意指令。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 以引號包覆，且 `$hook` 路徑經過驗證。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`。`$hook` 與 `$repo` 未經驗證即傳入 `eval`，存在命令注入風險。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git fetch`、`checkout`、`merge` 失敗時腳本仍繼續執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 指令僅將 stderr 重導向至 log，未檢查退出狀態。若 fetch 失敗（例如網路問題），後續的 checkout 或 merge 可能基於過時的遠端分支，導致同步結果不正確。此外，`git merge --ff-only` 若因衝突失敗，腳本仍會繼續執行並記錄錯誤的 ahead 數。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止。

**判斷依據**：diff 第 31-33 行：三個 git 指令均未檢查退出碼，僅重導向 stderr。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 任意檔案刪除：`cleanup_cache` 使用未經驗證的路徑執行 `rm -rf`</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 為空字串或未設定，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 包含符號連結或特殊路徑，可能導致非預期的刪除。

建議在使用前檢查 `$ROOT` 是否為空，並確保 `.cache` 目錄存在且為預期路徑。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`。`$ROOT` 未經驗證，若為空將導致危險的刪除操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 未處理 `git rev-list` 失敗：`ahead` 可能為空導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 將為空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空會導致語法錯誤。

建議檢查 `git rev-list` 的退出碼，失敗時設定 `ahead=0` 或跳過該 repo。

**判斷依據**：diff 第 36 行：未檢查 `git rev-list` 的退出碼，且 stderr 被丟棄。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:12</code> 並發安全性：多個實例同時執行時會互相干擾</summary>

腳本使用固定的 `/tmp/repo_sync.db` 與 `/tmp/repo_sync.log`，若同時執行多個實例（例如不同 branch 的同步），將導致資料庫寫入衝突或 log 內容混雜。此外，`cleanup_cache` 與 `summarize` 操作也可能互相影響。

建議為每個執行實例使用唯一的暫存檔（例如使用 `mktemp` 或將 PID 加入檔名），或加入鎖定機制。

**判斷依據**：diff 第 12-13 行：使用固定路徑的暫存檔，未考慮並發執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，無法處理包含空格或特殊字元的目錄名稱</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或 glob 字元，將導致迴圈分割錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：diff 第 79 行：使用 `ls` 輸出進行迴圈，未處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> `local` 使用於函數外，可能導致非預期行為</summary>

`main` 函數中的 `local target="$ROOT/$d"` 使用了 `local`，但 `local` 僅能在函數內使用。雖然在 `main` 函數內是合法的，但若未來重構將此段移出函數，將導致錯誤。建議改用一般變數賦值。

**判斷依據**：diff 第 87 行：`local` 在 `main` 函數內使用，但此處可能造成混淆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2293 ｜ PR #13</sub>