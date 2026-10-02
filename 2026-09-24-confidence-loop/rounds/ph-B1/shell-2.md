<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及變數作用域問題。最優先應修復 SQL 注入與 eval 的使用，並改善錯誤處理與日誌記錄。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 可能刪除任意檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗且未處理 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:88` | 變數作用域錯誤：在 main 函式內使用 local 但未宣告為函式 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能導致問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式並正確跳脫。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook</summary>

`run_hook` 使用 `eval "$hook $repo"`，若 `$repo` 包含 shell 特殊字元（例如 `; rm -rf /`），將導致任意命令執行。雖然 `$repo` 來自 `basename`，但 repo 目錄名稱可能包含惡意字元。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 54 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 可能刪除任意檔案</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用 `*` 萬用字元，或使用 `find` 搭配更嚴格的路徑驗證。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時資料，導致錯誤的 ahead 計算或合併失敗。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 30-32 行：`git fetch origin --prune 2>>"$LOG"` 等

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗且未處理</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而中斷腳本。建議檢查 `ahead` 是否為數字，失敗時設為 0 或記錄錯誤。

**判斷依據**：diff 第 36 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:88</code> 變數作用域錯誤：在 main 函式內使用 local 但未宣告為函式</summary>

`main` 函式內使用 `local target="$ROOT/$d"`，但 `local` 只能在函式內使用。若腳本以 `bash` 執行，`local` 在函式外會報錯。建議將 `local` 移除或將整個迴圈包在函式中。

**判斷依據**：diff 第 72 行：`local target="$ROOT/$d"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能導致問題</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會導致迴圈變數分割錯誤。建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：diff 第 70 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1665 ｜ PR #13</sub>