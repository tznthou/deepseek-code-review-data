<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及併發與資源清理問題。最該先修的是 SQL 注入與 hook 的 eval 使用，其次是補上錯誤處理與改用更安全的迴圈方式。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗時未中止，可能導致錯誤的 ahead 計算 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 可能為空字串，導致 SQL 語法錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 搭配未驗證的 ROOT，可能誤刪重要檔案 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 輸出進行迴圈，檔名含空白或換行會出錯 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函式外使用，可能導致非預期行為 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 將 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串。雖然 branch 有格式驗證，但 repo 名稱（來自目錄名稱）完全未驗證。攻擊者若建立名為 `x'); DROP TABLE runs;--` 的目錄，即可注入任意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 46 行直接將變數插入 SQL 字串，且 `$name` 來自 `basename "$dir"`，未做任何驗證或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 程式碼執行。`$hook` 是固定路徑，但 `$repo` 來自目錄名稱，攻擊者可建立名為 `; rm -rf ~` 的目錄，導致任意命令執行。建議改用直接執行：`"$hook" "$repo"`，避免 eval。

**判斷依據**：第 55 行使用 eval，且 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗時未中止，可能導致錯誤的 ahead 計算</summary>

`git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"` 的錯誤僅被重導向到 log，腳本仍會繼續執行。若 checkout 失敗（例如 branch 不存在），後續 merge 與 rev-list 可能基於錯誤的 HEAD，導致 ahead 數值不正確或 SQL 寫入錯誤資料。建議在每個 git 指令後檢查 exit code，失敗即 return 或 exit。

**判斷依據**：第 34-35 行未檢查指令執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空字串，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議在 rev-list 失敗時設定 ahead=0 或中止。

**判斷依據**：第 42 行未處理 rev-list 失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 搭配未驗證的 ROOT，可能誤刪重要檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未設定或為空，可能變成 `rm -rf /.cache/*` 或 `rm -rf .cache/*`，造成意外刪除。建議檢查 `$ROOT` 是否為空，並確認 `.cache` 目錄存在且位於預期路徑。

**判斷依據**：第 61 行直接使用 rm -rf，且 ROOT 來自使用者輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 輸出進行迴圈，檔名含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 會將 ls 的輸出以空白分割，若目錄名稱包含空白或換行，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：第 70 行使用 ls 輸出進行 word splitting。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函式外使用，可能導致非預期行為</summary>

`local target="$ROOT/$d"` 出現在 main 函式中，但 local 只能在函式內使用。若腳本以 bash 執行，此處會報錯或將變數設為全域。建議移除 local 或改用其他變數名稱。

**判斷依據**：第 73 行在 main 函式內使用 local，但 main 本身是函式，此處應為合法，但需確認 bash 版本。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1684 ｜ PR #13</sub>