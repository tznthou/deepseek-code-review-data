<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及變數作用域問題。最優先應修復 SQL 注入與 eval 的使用，並加強錯誤處理與輸入驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 路徑處理不當：ls 輸出未正確處理含空格或特殊字元的目錄名稱 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入資料庫 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數 ahead 可能未定義或為空，導致 SQL 插入失敗或錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 未正確設定可能造成災難性刪除 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | 使用 local 關鍵字在函數外，可能導致非預期行為 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少使用 `sqlite3` 的 `:name` 參數綁定。

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，若 `$hook` 或 `$repo` 包含 shell 特殊字元，將導致任意命令執行。例如 repo 名稱為 `; rm -rf ~` 時，會執行刪除指令。建議改用直接執行 `"$hook" "$repo"`，避免 eval。

**判斷依據**：第 50 行使用 eval 執行字串，變數未經安全處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 路徑處理不當：ls 輸出未正確處理含空格或特殊字元的目錄名稱</summary>

`for d in $(ls "$ROOT")` 使用 ls 的輸出進行迴圈，若目錄名稱包含空格、換行或 glob 字元，將導致路徑解析錯誤或意外展開。建議改用 `for d in "$ROOT"/*/` 並搭配 `basename` 或使用 `find` 搭配 `-print0`。

**判斷依據**：第 63 行使用 ls 輸出進行 word splitting，未考慮特殊字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入資料庫</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 寫入 log，未檢查退出碼。若 fetch 失敗，後續 checkout/merge 可能基於過時狀態，且 `ahead` 計算可能不準確，最終將錯誤資料寫入 SQLite。建議在每個 git 指令後檢查 `$?`，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：第 26-28 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數 ahead 可能未定義或為空，導致 SQL 插入失敗或錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。建議在計算後檢查 `ahead` 是否為數字，失敗時設為 0 或中止。

**判斷依據**：第 31 行未處理 git 指令失敗時 ahead 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 未正確設定可能造成災難性刪除</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 為空或未定義，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。建議在使用前檢查 `$ROOT` 非空且為絕對路徑，並避免使用 `*` 萬用字元，改用 `find` 搭配 `-mindepth 1`。

**判斷依據**：第 55 行未驗證 ROOT 路徑，存在誤刪風險。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> 使用 local 關鍵字在函數外，可能導致非預期行為</summary>

`main` 函數中 `local target="$ROOT/$d"` 使用了 `local`，但 `local` 僅能在函數內使用。此處 `main` 是函數，所以合法，但若未來重構將此段移到全域作用域，會導致錯誤。建議移除不必要的 `local` 或確保其位於函數內。

**判斷依據**：第 66 行使用 local，但此處已在函數內，屬合法但易混淆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1703 ｜ PR #13</sub>