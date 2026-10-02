<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及變數作用域問題。最優先應修復 SQL 注入與命令注入漏洞，並改善錯誤處理與日誌記錄。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入漏洞 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入漏洞 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 未加引號可能導致參數注入 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 可能為空導致數值比較錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出可能因檔名含空白而錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 宣告在函式外使用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入漏洞</summary>

`$name` 與 `$BRANCH` 直接插入 SQL 字串，未經跳脫。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用 sqlite3 的參數綁定功能，或至少以 `sqlite3_escape` 函數跳脫輸入。

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入漏洞</summary>

`eval "$hook $repo"` 將 hook 路徑與 repo 名稱直接執行。若 repo 名稱包含 shell 特殊字元（如 `;`、`$(...)`），可注入任意命令。例如 repo 名稱為 `x; rm -rf ~` 時，會執行惡意命令。建議改用陣列方式執行，或嚴格驗證 repo 名稱。

**判斷依據**：第 54 行使用 eval 執行未受信任的 repo 名稱。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 未加引號可能導致參數注入</summary>

`git checkout $BRANCH` 未加引號，若 branch 名稱包含空格或特殊字元，可能被 shell 拆解成多個參數。雖然開頭有驗證 branch 格式，但驗證允許 `.`、`/`、`-` 等字元，仍可能造成意外行為。建議改為 `git checkout "$BRANCH"`。

**判斷依據**：第 33 行未加引號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空導致數值比較錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），ahead 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議檢查 git 指令的 exit code，或設定預設值 0。

**判斷依據**：第 36 行未檢查 git 指令是否成功。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查路徑是否為預期目錄，或使用更安全的刪除方式。

**判斷依據**：第 60 行直接使用 rm -rf。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出可能因檔名含空白而錯誤</summary>

`for d in $(ls "$ROOT")` 若 repo 目錄名稱包含空白，會被拆成多個欄位。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 while read。

**判斷依據**：第 72 行使用 ls 輸出進行迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 宣告在函式外使用</summary>

`local target="$ROOT/$d"` 在 main 函式內使用，但 local 只能在函式內使用。此處應為全域變數，建議移除 local 關鍵字。

**判斷依據**：第 74 行在 main 函式內使用 local。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1421 ｜ PR #13</sub>