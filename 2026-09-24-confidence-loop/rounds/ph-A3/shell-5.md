<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（透過 eval）、錯誤處理不足（git 指令失敗仍繼續執行）、以及使用 ls 解析目錄造成的潛在問題。建議先修正安全性與錯誤處理問題再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未檢查，可能導致錯誤結果或資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 寫入空值或錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，可能因檔名包含換行或空格而錯誤 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`name` 與 `BRANCH` 直接以單引號字串拼接進 SQL 語句，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。

建議使用 sqlite3 的參數綁定功能，或至少對單引號進行跳脫（`'` → `''`）。

**判斷依據**：第 48 行直接將變數插入 SQL 字串，且變數來源為檔案系統目錄名稱（可被使用者控制）與命令列參數。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$ROOT/.hooks/post-sync` 檔案名稱或 `$repo` 包含特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。

建議改用直接執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 61 行使用 eval，且參數來自檔案系統路徑與 repo 名稱，可能包含惡意內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未檢查，可能導致錯誤結果或資料不一致</summary>

`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查其退出狀態。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的 ahead 計算或合併失敗。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 38-40 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 寫入空值或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致型別錯誤。

建議檢查指令是否成功，失敗時設定預設值（如 0）或跳過該 repo。

**判斷依據**：第 42 行未檢查命令執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，可能因檔名包含換行或空格而錯誤</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若目錄名稱包含空格或換行，會導致迴圈變數錯誤。

建議改用 glob：`for d in "$ROOT"/*/; do` 或 `find` 搭配 `-print0`。

**判斷依據**：第 72 行使用命令替換與 ls，未正確處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或為空，可能刪除不該刪除的檔案。建議加入檢查，確保 `$ROOT` 非空且 `.cache` 存在。

**判斷依據**：第 66 行直接使用 rm -rf，未做防護。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1451 ｜ PR #13</sub>