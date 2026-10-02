<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及變數未加引號可能導致的路徑問題。最優先應修復 SQL 注入與 eval 的使用，並加強錯誤處理與輸入驗證。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:43` | 變數未加引號可能導致路徑問題 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能導致問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 包含單引號，可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或使用 `sqlite3` 的 `-cmd` 與參數傳遞，或至少對輸入進行跳脫（如 `sqlite3` 的 `quote()` 函數）。

**判斷依據**：diff 第 45 行，直接將變數插入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook 路徑</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$hook` 與 `$repo` 來自外部輸入（repo 名稱）。若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），可執行任意命令。建議改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑與參數正確引用。

**判斷依據**：diff 第 53 行，使用 eval 執行未受信任的輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 中，`*` 未加引號，若 `.cache` 目錄不存在，glob 不會展開，`rm` 會收到字面路徑 `$ROOT/.cache/*`，但 `-f` 會忽略錯誤，不會造成誤刪。然而若 `$ROOT` 包含空格或特殊字元，可能導致路徑解析錯誤。建議使用 `rm -rf "$ROOT/.cache"` 或先檢查目錄存在。

**判斷依據**：diff 第 58 行，glob 未加引號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但腳本未檢查其退出狀態。若 fetch 失敗（如網路問題），後續 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

**判斷依據**：diff 第 36-38 行，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:43</code> 變數未加引號可能導致路徑問題</summary>

`git rev-list --count "origin/$BRANCH"..HEAD` 中，`$BRANCH` 已驗證格式，但 `origin/$BRANCH` 若 branch 包含 `/` 可能被解釋為遠端分支路徑，但這是預期行為。然而 `$ahead` 在 `if [ "$ahead" -gt 0 ]` 中未加引號，若 `$ahead` 為空（如 rev-list 失敗），會導致語法錯誤。建議使用 `[[ -n "$ahead" && "$ahead" -gt 0 ]]` 或先檢查。

**判斷依據**：diff 第 40 行，`$ahead` 可能為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能導致問題</summary>

`for d in $(ls "$ROOT")` 中，若目錄名稱包含空格或換行，會被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 配合 `-print0`。

**判斷依據**：diff 第 67 行，使用 ls 輸出。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1495 ｜ PR #13</sub>