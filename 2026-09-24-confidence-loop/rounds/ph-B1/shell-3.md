<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入（repo 名稱與 branch 未經跳脫直接插入 SQL）、`eval` 執行 hook 可能被惡意 repo 名稱利用、`ls` 解析路徑的脆弱性、以及錯誤處理不足（如 `cd` 失敗後仍繼續執行）。建議先修正 SQL 注入與 `eval` 問題，並強化錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | `eval` 執行 hook 可能被惡意 repo 名稱利用 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | `cd` 失敗後未中止，後續 git 指令可能在錯誤目錄執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，路徑含空白或特殊字元時可能出錯 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 與 `git merge` 失敗未處理，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 可能為空字串，導致 SQL 插入錯誤 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 可能誤刪非預期檔案 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 名稱或 branch 包含單引號，可注入任意 SQL。例如 repo 目錄名為 `x'; DROP TABLE runs; --` 時，會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或使用 `sqlite3` 的 `-cmd` 與 `.parameter` 機制，或至少對輸入進行單引號跳脫。

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，且 `$name` 來自 `basename "$dir"`，`$BRANCH` 雖有格式驗證但允許單引號以外的字元，仍可能包含單引號。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> `eval` 執行 hook 可能被惡意 repo 名稱利用</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$repo` 是 repo 名稱（來自 `basename "$dir"`），若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），可注入任意指令。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 50 行使用 eval 執行字串，且 `$repo` 未經任何 sanitization。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> `cd` 失敗後未中止，後續 git 指令可能在錯誤目錄執行</summary>

`sync_one` 中 `cd "$dir"` 若失敗（例如目錄不存在或權限不足），腳本不會停止，後續 `git fetch`、`git checkout` 等指令會在錯誤的目錄執行，可能導致非預期行為。建議在 `cd` 後檢查 `$?` 或使用 `set -e`，或改為 `cd "$dir" || return 1`。

**判斷依據**：第 31 行直接 `cd`，未檢查結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，路徑含空白或特殊字元時可能出錯</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出進行分詞，若 repo 目錄名稱包含空白、換行或 glob 字元，會導致迭代錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：第 68 行使用 `ls` 且未加引號，容易受特殊字元影響。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 與 `git merge` 失敗未處理，可能導致資料不一致</summary>

`git checkout $BRANCH` 或 `git merge --ff-only` 失敗時（例如 branch 不存在、有衝突），腳本仍繼續執行，並將錯誤結果寫入資料庫。建議檢查每個 git 指令的 exit code，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 34-35 行未檢查 git 指令的執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 可能為空字串，導致 SQL 插入錯誤</summary>

`ahead=$(git rev-list --count ...)` 若 git 指令失敗（例如 branch 不存在），`ahead` 可能為空字串，後續 `sqlite3` 插入時會產生語法錯誤。建議在插入前檢查 `ahead` 是否為數字，或設定預設值。

**判斷依據**：第 37 行未處理 git 指令失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 可能誤刪非預期檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除不該刪除的檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用 `*` 萬用字元，或改用 `find` 搭配更精確的刪除條件。

**判斷依據**：第 58 行使用 `rm -rf` 且路徑來自使用者輸入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1679 ｜ PR #13</sub>