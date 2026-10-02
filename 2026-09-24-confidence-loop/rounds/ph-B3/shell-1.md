<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及使用 eval 執行 hook 的危險做法。最優先應修復 SQL 注入與 eval 問題，並加強錯誤處理與輸入驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：使用 eval 執行 hook 腳本 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 插入空值 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能不準確 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空格或換行會出錯 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行單引號跳脫。

**判斷依據**：diff 第 42 行，直接將變數插入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：使用 eval 執行 hook 腳本</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱為 `; rm -rf /`），將導致任意命令執行。即使 hook 路徑看似固定，但 repo 名稱來自目錄名稱，可能受攻擊者控制。建議改用直接執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：diff 第 53 行，使用 eval 執行字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 31-33 行，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 插入空值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如分支不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致 SQL 錯誤。建議檢查 `ahead` 是否為數字，失敗時設定為 0 或中止。

**判斷依據**：diff 第 36 行，未處理指令失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查 `.cache` 是否為目錄，並避免使用 `*` 萬用字元，或使用更安全的刪除方式。

**判斷依據**：diff 第 60 行，使用 rm -rf 與萬用字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能不準確</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 log 檔案不存在，grep 回傳非零，`total` 會被設為 0，但若 log 存在但為空，grep 回傳 1，`total` 也會被設為 0，導致無法區分。建議使用 `wc -l` 或檢查檔案存在性。

**判斷依據**：diff 第 70 行，邏輯可能混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空格或換行會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 ls 的輸出，若目錄名稱包含空格或換行，迴圈會錯誤分割。建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 80 行，使用 ls 輸出。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1662 ｜ PR #13</sub>