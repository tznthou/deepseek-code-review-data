<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步 repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入（repo 名稱與 branch 未經跳脫直接插入 SQL）、命令注入（hook 使用 eval）、以及錯誤處理不足（git 指令失敗後仍繼續執行並寫入錯誤資料）。此外，使用 ls 解析目錄名稱在特殊字元下可能出錯，且缺少 set -e 導致部分失敗被忽略。建議優先修補 SQL 注入與 eval 的使用，並加入錯誤檢查。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：run_hook 使用 eval 執行未受信任的路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗後仍繼續執行，可能寫入錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 寫入空值或錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄名稱，特殊字元可能導致錯誤 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:1` | 缺少 set -e 或錯誤處理，部分失敗可能被忽略 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL。雖然 branch 有格式驗證，但 repo 名稱完全未驗證。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少使用 `sqlite3` 的 `-cmd` 與 `printf` 進行跳脫。

**判斷依據**：diff 第 41 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 來自 `basename "$dir"`，未經驗證或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：run_hook 使用 eval 執行未受信任的路徑</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自目錄名稱，可能包含 shell 特殊字元（例如 `; rm -rf ~`）。攻擊者可建立惡意名稱的 repo 目錄，導致任意命令執行。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 50 行：`eval "$hook $repo"`，其中 `$repo` 為傳入的目錄名稱，未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗後仍繼續執行，可能寫入錯誤資料</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 重導至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 可能失敗，merge 可能基於舊資料，最後仍會寫入 SQLite，導致報表資料不正確。建議在每個 git 指令後檢查 `$?` 或使用 `set -e`，並在失敗時跳過寫入。

**判斷依據**：diff 第 34-36 行：連續執行 git 指令，無任何錯誤檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 寫入空值或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空，可能導致資料型別錯誤。建議檢查 rev-list 的退出碼，失敗時設定 ahead=0 或跳過。

**判斷依據**：diff 第 38 行：未檢查 rev-list 是否成功。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄名稱，特殊字元可能導致錯誤</summary>

`for d in $(ls "$ROOT")` 使用 ls 的輸出進行 word splitting，若目錄名稱包含空格、換行或 glob 字元，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 68 行：`for d in $(ls "$ROOT"); do`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:1</code> 缺少 set -e 或錯誤處理，部分失敗可能被忽略</summary>

腳本未設定 `set -e` 或 `set -o pipefail`，許多指令失敗後仍會繼續執行，可能導致後續操作基於錯誤狀態。建議在腳本開頭加入 `set -euo pipefail`，並對預期可能失敗的指令（如 grep）明確處理。

**判斷依據**：diff 第 1 行：shebang 後無任何 set 指令。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1575 ｜ PR #13</sub>