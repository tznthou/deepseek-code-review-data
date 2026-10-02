<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及對目錄名稱的假設可能導致腳本失敗或資料損毀。最優先應修正 SQL 注入與命令注入問題，並加強錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval "$hook $repo"` 未安全處理參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 插入空值或錯誤型別 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 設定錯誤可能造成災難性刪除 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 函式在 log 檔案不存在時可能出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能因特殊檔名而失敗 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或注入攻擊。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 名稱來執行任意 SQL 指令，可能竄改或刪除資料庫內容。

**失敗情境**：
1. 建立名為 `x'; DROP TABLE runs;--` 的 repo 目錄，執行腳本後 `runs` 表將被刪除。
2. 傳入 branch 名稱 `main'; DELETE FROM runs;--`，同樣可造成資料遺失。

**建議修法**：
- 使用 `sqlite3` 的參數化查詢功能，例如：
  ```bash
  sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
  ```
- 或使用 `sqlite3` 的 `.parameter` 指令，或先以 `sqlite3` 的 `quote()` 函數處理輸入。

**判斷依據**：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 直接拼接進 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval "$hook $repo"` 未安全處理參數</summary>

`run_hook` 函式使用 `eval` 執行 hook 腳本，並將 repo 名稱作為參數傳入。若 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），將導致任意命令執行。攻擊者可建立惡意名稱的 repo 目錄，當腳本執行到該 repo 時觸發命令注入。

**失敗情境**：
1. 建立名為 `test; touch /tmp/pwned` 的 repo 目錄，執行腳本後 `/tmp/pwned` 檔案將被建立。
2. 更嚴重者，可注入 `rm -rf` 等破壞性指令。

**建議修法**：
- 避免使用 `eval`，改為直接執行：
  ```bash
  "$hook" "$repo"
  ```
- 若需傳遞多個參數，使用陣列或 `"$@"` 方式。

**判斷依據**：diff 第 54 行：`eval "$hook $repo"`，其中 `$repo` 未經跳脫直接放入 eval 字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致資料不一致</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的 stderr 被重導至 log 檔，但未檢查其 exit code。若 fetch 失敗（例如網路問題、認證失敗），後續 checkout 與 merge 可能基於過時的遠端狀態執行，導致錯誤的同步結果。此外，`git merge --ff-only` 若因衝突或非 fast-forward 而失敗，腳本仍會繼續計算 ahead 並寫入資料庫，造成報表數據不準確。

**失敗情境**：
1. 網路中斷導致 `git fetch` 失敗，但腳本仍執行 `git checkout` 與 `git merge`，可能將本地分支重置到舊的 origin 狀態。
2. `git merge --ff-only` 因衝突失敗，但腳本仍記錄 ahead 為 0 或錯誤值，誤導維運人員。

**建議修法**：
- 在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo 或中止腳本。
- 使用 `set -e` 或明確的 `if ! git ...; then ...; fi` 處理。

**判斷依據**：diff 第 31-34 行：連續執行 git 指令，未檢查 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 插入空值或錯誤型別</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若執行失敗（例如 origin/$BRANCH 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空，可能導致型別不符或插入 NULL。

**失敗情境**：
1. 若 `origin/$BRANCH` 不存在（例如遠端尚未建立該分支），`git rev-list` 失敗，`ahead` 為空，腳本可能中斷或寫入錯誤資料。

**建議修法**：
- 檢查 `git rev-list` 的 exit code，失敗時設定 `ahead=0` 或記錄錯誤。
- 使用 `ahead=$(git rev-list --count ... 2>/dev/null || echo 0)` 提供預設值。

**判斷依據**：diff 第 38 行：未處理 `git rev-list` 失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 設定錯誤可能造成災難性刪除</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 因使用者輸入錯誤而指向敏感目錄（例如 `/` 或使用者家目錄），且該目錄下存在 `.cache` 子目錄，將刪除其所有內容。雖然腳本開頭未驗證 `$ROOT` 是否存在或為預期路徑，但此風險存在。

**失敗情境**：
1. 使用者誤將 `$ROOT` 設為 `/`，且系統存在 `/.cache` 目錄，執行腳本將刪除 `/.cache` 下所有檔案。

**建議修法**：
- 驗證 `$ROOT` 是否為預期的 repos 根目錄，例如檢查是否存在特定標記檔案。
- 使用更精確的刪除方式，或限制刪除範圍。

**判斷依據**：diff 第 62 行：`rm -rf` 搭配變數路徑，未驗證路徑安全性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 函式在 log 檔案不存在時可能出錯</summary>

`summarize` 函式中，`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 試圖處理 log 檔案不存在的情況，但 `grep -c .` 在檔案不存在時會回傳非零 exit code，此時 `total` 會被設為 0。然而，後續 `if [ "$total" -gt 100 ]` 使用 `-gt` 比較，若 `total` 為空字串（例如 grep 因其他原因失敗），可能導致錯誤。此外，`tail -100 "$LOG" > "$LOG.trimmed"` 在 log 檔案不存在時也會失敗。

**失敗情境**：
1. 若 `$LOG` 檔案因權限問題無法讀取，`grep` 失敗且 `total` 為空，`[ "$total" -gt 100 ]` 會報錯。

**建議修法**：
- 使用 `total=$(wc -l < "$LOG" 2>/dev/null || echo 0)` 並確保 `total` 為數字。
- 在操作 log 檔案前檢查其存在性。

**判斷依據**：diff 第 71 行：`grep -c .` 的錯誤處理可能不完整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能因特殊檔名而失敗</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或其他特殊字元，將導致迴圈變數 `$d` 被錯誤分割。此外，`ls` 的輸出可能包含非目錄項目，需額外檢查。

**失敗情境**：
1. 若 repos 根目錄下有名稱包含空格的目錄（例如 `my repo`），`for` 迴圈會將其視為兩個項目，導致後續路徑錯誤。

**建議修法**：
- 使用 `find "$ROOT" -maxdepth 1 -type d` 或 glob 搭配 null 分隔符處理。
- 或使用 `for d in "$ROOT"/*/; do ...` 並去除尾隨斜線。

**判斷依據**：diff 第 82 行：`ls` 輸出未安全處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2822 ｜ PR #13</sub>