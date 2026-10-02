<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及對工作目錄的假設。最應優先修正的是 SQL 注入與 eval 的使用，因為它們可能導致任意程式碼執行或資料庫損毀。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：`eval` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`cleanup_cache` 使用未加引號的 glob 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗未中止，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | 工作目錄假設：`sync_one` 依賴 `cd` 成功，但未檢查 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | 潛在的變數未初始化：`ahead` 可能為空導致 SQL 錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能因檔名包含換行或空白而錯誤 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，將破壞 SQL 語法，甚至可注入任意 SQL 指令。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對輸入進行單引號跳脫。

**判斷依據**：diff 第 44 行新增的 SQL 插入語句，直接使用變數 `$name` 與 `$BRANCH`，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：`eval` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 repo 目錄名稱，可能包含 shell 特殊字元（如 `;`, `$(...)`, 反引號等），導致任意命令執行。例如，若 repo 名稱為 `x; rm -rf ~`，則會執行 `rm -rf ~`。建議避免使用 `eval`，改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑與參數正確引用。

**判斷依據**：diff 第 55 行使用 `eval` 執行包含變數的字串，其中 `$repo` 來自外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`cleanup_cache` 使用未加引號的 glob 可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 中，`*` 在引號外，若 `$ROOT` 包含空白或特殊字元，可能展開成多個路徑，導致刪除非預期的檔案。此外，若 `.cache` 目錄不存在，`rm` 會報錯但腳本仍繼續執行。建議使用 `rm -rf "$ROOT/.cache"` 或先檢查目錄是否存在，並確保 `$ROOT` 已正確引用。

**判斷依據**：diff 第 61 行，glob 未加引號，且未檢查目錄存在性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗未中止，可能導致資料不一致</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 重導至 log，腳本仍繼續執行。例如，若 `git checkout` 因未提交的變更失敗，後續的 `git merge` 可能基於錯誤的 branch 執行，導致錯誤的同步結果。建議在每個 git 指令後檢查退出碼，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 34-36 行，未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> 工作目錄假設：`sync_one` 依賴 `cd` 成功，但未檢查</summary>

`sync_one` 使用 `cd "$dir"` 切換目錄，若目錄不存在或無權限，`cd` 失敗後續指令將在錯誤的目錄執行，可能操作錯誤的 repo。建議檢查 `cd` 的退出碼，失敗時回報錯誤並跳過該 repo。

**判斷依據**：diff 第 32 行，未檢查 `cd` 的結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> 潛在的變數未初始化：`ahead` 可能為空導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，`ahead` 可能為空字串，後續的 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致 SQL 語法錯誤。建議在 git 指令失敗時設定 `ahead=0` 或中止處理。

**判斷依據**：diff 第 39 行，未處理 git 指令失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能因檔名包含換行或空白而錯誤</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白、換行或特殊字元，將被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

**判斷依據**：diff 第 84 行，使用 `ls` 的輸出進行 word splitting。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1823 ｜ PR #13</sub>