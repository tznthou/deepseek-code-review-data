<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite，並提供日誌與 hook 機制。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復 SQL 注入與命令注入漏洞，並改善錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入漏洞：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入漏洞：run_hook 使用 eval 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用 rm -rf 可能誤刪檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未初始化：ahead 可能為空導致數值比較錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空白或換行會出錯 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函式外使用 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:75` | summarize 函式在日誌為空時仍輸出訊息 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入漏洞：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆插入 SQL 語句，但未對單引號進行跳脫。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或 SQL 注入。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 參數，執行任意 SQL 指令，例如刪除資料表或竄改資料。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `printf` 進行跳脫。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入漏洞：run_hook 使用 eval 執行未受信任的 hook 路徑</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook 腳本。`$hook` 路徑由 `$ROOT` 與固定檔名組成，但 `$ROOT` 來自使用者輸入，若 `$ROOT` 包含惡意內容（例如 `$(malicious)` 或 `; rm -rf /`），將導致任意命令執行。即使 `$ROOT` 看似受控，攻擊者若能控制 repo 根目錄路徑，即可注入命令。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 路徑不含特殊字元。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`，其中 `$hook` 包含 `$ROOT`，而 `$ROOT` 來自使用者輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出被重導至日誌，但未檢查其退出狀態。若 fetch 失敗（例如網路問題）或 checkout 失敗（例如 branch 不存在），腳本仍會繼續執行後續指令，可能導致 `git merge` 在錯誤狀態下執行，或將錯誤的資料寫入資料庫。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止。

**判斷依據**：diff 第 31-33 行：連續執行 git 指令，未檢查退出狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用 rm -rf 可能誤刪檔案</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 為空字串或未設定，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `.cache` 目錄不存在，`rm -rf` 不會報錯，但若 `$ROOT` 包含符號連結或特殊路徑，可能造成非預期刪除。

建議先檢查 `$ROOT` 是否為空，並確認 `.cache` 目錄存在且為預期路徑，或使用更安全的刪除方式。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`，未檢查 `$ROOT` 是否為空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未初始化：ahead 可能為空導致數值比較錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 `sqlite3` 插入空值可能導致資料型別錯誤。

建議在取得 `ahead` 後檢查是否為數字，或設定預設值 0。

**判斷依據**：diff 第 35-37 行：未處理 `ahead` 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迭代，若 repo 目錄名稱包含空白、換行或特殊字元，將被錯誤分割。此外，`ls` 的輸出可能包含非目錄項目，需額外檢查。

建議改用 `find` 或 glob：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  ...
done
```

**判斷依據**：diff 第 72 行：`for d in $(ls "$ROOT")` 未正確處理檔名。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函式外使用</summary>

`main` 函式中使用 `local target="$ROOT/$d"`，但 `local` 僅能在函式內使用。雖然在 bash 中可能不會報錯，但這是不良實踐，可能導致變數作用域混淆。

建議移除 `local` 或將該段程式碼放入函式中。

**判斷依據**：diff 第 82 行：在 `main` 函式內使用 `local`，但 `main` 本身是函式，此處 `local` 是多餘的。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:75</code> summarize 函式在日誌為空時仍輸出訊息</summary>

`summarize` 函式中，若 `$LOG` 檔案不存在或為空，`total` 為 0，但仍會輸出「本次同步共 0 筆紀錄，詳見 $LOG」。這可能造成誤導。

建議在 `total` 為 0 時輸出不同訊息或省略。

**判斷依據**：diff 第 68 行：未處理 `total` 為 0 的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 2272 ｜ PR #13</sub>