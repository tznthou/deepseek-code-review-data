<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入（repo 名稱與 branch 未經參數化）、`eval` 執行未受信任的 hook 路徑、以及多個錯誤處理與併發問題。最優先應修復 SQL 注入與 `eval` 的使用，並加強錯誤處理與輸入驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經參數化直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 使用 `eval` 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 與 `git merge` 失敗未中止，可能導致錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 可能為空字串，導致 SQL 錯誤或錯誤比較 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 可能誤刪重要檔案 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | `for d in $(ls "$ROOT")` 無法處理含空格或特殊字元的目錄名稱 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `summarize` 中 `total` 計算可能因 log 不存在而錯誤 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經參數化直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號或 SQL 特殊字元，可能導致 SQL 注入，進而破壞資料庫或執行任意 SQL。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 使用 `eval` 執行未受信任的 hook 路徑</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 路徑來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 由使用者提供，若攻擊者能控制 repo 目錄結構，可能注入任意命令。例如，若 `$ROOT` 包含空格或特殊字元，`eval` 可能執行非預期的命令。建議改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑安全。

**判斷依據**：第 50 行使用 eval 執行字串，未對 hook 路徑做安全處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 與 `git merge` 失敗未中止，可能導致錯誤結果</summary>

`sync_one` 中 `git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導至 log，未檢查退出狀態。若 checkout 失敗（例如 branch 不存在），後續 merge 可能基於錯誤的 branch 執行，或 `ahead` 計算錯誤。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 34-35 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 可能為空字串，導致 SQL 錯誤或錯誤比較</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入空字串可能導致型別錯誤。建議在計算後檢查 `ahead` 是否為數字，否則設為 0 或跳過。

**判斷依據**：第 38 行未處理 git 指令失敗時 `ahead` 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 可能誤刪重要檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議先檢查路徑是否為預期的 cache 目錄，或使用更安全的刪除方式。

**判斷依據**：第 60 行直接使用 rm -rf 刪除目錄內容，未做路徑驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> `for d in $(ls "$ROOT")` 無法處理含空格或特殊字元的目錄名稱</summary>

使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或特殊字元，會被錯誤分割。建議改用 `find` 或 glob 搭配 null 分隔符。

**判斷依據**：第 72 行使用命令替換與 ls，未考慮特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `summarize` 中 `total` 計算可能因 log 不存在而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 失敗（例如 log 不存在），`total` 會被設為 0，但後續 `if [ "$total" -gt 100 ]` 仍會執行，可能因 `total` 非數字而報錯。建議先檢查 log 是否存在。

**判斷依據**：第 66 行未處理 grep 失敗時 total 可能非數字的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 0) ｜ completion tokens 1701 ｜ PR #13</sub>