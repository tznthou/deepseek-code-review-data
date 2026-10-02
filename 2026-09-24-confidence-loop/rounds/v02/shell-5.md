<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 並提供日誌摘要。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復 SQL 注入與 eval 的使用，並強化錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 可能刪除任意目錄 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未初始化：ahead 可能為空導致數值比較錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 迴圈中使用 ls 解析目錄，可能因特殊字元或空格出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:90` | 缺少對 repo 目錄是否為 Git 儲存庫的驗證 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | 日誌摘要計算可能不準確 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，可能導致 SQL 語法錯誤或注入。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或對輸入進行跳脫。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 由使用者提供，可能包含惡意內容。攻擊者可控制 `$ROOT` 路徑，使 `$hook` 指向任意可執行檔，或利用 `$repo` 注入額外命令。建議改用直接執行（如 `"$hook" "$repo"`）並避免 eval。

**判斷依據**：diff 第 50 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 寫入日誌，未檢查退出碼。若 fetch 失敗（如網路問題），後續 checkout/merge 可能基於過時狀態執行，導致錯誤結果。建議在每個 git 指令後檢查 `$?` 並在失敗時中止該 repo 的同步。

**判斷依據**：diff 第 34-36 行：連續執行 git 指令但未檢查退出碼

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 可能刪除任意目錄</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能導致刪除非預期的檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用 `rm -rf` 搭配變數路徑。

**判斷依據**：diff 第 55 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未初始化：ahead 可能為空導致數值比較錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，`ahead` 可能為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串導致語法錯誤。建議在指令失敗時設定預設值（如 `ahead=0`）或檢查退出碼。

**判斷依據**：diff 第 39-41 行：未處理 git rev-list 失敗的情況

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 迴圈中使用 ls 解析目錄，可能因特殊字元或空格出錯</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格或換行，會導致錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 68 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:90</code> 缺少對 repo 目錄是否為 Git 儲存庫的驗證</summary>

`if [ ! -d "$target/.git" ]` 僅檢查 `.git` 目錄是否存在，但未驗證其是否為有效的 Git 儲存庫。若 `.git` 損壞或非 Git 目錄，後續 git 指令可能失敗。建議使用 `git -C "$target" rev-parse --git-dir` 驗證。

**判斷依據**：diff 第 71 行：`if [ ! -d "$target/.git" ]; then`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> 日誌摘要計算可能不準確</summary>

`summarize` 使用 `grep -c .` 計算行數，但若日誌最後一行沒有換行符，可能少算一行。建議使用 `wc -l` 或 `awk 'END{print NR}'`。

**判斷依據**：diff 第 62 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1869 ｜ PR #13</sub>