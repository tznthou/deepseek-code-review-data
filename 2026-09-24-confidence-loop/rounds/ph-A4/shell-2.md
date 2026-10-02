<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval hook）、路徑處理不當、錯誤處理不足，以及使用全域變數與 local 誤用等問題。最優先應修復 SQL 注入與 eval 的使用，並改善錯誤處理與變數作用域。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob，可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤結果 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數 ahead 可能未初始化，導致數值比較錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，可能因檔名包含換行或空格而失敗 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | 在函數內使用 local 但未宣告，可能影響全域變數 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自目錄名稱，可能包含單引號等特殊字元，導致 SQL 注入或語法錯誤。攻擊者可建立名為 `x'); DROP TABLE runs;--` 的目錄來破壞資料庫。

建議使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：diff 第 39 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱帶有 `; rm -rf ~`），將導致任意命令執行。即使 hook 路徑看似固定，但 repo 名稱來自目錄名稱，攻擊者可建立惡意目錄名稱。

建議改為直接執行，避免 eval：
```bash
"$hook" "$repo"
```

**判斷依據**：diff 第 48 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob，可能誤刪檔案</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空格或特殊字元，或 `.cache` 目錄不存在，glob 可能展開成意外路徑。此外，若 `$ROOT` 為空或未定義，可能變成 `rm -rf /.cache/*`，造成系統檔案刪除。

建議先檢查目錄是否存在，並使用更安全的寫法：
```bash
if [ -d "$ROOT/.cache" ]; then
  find "$ROOT/.cache" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
fi
```

**判斷依據**：diff 第 53 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤結果</summary>

`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。

建議在每個 git 指令後檢查退出碼，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：diff 第 30-32 行：`git fetch origin --prune 2>>"$LOG"` 等指令未檢查退出碼

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數 ahead 可能未初始化，導致數值比較錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 可能為空字串。後續 `[ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空可能導致語法錯誤。

建議在指令失敗時設定預設值，例如：
```bash
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null) || ahead=0
```

**判斷依據**：diff 第 36 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或特殊字元，將被錯誤分割。此外，`ls` 的輸出可能包含非目錄項目。

建議使用 glob 或 `find`：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

**判斷依據**：diff 第 72 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> 在函數內使用 local 但未宣告，可能影響全域變數</summary>

`main` 函數中 `local target="$ROOT/$d"` 使用了 `local`，但 `main` 本身是在腳本頂層呼叫，`local` 在函數外無效，可能導致錯誤或非預期行為。建議移除 `local` 或將整個邏輯包在函數中。

**判斷依據**：diff 第 73 行：`local target="$ROOT/$d"`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1899 ｜ PR #13</sub>