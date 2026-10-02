<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 並執行 hook。主要風險在於 SQL 注入、命令注入、錯誤處理不足及並發問題。最優先應修復 SQL 注入與 hook 的 eval 使用，並增加錯誤檢查與交易處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗未檢查，可能導致資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 插入空值或錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除整個 .cache 目錄內容，可能誤刪重要檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，可能因檔名包含空格或換行而錯誤 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 與 `BRANCH` 直接以單引號字串拼接進 SQL 語句，若 repo 目錄名稱或 branch 包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符），或至少使用 `sqlite3` 的 `:name` 參數綁定。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 將 hook 路徑與 repo 名稱直接拼接後執行，若 repo 名稱包含 shell 特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。例如 repo 名稱為 `x; rm -rf ~` 時，會執行惡意命令。建議避免使用 eval，改用直接執行並傳遞參數：`"$hook" "$repo"`。

**判斷依據**：diff 第 53 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗未檢查，可能導致資料不一致</summary>

`git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導向至 log，未檢查退出碼。若 checkout 失敗（例如 branch 不存在），後續 merge 可能基於錯誤的 branch 執行，或 merge 失敗時仍繼續寫入資料庫，導致記錄不正確。建議在每個 git 指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

**判斷依據**：diff 第 34-35 行：`git checkout $BRANCH 2>>"$LOG"` 與 `git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 插入空值或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而中止腳本（set -e 未啟用，但可能產生錯誤訊息），且 SQL 插入時 `$ahead` 為空會導致型別錯誤。建議檢查指令退出碼並設定預設值（如 0）。

**判斷依據**：diff 第 38 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除整個 .cache 目錄內容，可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 會刪除 .cache 目錄下所有檔案，若 .cache 路徑因變數錯誤而指向其他位置（例如 ROOT 為空或包含空格），可能造成大規模刪除。建議檢查 .cache 是否存在且為預期目錄，或使用更精確的刪除方式。

**判斷依據**：diff 第 60 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 因檔案不存在而失敗，total 會被設為 0，但若檔案存在但無內容，grep 回傳 1，也會觸發 `|| total=0`，導致 total 為 0 而非實際行數。建議改用 `wc -l` 或檢查檔案存在性。

**判斷依據**：diff 第 72 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，可能因檔名包含空格或換行而錯誤</summary>

`for d in $(ls "$ROOT")` 會將 ls 輸出以空白分割，若 repo 目錄名稱包含空格，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 80 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2642 (cache hit 1536) ｜ completion tokens 1748 ｜ PR #13</sub>