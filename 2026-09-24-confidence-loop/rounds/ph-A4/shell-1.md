<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復的是 SQL 注入與命令注入漏洞，其次是路徑驗證與錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval "$hook $repo"` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑刪除風險：`rm -rf "$ROOT"/.cache/*` 可能因 `$ROOT` 未定義或含空格而出錯 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 迴圈中使用 `ls` 解析目錄，可能因檔名包含換行或空格而失敗 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | 錯誤處理不足：`git checkout` 與 `git merge` 失敗後仍繼續執行 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | `ahead` 變數可能未定義或為空，導致 SQL 插入失敗 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `grep -c .` 可能因 log 檔案不存在或權限問題而失敗 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。雖然 branch 有格式驗證，但 repo 名稱完全未驗證。

**失敗情境**：若 `$ROOT` 下有一個名為 `x'; DROP TABLE runs;--` 的目錄，執行後會刪除 `runs` 資料表。

**建議**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對字串進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval "$hook $repo"` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 使用 `eval` 執行 `$hook $repo`。`$hook` 是固定路徑，但 `$repo` 來自目錄名稱，未經驗證。若 repo 名稱包含 shell 特殊字元（例如 `$(rm -rf ~)`），會被執行。

**失敗情境**：若 `$ROOT` 下有名為 `$(touch /tmp/pwned)` 的目錄，執行此腳本會建立 `/tmp/pwned` 檔案。

**建議**：避免使用 `eval`，改用直接執行：`"$hook" "$repo"`。若 hook 需要 shell 解析，應明確限制 repo 名稱格式（例如只允許 `[A-Za-z0-9._-]+`）。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑刪除風險：`rm -rf "$ROOT"/.cache/*` 可能因 `$ROOT` 未定義或含空格而出錯</summary>

`cleanup_cache` 直接使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未設定（例如使用者未傳第一個參數），會變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 包含空格，路徑會被正確引用，但 glob 展開可能不如預期。

**失敗情境**：執行 `./repo_sync.sh`（未帶參數）時，`$ROOT` 為空，`rm -rf /.cache/*` 會嘗試刪除根目錄下的 `.cache` 內容。

**建議**：在 `main` 中檢查 `$ROOT` 是否為空，並確保其為絕對路徑。使用 `rm -rf -- "$ROOT/.cache"/*` 並考慮使用 `find` 搭配 `-delete` 更安全。

**判斷依據**：diff 第 57 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 迴圈中使用 `ls` 解析目錄，可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，但 `ls` 的輸出會將檔名中的換行或空格視為分隔符，導致檔名被拆開。若 repo 目錄名稱包含空格，迴圈會將每個部分視為獨立項目。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，迴圈會嘗試處理 `my` 和 `repo` 兩個項目，導致錯誤。

**建議**：使用 `for d in "$ROOT"/*/; do` 或 `find "$ROOT" -maxdepth 1 -mindepth 1 -type d -printf '%f\n'` 並搭配 `while IFS= read -r` 處理。

**判斷依據**：diff 第 74 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> 錯誤處理不足：`git checkout` 與 `git merge` 失敗後仍繼續執行</summary>

`sync_one` 中的 `git checkout $BRANCH` 和 `git merge --ff-only "origin/$BRANCH"` 的錯誤僅被重導向到 log，但腳本不會檢查退出碼。若 checkout 或 merge 失敗（例如 branch 不存在、衝突），後續的 `git rev-list` 和 SQL 插入仍會執行，可能記錄錯誤的 ahead 值。

**失敗情境**：若 `$BRANCH` 不存在於 remote，`git checkout` 失敗，但 `git merge` 可能基於錯誤的狀態執行，導致 `ahead` 計算錯誤。

**建議**：在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo（`return 1`）。

**判斷依據**：diff 第 36-37 行：`git checkout $BRANCH 2>>"$LOG"` 和 `git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 變數可能未定義或為空，導致 SQL 插入失敗</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因 `$ahead` 非整數而報錯，且 SQL 插入的 `$ahead` 為空會導致語法錯誤。

**失敗情境**：若 `origin/$BRANCH` 不存在，`git rev-list` 回傳錯誤，`ahead` 為空，`[ "$ahead" -gt 0 ]` 會輸出錯誤訊息，且 SQL 插入失敗。

**建議**：在 `git rev-list` 後檢查退出碼，失敗時設定 `ahead=0` 或跳過該 repo。

**判斷依據**：diff 第 40 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `grep -c .` 可能因 log 檔案不存在或權限問題而失敗</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 中，若 `$LOG` 不存在，`grep` 會回傳非零退出碼，`total` 會被設為 0，但錯誤訊息被隱藏。這可能掩蓋 log 檔案無法寫入的問題。

**失敗情境**：若 `/tmp` 沒有寫入權限，`$LOG` 無法建立，`grep` 失敗，`total` 為 0，但使用者不會知道 log 未記錄。

**建議**：在腳本開頭檢查 log 檔案是否可寫，或使用 `set -e` 並明確處理錯誤。

**判斷依據**：diff 第 62 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2448 ｜ PR #13</sub>