<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及對輸入目錄的假設。最該先修的是 SQL 查詢的參數化與移除 eval 的使用。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 缺少錯誤處理：git 指令失敗仍繼續執行 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 危險的 rm -rf 使用：可能刪除非預期目錄 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，無法處理特殊檔名 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在函式外使用 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自目錄名稱，攻擊者可以建立包含單引號的目錄（例如 `'; DROP TABLE runs; --`），導致 SQL 注入。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：diff 第 49 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$repo` 來自目錄名稱，攻擊者可以建立包含 shell 指令的目錄（例如 `$(rm -rf /)`），導致任意命令執行。建議改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑安全。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 缺少錯誤處理：git 指令失敗仍繼續執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時（例如網路問題、branch 不存在）只將 stderr 寫入 log，但腳本仍繼續執行後續指令，可能導致錯誤的 ahead 計算或錯誤的 SQL 寫入。建議在每個 git 指令後檢查 exit code，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 31-33 行：連續執行 git 指令但未檢查回傳值

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 危險的 rm -rf 使用：可能刪除非預期目錄</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`。如果 `$ROOT` 未設定或為空，可能變成 `rm -rf /.cache/*`，造成系統檔案刪除。建議檢查 `$ROOT` 是否為空，並使用更安全的刪除方式（例如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，無法處理特殊檔名</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出進行分詞，若目錄名稱包含空白或特殊字元（例如換行），會導致迴圈錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 74 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在函式外使用</summary>

`main` 函式中的 `local target="$ROOT/$d"` 使用了 `local`，但 `local` 只能在函式內使用。雖然 bash 可能容忍，但這不是標準用法，建議移除 `local`。

**判斷依據**：diff 第 84 行：`local target="$ROOT/$d"`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 2432) ｜ completion tokens 1399 ｜ PR #13</sub>