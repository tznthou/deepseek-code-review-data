<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（eval 使用未受信任的 repo 名稱）、路徑處理不當（ls 解析、rm -rf 使用變數）、錯誤處理不足（git 指令失敗仍繼續）以及併發問題（固定 DB 路徑）。最優先應修復 SQL 注入與 eval 命令注入，並改善路徑處理與錯誤處理。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | rm -rf 使用變數路徑，若 ROOT 為空或錯誤可能刪除大量檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，檔名含空格或換行會出錯 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未檢查，可能導致錯誤結果或資料不一致 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 插入空值或錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:12` | DB 路徑固定為 /tmp/repo_sync.db，多個實例同時執行會互相干擾 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:13` | LOG 路徑固定，多個實例同時執行會互相覆蓋 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 已驗證格式，但 `$name` 來自目錄名稱，完全未驗證。攻擊者若建立名為 `x'); DROP TABLE runs;--` 的目錄，即可執行任意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對單引號進行跳脫。

**判斷依據**：diff 第 42 行，`$name` 來自 `basename "$dir"`（第 29 行），未經驗證。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$repo` 是 repo 名稱（來自目錄名稱），未經驗證。攻擊者可建立名為 `; rm -rf ~` 的目錄，導致任意命令執行。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 51 行，`$repo` 來自 `$d`（第 76 行），未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> rm -rf 使用變數路徑，若 ROOT 為空或錯誤可能刪除大量檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 為空字串，會變成 `rm -rf /.cache/*`，可能刪除系統檔案。雖然 `main` 檢查了 `$BRANCH` 但未檢查 `$ROOT` 是否為空。建議在腳本開頭驗證 `$ROOT` 非空且為目錄，或使用更安全的路徑處理。

**判斷依據**：diff 第 57 行，`$ROOT` 來自命令列參數，未驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，檔名含空格或換行會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 ls 的輸出，若目錄名稱包含空格、換行或特殊字元，迴圈會錯誤分割。建議改用 glob：`for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 76 行，未使用安全的方式迭代目錄。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未檢查，可能導致錯誤結果或資料不一致</summary>

`git fetch`、`git checkout`、`git merge` 的輸出僅重導向到 log，未檢查退出碼。若 fetch 失敗（如網路問題），後續 checkout/merge 可能基於過時資料，甚至 merge 失敗仍繼續執行，導致 ahead 計算錯誤或資料庫記錄不正確。建議每個 git 指令後檢查 `$?` 或使用 `set -e`（但需注意 set -e 的陷阱）。

**判斷依據**：diff 第 35-37 行，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 插入空值或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git 指令失敗（如 branch 不存在），`$ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空可能導致語法錯誤。建議檢查 ahead 是否為數字，或設定預設值。

**判斷依據**：diff 第 39 行，未處理 git 失敗情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:12</code> DB 路徑固定為 /tmp/repo_sync.db，多個實例同時執行會互相干擾</summary>

`DB=/tmp/repo_sync.db` 是固定路徑，若多個使用者或排程同時執行此腳本，會寫入同一個資料庫，導致資料混亂或鎖定問題。建議使用唯一路徑（如包含 PID 或時間戳）或使用鎖定機制。

**判斷依據**：diff 第 13 行，固定路徑。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:13</code> LOG 路徑固定，多個實例同時執行會互相覆蓋</summary>

`LOG=/tmp/repo_sync.log` 是固定路徑，多個實例同時執行會互相覆蓋日誌，導致資訊遺失。建議使用唯一路徑或附加模式。

**判斷依據**：diff 第 14 行，固定路徑。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2696 (cache hit 2688) ｜ completion tokens 1891 ｜ PR #13</sub>