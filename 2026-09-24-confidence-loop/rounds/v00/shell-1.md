<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個批次同步多個 Git repository 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及使用 `eval` 執行 hook 的危險做法。最優先應修復 SQL 注入與 `eval` 的使用，並加強錯誤處理與輸入驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 使用 eval 執行 hook 可能導致命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表可能導致路徑處理錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗時未中止，可能導致資料不一致 | 0.70 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 插入失敗或錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 函式在 log 不存在時可能出錯 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如，若 repo 名稱為 `x'; DROP TABLE runs;--`，則會執行惡意 SQL。

建議使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 使用 eval 執行 hook 可能導致命令注入</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行外部 hook。若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱包含 `; rm -rf /`），將導致任意命令執行。此外，`$hook` 路徑由 `$ROOT` 決定，若 `$ROOT` 受攻擊者控制，風險更高。

建議直接執行 `"$hook" "$repo"`，避免使用 `eval`，並確保 hook 路徑與參數安全。

**判斷依據**：diff 第 51 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。例如，若 `$ROOT` 為 `/`，則會嘗試刪除 `/.cache/*`，可能影響系統。

建議檢查 `$ROOT` 是否為有效目錄，並避免使用 `rm -rf` 搭配變數路徑，或改用更安全的刪除方式。

**判斷依據**：diff 第 56 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表可能導致路徑處理錯誤</summary>

`main` 函式使用 `for d in $(ls "$ROOT")` 迭代目錄。若目錄名稱包含空格或特殊字元，將被錯誤分割。此外，`ls` 的輸出可能包含換行符號，導致迭代錯誤。

建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來安全處理。

**判斷依據**：diff 第 70 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗時未中止，可能導致資料不一致</summary>

`sync_one` 函式中，`git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"` 的錯誤僅被重導向至 log，未檢查退出碼。若 checkout 或 merge 失敗（例如 branch 不存在、衝突），後續仍會執行 `git rev-list` 與 SQL 插入，可能記錄錯誤的 ahead 值。

建議在每個 git 指令後檢查退出碼，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 32-33 行：`git checkout $BRANCH 2>>"$LOG"` 與 `git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 插入失敗或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。

建議檢查 `git rev-list` 的退出碼，並在失敗時設定 `ahead=0` 或中止。

**判斷依據**：diff 第 36 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 函式在 log 不存在時可能出錯</summary>

`summarize` 函式使用 `grep -c . "$LOG" 2>/dev/null` 計算行數，若 `$LOG` 不存在，`grep` 會回傳非零退出碼，但 `total` 會被設為 0（因為 `|| total=0`）。然而，後續 `tail -100 "$LOG"` 若檔案不存在會失敗，且 `mv` 也可能失敗。

建議在操作前檢查 `$LOG` 是否存在，或使用 `touch "$LOG"` 確保檔案存在。

**判斷依據**：diff 第 62 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 1408) ｜ completion tokens 1926 ｜ PR #13</sub>