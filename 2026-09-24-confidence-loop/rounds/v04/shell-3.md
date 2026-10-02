<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供維運報表使用。主要風險在於 SQL 注入（repo 名稱與 branch 名稱直接拼接進 SQL 語句）、路徑處理不當（ls 輸出未加引號、rm -rf 使用未加引號的變數）、以及 eval 執行 hook 可能造成任意程式碼執行。建議優先修正 SQL 注入與路徑處理問題，並考慮移除 eval 或改用更安全的執行方式。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 名稱未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 任意程式碼執行：eval 執行 hook 路徑未受信任 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑未加引號：rm -rf 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | ls 輸出未加引號，路徑含空白時會出錯 | 0.80 |
| 🔸 | Minor | `sandbox/repo_sync.sh:37` | git checkout 未加引號，branch 名稱含特殊字元可能出錯 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 名稱未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串拼接方式插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 指令。例如 repo 名稱若為 `x'); DROP TABLE runs;--`，將導致資料表被刪除。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行跳脫（如將單引號替換為兩個單引號）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 任意程式碼執行：eval 執行 hook 路徑未受信任</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 路徑由 `$ROOT` 決定，而 `$ROOT` 是使用者提供的參數。若攻擊者能控制 `$ROOT`（例如提供一個包含惡意 hook 的目錄），即可執行任意程式碼。建議移除 eval，改用直接執行（如 `"$hook" "$repo"`），並確保 hook 路徑來自受信任的來源。

**判斷依據**：diff 第 55 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑未加引號：rm -rf 可能誤刪檔案</summary>

`cleanup_cache` 函式使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空白或特殊字元，路徑可能被錯誤解析，導致刪除非預期的檔案。建議將整個路徑用雙引號包住：`rm -rf "$ROOT/.cache"/*`。

**判斷依據**：diff 第 60 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> ls 輸出未加引號，路徑含空白時會出錯</summary>

`for d in $(ls "$ROOT")` 使用命令替換，若 repo 目錄名稱包含空白或換行，迴圈會錯誤分割。建議改用 `find` 或 `for d in "$ROOT"/*` 並檢查是否為目錄。

**判斷依據**：diff 第 76 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 未加引號，branch 名稱含特殊字元可能出錯</summary>

`git checkout $BRANCH` 未將 `$BRANCH` 用雙引號包住。雖然開頭有驗證格式，但若 branch 名稱包含空白（例如 `feature branch`），仍可能被 shell 分割。建議改為 `git checkout "$BRANCH"`。

**判斷依據**：diff 第 33 行：`git checkout $BRANCH 2>>"$LOG"`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1243 ｜ PR #13</sub>