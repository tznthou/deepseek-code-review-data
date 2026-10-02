<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與資源管理問題。最優先應修復 SQL 注入與命令注入漏洞，並改善錯誤處理與路徑驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`cleanup_cache` 使用未加引號的 glob 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗時腳本仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 路徑處理不當：`ls` 輸出未正確處理包含空白或換行的檔名 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:1` | 缺少 `set -e` 或錯誤處理，可能導致部分失敗被忽略 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | 變數 `ahead` 可能未初始化或為空，導致數值比較錯誤 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令使用字串拼接方式插入 `$name` 與 `$BRANCH`，若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 指令，導致資料庫內容被竄改或破壞。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，或至少使用 `sqlite3` 的參數綁定功能（例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 直接插入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook，其中 `$hook` 與 `$repo` 來自檔案系統與使用者輸入。若 hook 路徑或 repo 名稱包含 shell 特殊字元（如 `;`, `$(...)`, `` ` ``），可能導致任意命令執行。例如 repo 名稱為 `x; rm -rf ~` 時，`eval` 會執行 `rm -rf ~`。

建議避免使用 `eval`，改為直接執行並傳遞參數：`"$hook" "$repo"`，並確保 hook 路徑與 repo 名稱不包含特殊字元。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經任何過濾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`cleanup_cache` 使用未加引號的 glob 可能誤刪檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 包含空白或特殊字元，或 `.cache` 目錄不存在，glob 可能展開為空或錯誤路徑，導致刪除不正確的檔案。例如 `$ROOT` 為 `/tmp/my repos` 時，`"$ROOT"/.cache/*` 會展開為 `/tmp/my repos/.cache/*`，但若 `.cache` 不存在，glob 保持原樣，`rm -rf` 會嘗試刪除名為 `*` 的檔案，可能誤刪其他檔案。

建議先檢查目錄是否存在，並使用 `find` 或 `rm -rf -- "$ROOT/.cache"` 後再重建目錄。

**判斷依據**：diff 第 66 行：`rm -rf "$ROOT"/.cache/*`，未檢查目錄存在性且 glob 可能未展開。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗時腳本仍繼續執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 等指令僅將 stderr 重導向至 log，未檢查退出碼。若 fetch 失敗（如網路問題）或 checkout 失敗（如 branch 不存在），腳本仍會繼續執行後續指令，可能導致錯誤的同步結果或資料庫寫入不正確的資料。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止腳本。

**判斷依據**：diff 第 30-32 行：三個 git 指令均未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 路徑處理不當：`ls` 輸出未正確處理包含空白或換行的檔名</summary>

`main` 中使用 `for d in $(ls "$ROOT")` 迭代 repo 目錄，若目錄名稱包含空白或換行，`ls` 的輸出會被 word splitting 拆開，導致 `$d` 不正確，進而跳過或錯誤處理 repo。

建議改用 `find` 或 glob：`for d in "$ROOT"/*/; do`，並去除尾隨斜線。

**判斷依據**：diff 第 84 行：`for d in $(ls "$ROOT"); do`，未使用 `--` 且未處理特殊字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:1</code> 缺少 `set -e` 或錯誤處理，可能導致部分失敗被忽略</summary>

腳本未設定 `set -e` 或 `set -o pipefail`，任何指令失敗（如 `cd` 失敗、`sqlite3` 失敗）都不會中止腳本，可能導致後續指令在不正確的目錄或狀態下執行，產生難以追蹤的錯誤。

建議在腳本開頭加入 `set -euo pipefail`，並對預期可能失敗的指令（如 `grep`）進行適當處理。

**判斷依據**：diff 第 1 行：shebang 後未設定 `set -e` 等選項。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> 變數 `ahead` 可能未初始化或為空，導致數值比較錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 `sqlite3` 插入時 `$ahead` 為空可能導致 SQL 錯誤。

建議在取得 `ahead` 後檢查是否為數字，或設定預設值 0。

**判斷依據**：diff 第 34 行：未檢查 `git rev-list` 的退出碼或輸出是否為數字。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 2065 ｜ PR #13</sub>