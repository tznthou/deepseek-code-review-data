<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及迴圈中使用全域變數導致的潛在問題。最優先應修復 SQL 注入與命令注入問題，並改善錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗未中止，可能導致錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄名稱，無法處理包含空白或特殊字元的目錄 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | 在迴圈內使用 local 宣告變數，可能導致非預期行為 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除快取，若 ROOT 未正確設定可能誤刪 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 查詢。若 repo 目錄名稱或 branch 名稱包含單引號，將破壞 SQL 語法或造成注入。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 45 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會執行由 `$ROOT` 與 `$repo` 組成的字串。若 `$ROOT` 或 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），將導致任意命令執行。建議避免使用 eval，改用直接執行並正確引用變數：`"$hook" "$repo"`。

**判斷依據**：第 56 行使用 eval 執行包含變數的字串，且變數來源為使用者輸入的目錄路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗未中止，可能導致錯誤結果</summary>

`git checkout $BRANCH` 與 `git merge --ff-only` 的錯誤僅被重導向至 log，腳本仍會繼續執行。若 checkout 失敗（例如 branch 不存在），後續 merge 可能基於錯誤的 branch，或 `ahead` 計算不正確。建議在每個 git 指令後檢查 exit code，失敗即回報並跳過該 repo。

**判斷依據**：第 31-32 行未檢查 git 指令的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入會失敗。建議檢查 rev-list 的 exit code，失敗時設定 ahead 為 0 或跳過。

**判斷依據**：第 34 行未檢查 rev-list 的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄名稱，無法處理包含空白或特殊字元的目錄</summary>

`for d in $(ls "$ROOT")` 會將 ls 的輸出以空白分割，若 repo 目錄名稱包含空白，會被拆成多個項目。建議改用 glob：`for d in "$ROOT"/*/; do d=$(basename "$d"); ...` 或使用 `find`。

**判斷依據**：第 76 行使用 ls 的輸出進行迴圈，未正確處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> 在迴圈內使用 local 宣告變數，可能導致非預期行為</summary>

`local target="$ROOT/$d"` 在 for 迴圈內使用 local，但 local 僅在函數內有效。此處位於 main 函數中，因此有效，但若未來重構可能造成混淆。建議改為一般賦值。

**判斷依據**：第 77 行在迴圈內使用 local。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除快取，若 ROOT 未正確設定可能誤刪</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或未設定，可能刪除根目錄下的 .cache。建議檢查 `$ROOT` 是否為空，或使用更安全的刪除方式。

**判斷依據**：第 62 行使用 rm -rf，且未檢查 ROOT 是否有效。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1590 ｜ PR #13</sub>