<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（透過 eval 執行 hook）、路徑處理不當（ls 解析、rm -rf 使用變數）、以及錯誤處理不足（git 指令失敗未中止）。最該先修的是 SQL 注入與 eval 的使用，因為它們可能被惡意 repo 名稱或 hook 利用。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 危險的 rm -rf 使用：路徑未驗證可能導致意外刪除 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | ls 輸出解析脆弱：檔名包含空白或換行會導致錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能導致後續操作在錯誤狀態下執行 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 變數可能未初始化，導致 SQL 插入空值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL。攻擊者可以建立惡意名稱的 repo 目錄，導致資料庫被竄改或資料外洩。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 和 `$repo` 都來自外部輸入（`$ROOT` 和 repo 名稱），如果 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），可能導致任意命令執行。即使 hook 檔案本身是受信任的，repo 名稱仍可能被利用。建議避免使用 eval，改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑是固定的。

**判斷依據**：diff 第 53 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 危險的 rm -rf 使用：路徑未驗證可能導致意外刪除</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。如果 `$ROOT` 未設定或為空，會變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，如果 `.cache` 是符號連結，可能刪除連結目標的內容。建議在使用前檢查 `$ROOT` 非空且為目錄，並避免使用萬用字元，或改用 `find` 搭配更嚴格的條件。

**判斷依據**：diff 第 58 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> ls 輸出解析脆弱：檔名包含空白或換行會導致錯誤</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，但 `ls` 的輸出會受到檔名中的空白、換行等特殊字元影響而分割錯誤。例如，若 repo 目錄名稱為 `my repo`，會被拆成 `my` 和 `repo` 兩個項目。建議改用 glob：`for d in "$ROOT"/*/; do` 並去除尾隨斜線，或使用 `find` 搭配 `-print0` 和 `while read -d ''`。

**判斷依據**：diff 第 68 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能導致後續操作在錯誤狀態下執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將錯誤寫入 log，但腳本繼續執行。例如，若 `git checkout` 失敗（例如 branch 不存在），後續的 `git merge` 和 `git rev-list` 可能在不正確的 branch 上執行，導致資料錯誤。建議在每個 git 指令後檢查退出碼，失敗時 return 或 exit，或使用 `set -e`（但需注意 `set -e` 對管線和條件式的影響）。

**判斷依據**：diff 第 31-35 行：git 指令沒有錯誤處理

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能未初始化，導致 SQL 插入空值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議在指令失敗時設定預設值，例如 `ahead=0`，或檢查退出碼。

**判斷依據**：diff 第 38 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1702 ｜ PR #13</sub>