<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及變數作用域問題。最優先應修復 SQL 注入與 eval 的使用，並改善錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook 且未驗證參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數 ahead 可能未賦值導致 SQL 錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:88` | 變數作用域錯誤：在 for 迴圈中使用 local 導致變數全域可見 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能導致問題 | 0.65 |
| 🔸 | Minor | `sandbox/repo_sync.sh:70` | 日誌截斷邏輯可能丟失資料 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`name` 來自 `basename "$dir"`，`BRANCH` 雖有格式驗證，但兩者皆未經 SQL 跳脫即直接嵌入 INSERT 語句。若 repo 目錄名稱包含單引號（例如 `my'repo`），將導致 SQL 語法錯誤或注入任意 SQL。攻擊者若能在 `$ROOT` 下建立惡意名稱的目錄，即可執行任意 SQL 指令。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：第 44 行直接將變數插入 SQL 字串，未使用參數化查詢或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook 且未驗證參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook 腳本。`$repo` 來自 `basename "$dir"`，可能包含 shell 特殊字元（如 `;`, `$(...)`, 反引號）。若 repo 目錄名稱被惡意控制，可注入任意命令。

建議改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 路徑安全。

**判斷依據**：第 55 行使用 eval 將未驗證的變數組合成命令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 中，`*` 未加引號，若 `$ROOT` 包含空格或特殊字元，可能導致路徑解析錯誤。此外，若 `.cache` 目錄不存在，`rm -rf` 會報錯但腳本仍繼續執行。建議先檢查目錄是否存在，並使用 `find` 或正確引號處理。

**判斷依據**：第 61 行 glob 未加引號，且未檢查目錄存在性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的 stderr 被重定向到日誌，但未檢查退出碼。若 fetch 失敗（如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 30-32 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數 ahead 可能未賦值導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git 指令失敗（例如分支不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串導致語法錯誤，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。建議在賦值後檢查是否為空，並設定預設值 0。

**判斷依據**：第 35 行未處理 git 指令失敗時 ahead 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:88</code> 變數作用域錯誤：在 for 迴圈中使用 local 導致變數全域可見</summary>

在 `main` 函數的 for 迴圈中使用 `local target="$ROOT/$d"`，但 `local` 只能在函數內使用，此處 `main` 是函數，所以合法，但 `target` 的作用域是整個 `main` 函數，而非迴圈內。這可能導致後續迭代意外使用前一次的值。建議改用 `declare` 或直接賦值，並注意作用域。

**判斷依據**：第 72 行在 for 迴圈內使用 local，作用域為整個函數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能導致問題</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迭代，若目錄名稱包含空格或換行符，將無法正確處理。建議改用 glob：`for d in "$ROOT"/*/; do` 並去除尾隨斜線。

**判斷依據**：第 82 行使用 ls 輸出進行迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:70</code> 日誌截斷邏輯可能丟失資料</summary>

`summarize` 中若日誌行數超過 100，會將日誌截斷為最後 100 行，但 `total` 變數仍記錄原始行數，導致輸出訊息「本次同步共 $total 筆紀錄」與實際日誌內容不符。建議在截斷後更新 total 或調整訊息。

**判斷依據**：第 67-71 行截斷日誌但未更新 total。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1971 ｜ PR #13</sub>