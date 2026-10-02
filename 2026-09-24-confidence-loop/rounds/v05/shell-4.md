<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（透過 eval）、路徑處理不當、錯誤處理不足，以及併發執行時可能發生的競態條件。最優先應修復 SQL 注入與 eval 的使用，並加強錯誤處理與輸入驗證。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:12` | 競態條件：多個實例同時寫入同一 SQLite 資料庫可能導致鎖定或資料損毀 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能因檔名包含換行或空格而失敗 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`name` 與 `BRANCH` 直接以字串串接方式插入 SQL 語句，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 注入。例如，若 repo 目錄名為 `x'; DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$hook` 路徑或 `$repo` 名稱包含惡意內容（例如 `; rm -rf ~`），將導致任意命令執行。建議改用直接執行：`"$hook" "$repo"`，並確保 `$hook` 是受信任的路徑。

**判斷依據**：diff 第 54 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 包含空格或特殊字元，可能導致路徑解析錯誤。此外，若 `.cache` 目錄不存在，glob 未展開時可能刪除非預期檔案。建議先檢查目錄是否存在，並使用 `find` 或正確引號處理。

**判斷依據**：diff 第 60 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的失敗僅記錄到 log，但腳本仍繼續執行後續步驟，可能導致資料不一致或錯誤的 ahead 計算。建議檢查每個 git 指令的 exit code，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 31-33 行：git 指令僅重導向 stderr，未檢查 exit code

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:12</code> 競態條件：多個實例同時寫入同一 SQLite 資料庫可能導致鎖定或資料損毀</summary>

腳本使用固定的 `/tmp/repo_sync.db`，若同時執行多個實例，可能發生資料庫鎖定或寫入衝突。建議使用唯一的資料庫檔案或加入鎖定機制（例如 `flock`）。

**判斷依據**：diff 第 11 行：`DB=/tmp/repo_sync.db`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會導致迴圈變數被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 82 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1389 ｜ PR #13</sub>