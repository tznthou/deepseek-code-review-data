<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足、並發問題及資源清理不當。最優先應修復 SQL 注入與 eval 的使用，並補強錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 可能為空導致數值比較錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:68` | summarize 中 total 計算錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 解析目錄名稱，可能因空格或換行出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函數外使用 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入。例如 repo 名稱為 `x' ; DROP TABLE runs; --` 時，會執行惡意 SQL。建議使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook</summary>

`run_hook` 使用 `eval "$hook $repo"`。若 `$repo` 包含 shell 特殊字元（例如 `; rm -rf ~`），將被執行。雖然 repo 名稱來自目錄名稱，但攻擊者可能建立惡意目錄名稱。建議改用直接執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的失敗僅被重導向至 log，腳本仍繼續執行。例如 checkout 失敗（branch 不存在）時，後續 merge 可能基於錯誤的 branch，導致錯誤結果。建議檢查每個 git 指令的 exit code，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 35-37 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空導致數值比較錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，ahead 為空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入空值可能導致錯誤。建議在 git 指令失敗時設定 ahead=0 或直接跳過。

**判斷依據**：diff 第 39-41 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含空格，可能刪除非預期檔案。且無任何防護，若 `$ROOT` 為 `/` 將刪除 `/.cache/*`。建議檢查路徑是否為預期目錄，或使用更安全的清理方式。

**判斷依據**：diff 第 58 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 失敗（例如檔案不存在），total 會被設為 0，但若 grep 成功但檔案為空，total 為 0 且 exit code 為 1，導致 total 被重設為 0，但實際上應為 0。此處邏輯正確但易混淆。更嚴重的問題是若 log 檔案不存在，grep 失敗，total=0，但後續 `tail -100 "$LOG"` 會失敗。建議先檢查檔案存在。

**判斷依據**：diff 第 68 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 解析目錄名稱，可能因空格或換行出錯</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會被拆成多個欄位。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 76 行

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函數外使用</summary>

`local target="$ROOT/$d"` 在 `main` 函數內使用，但 `local` 僅在函數內有效，此處正確。但若腳本被 source 而非執行，可能汙染全域變數。建議改用 `declare` 或直接賦值。

**判斷依據**：diff 第 78 行

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1774 ｜ PR #13</sub>