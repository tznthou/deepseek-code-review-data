<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。整體結構清楚，有基本的輸入驗證與錯誤處理，但存在幾個高風險問題：SQL 注入、命令注入、錯誤處理不完整、以及潛在的資料遺失。最優先應修復 SQL 注入與命令注入問題，並加強錯誤處理，避免同步失敗卻被記錄為成功。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不完整：git 指令失敗仍繼續執行並記錄成功 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 變數可能為空，導致 SQL 語法錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，導致 `total` 被設為 0 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆後插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 指令。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行 `INSERT INTO runs VALUES('x'); DROP TABLE runs;--', 'main', 0, datetime('now'))`，導致資料表被刪除。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或使用 `sqlite3` 的 `.parameter` 功能。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 皆來自使用者輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元，將導致任意命令執行。例如，若 repo 名稱為 `foo; rm -rf ~`，則會執行 `eval "/path/.hooks/post-sync foo; rm -rf ~"`，造成嚴重後果。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 不包含特殊字元，或使用 `--` 分隔參數。

**判斷依據**：diff 第 55 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不完整：git 指令失敗仍繼續執行並記錄成功</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出被重導至 log，但未檢查其退出狀態。若 fetch 失敗（例如網路問題），後續的 checkout 與 merge 可能基於過時的遠端資訊，甚至 merge 失敗，但腳本仍會繼續執行並將結果寫入資料庫，導致報表顯示同步成功，實際卻未同步。

建議在每個 git 指令後檢查 `$?`，若失敗則記錄錯誤並跳過該 repo，或至少標記為失敗。

**判斷依據**：diff 第 36-39 行：連續執行 git 指令，未檢查退出狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 變數可能為空，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因 `-gt` 需要整數而報錯，且 SQL 插入時 `$ahead` 為空，導致 SQL 語法錯誤。

建議在取得 `ahead` 後檢查是否為數字，若不是則設為 0 或記錄錯誤。

**判斷依據**：diff 第 41 行：未檢查 `git rev-list` 的退出狀態，可能導致 `ahead` 為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 因使用者輸入錯誤而指向敏感目錄（例如 `/`），則會刪除 `/.cache/*`，可能造成系統損壞。雖然 `$ROOT` 是第一個參數，但未驗證其是否為預期的 repos 根目錄。

建議檢查 `$ROOT` 是否存在且為目錄，並確認 `.cache` 子目錄存在後再刪除，或使用更安全的刪除方式（例如 `find ... -delete`）。

**判斷依據**：diff 第 63 行：未驗證 `$ROOT` 的安全性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，導致 `total` 被設為 0</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `$LOG` 不存在時，`grep` 回傳非零，`total` 被設為 0。但若 `$LOG` 存在但為空，`grep -c .` 回傳 0 且退出碼為 1，也會觸發 `|| total=0`，導致 `total` 被設為 0，但實際上 log 是空的，這可能不是預期行為。

建議改用 `total=$(wc -l < "$LOG" 2>/dev/null || echo 0)` 或先檢查檔案是否存在。

**判斷依據**：diff 第 72 行：`grep -c .` 在空檔案時回傳 1，導致 `total` 被設為 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1961 ｜ PR #13</sub>