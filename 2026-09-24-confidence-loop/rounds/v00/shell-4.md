<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及可能的資料遺失。最優先應修復 SQL 注入與命令注入問題，並加強錯誤處理與輸入驗證。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 刪除快取，可能誤刪重要檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:68` | `summarize` 使用 `grep -c .` 計算行數，可能因檔案不存在或權限問題回傳錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | `for d in $(ls "$ROOT")` 無法處理包含空格或特殊字元的目錄名稱 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:88` | `local target="$ROOT/$d"` 未處理 `$d` 包含斜線或 `..` 的情況 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | `sync_one` 未檢查 `git fetch`、`checkout`、`merge` 的執行結果 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | `ahead` 變數可能為空，導致後續數值比較錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，攻擊者可透過特製的 repo 目錄名稱或 branch 名稱注入任意 SQL，例如建立名為 `x'); DROP TABLE runs;--` 的目錄。建議改用參數化查詢或使用 `sqlite3` 的參數綁定功能，或至少對輸入進行跳脫。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$hook` 與 `$repo` 來自使用者控制的目錄結構。攻擊者可建立惡意 hook 檔案或 repo 名稱包含 shell 指令，導致任意命令執行。建議改用直接執行並傳遞參數的方式，例如 `"$hook" "$repo"`，並避免使用 `eval`。

**判斷依據**：diff 第 56 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 刪除快取，可能誤刪重要檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未正確設定或包含符號連結，可能導致刪除非預期的檔案。建議檢查路徑是否存在且為預期的快取目錄，並考慮使用更安全的刪除方式。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:68</code> `summarize` 使用 `grep -c .` 計算行數，可能因檔案不存在或權限問題回傳錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `grep` 失敗時會設定 `total=0`，但若 `$LOG` 不存在，`grep` 會回傳非零狀態，導致 `total` 被設為 0，但後續 `tail` 仍可能失敗。建議先檢查檔案是否存在。

**判斷依據**：diff 第 71 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> `for d in $(ls "$ROOT")` 無法處理包含空格或特殊字元的目錄名稱</summary>

使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或特殊字元，會導致路徑解析錯誤。建議改用 `find` 或 globbing，例如 `for d in "$ROOT"/*/; do`。

**判斷依據**：diff 第 82 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:88</code> `local target="$ROOT/$d"` 未處理 `$d` 包含斜線或 `..` 的情況</summary>

若 `$d` 包含斜線或 `..`，可能導致路徑穿越，存取非預期的目錄。建議驗證 `$d` 是否為合法目錄名稱，或使用 `basename` 處理。

**判斷依據**：diff 第 84 行：`local target="$ROOT/$d"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> `sync_one` 未檢查 `git fetch`、`checkout`、`merge` 的執行結果</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向至 log，未檢查回傳值。若 fetch 失敗或 branch 不存在，後續指令可能在不正確的狀態下執行，導致資料不一致。建議檢查每個指令的回傳值並在失敗時中止。

**判斷依據**：diff 第 30-32 行：`git fetch origin --prune 2>>"$LOG"`、`git checkout $BRANCH 2>>"$LOG"`、`git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 變數可能為空，導致後續數值比較錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗，`ahead` 可能為空字串，後續 `[ "$ahead" -gt 0 ]` 會因非整數而報錯。建議在指令失敗時設定預設值，例如 `ahead=0`。

**判斷依據**：diff 第 35 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1905 ｜ PR #13</sub>