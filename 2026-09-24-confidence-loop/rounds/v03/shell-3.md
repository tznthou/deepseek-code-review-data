<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步 repo 的 bash 腳本，將同步結果寫入 sqlite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足以及潛在的資料遺失。最該先修的是 sync_one 中的 SQL 注入與 run_hook 的 eval 使用，以及 git 指令失敗時仍繼續執行的問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能導致錯誤結果或資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除快取，若 ROOT 未正確設定可能造成大規模刪除 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而誤設為 0 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空格或特殊字元時會出錯 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 來自目錄名稱，`BRANCH` 雖有格式驗證但未做 SQL 跳脫，攻擊者若能在 repo 根目錄建立惡意名稱的目錄（例如 `x'); DROP TABLE runs;--`），即可注入任意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 42 行直接將變數插入 SQL 字串，未使用參數化查詢或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會執行任意字串，若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱帶有 `; rm -rf /`），可能導致任意命令執行。建議改用直接執行並傳參數：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 51 行使用 eval 執行包含變數的字串，未做任何防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能導致錯誤結果或資料不一致</summary>

`git fetch`、`git checkout`、`git merge` 的失敗僅被重導向到 log，腳本仍會繼續執行。例如 fetch 失敗時，`origin/$BRANCH` 可能不存在，導致 merge 失敗，但腳本仍會將 `ahead` 設為 0 並寫入資料庫，造成報表錯誤。建議在每個 git 指令後檢查 exit code，失敗即中止或記錄錯誤。

**判斷依據**：第 29-31 行未檢查 git 指令的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議檢查 rev-list 的 exit code 並處理失敗情況。

**判斷依據**：第 33 行未檢查 rev-list 的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除快取，若 ROOT 未正確設定可能造成大規模刪除</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或未定義，可能變成 `rm -rf /.cache/*` 或 `rm -rf /*`，造成系統檔案刪除。建議檢查 `$ROOT` 是否為空，並使用更安全的刪除方式（例如 find 搭配 -delete 或限制深度）。

**判斷依據**：第 60 行未檢查 ROOT 是否為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而誤設為 0</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 因檔案不存在而失敗，total 會被設為 0，但實際上可能已有 log 內容。建議先檢查檔案是否存在，或使用 `wc -l` 並處理錯誤。

**判斷依據**：第 70 行 grep 失敗時 total 設為 0，可能掩蓋實際 log 行數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空格或特殊字元時會出錯</summary>

`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會被拆成多個項目。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：第 82 行使用 ls 輸出進行迴圈，未處理特殊字元。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2642 (cache hit 2560) ｜ completion tokens 1645 ｜ PR #13</sub>