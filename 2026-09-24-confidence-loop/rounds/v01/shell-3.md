<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 並執行 hook。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足及資源清理問題。最優先應修復 SQL 注入與 hook 的 eval 使用，並改善錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：hook 使用 eval 執行未受信任的參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未初始化：ahead 可能為空導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 迴圈使用 ls 輸出解析，檔名含空格或換行會出錯 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:47` | SQL 插入未使用參數化，且未處理 ahead 為空 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:56` | hook 執行未檢查退出碼 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 與 `BRANCH` 直接以字串拼接方式插入 SQL 語句，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行跳脫。

**判斷依據**：diff 第 47 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經處理。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：hook 使用 eval 執行未受信任的參數</summary>

`eval "$hook $repo"` 將 `$repo` 直接拼入命令字串，若 repo 名稱包含 shell 特殊字元（如 `; rm -rf /`），將導致任意命令執行。即使 hook 路徑固定，`$repo` 來自目錄名稱，可能受攻擊者控制。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 55 行：`eval "$hook $repo"`，其中 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 包含空格或特殊字元，可能導致路徑解析錯誤；且若 `.cache` 不存在，glob 未展開時會嘗試刪除字面路徑 `$ROOT/.cache/*`，可能意外刪除其他檔案。建議先檢查目錄存在再刪除，並使用 `find` 或正確引號。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`，未檢查目錄存在且 glob 可能未展開。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的輸出僅重定向到日誌，未檢查退出碼。若 fetch 失敗或 checkout 失敗，後續 merge 可能基於錯誤狀態，導致資料不一致或誤報。建議每個 git 指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

**判斷依據**：diff 第 37-39 行：三個 git 指令均未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未初始化：ahead 可能為空導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 將為空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入時 `$ahead` 為空會導致語法錯誤。建議在指令失敗時設定預設值（如 0）並記錄錯誤。

**判斷依據**：diff 第 42 行：未檢查 git rev-list 的退出碼，可能導致 ahead 為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 迴圈使用 ls 輸出解析，檔名含空格或換行會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 ls 的輸出，若目錄名稱包含空格、換行或特殊字元，迴圈會錯誤分割。建議使用 `find` 或 glob 搭配 null 分隔符，或使用 `for d in "$ROOT"/*/` 並檢查是否為目錄。

**判斷依據**：diff 第 74 行：使用命令替換解析 ls 輸出。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:47</code> SQL 插入未使用參數化，且未處理 ahead 為空</summary>

即使輸入合法，若 `ahead` 為空（如 git 指令失敗），SQL 語句會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致語法錯誤。建議使用參數化查詢並確保 ahead 有預設值。

**判斷依據**：diff 第 47 行：ahead 可能為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:56</code> hook 執行未檢查退出碼</summary>

`eval "$hook $repo"` 未檢查 hook 的退出碼，若 hook 失敗，腳本仍繼續執行，可能導致後續步驟基於不完整狀態。建議檢查退出碼並記錄錯誤。

**判斷依據**：diff 第 55 行：未檢查 eval 的退出碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2696 (cache hit 1664) ｜ completion tokens 1848 ｜ PR #13</sub>