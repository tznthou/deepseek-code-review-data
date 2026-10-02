<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及對 repo 目錄的假設過於樂觀。最優先應修復 SQL 注入與命令注入問題，並強化錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 為空或錯誤可能造成災難性刪除 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 與 `git merge` 失敗時未中止，可能導致後續操作在錯誤狀態下執行 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 變數可能為空，導致 `[ "$ahead" -gt 0 ]` 比較失敗 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | `for d in $(ls "$ROOT")` 對包含空格或特殊字元的目錄名稱處理不當 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法，甚至可能執行任意 SQL。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行 `INSERT INTO runs VALUES('x'); DROP TABLE runs;--', ...)`，導致資料表被刪除。

建議使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 45 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 是 `$ROOT/.hooks/post-sync`，而 `$ROOT` 來自使用者輸入；`$repo` 是 repo 目錄名稱。如果 `$ROOT` 或 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），可能導致任意命令執行。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 的值安全。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 為空或錯誤可能造成災難性刪除</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。如果 `$ROOT` 未設定或為空字串，路徑會變成 `/.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 指向錯誤目錄，也可能誤刪重要資料。

建議在使用前檢查 `$ROOT` 是否為空，並確認 `.cache` 目錄存在且為預期路徑。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`，未對 `$ROOT` 進行空值或有效性檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 與 `git merge` 失敗時未中止，可能導致後續操作在錯誤狀態下執行</summary>

`sync_one` 中執行 `git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"`，但未檢查其退出狀態。如果 checkout 失敗（例如 branch 不存在），後續的 merge 與 rev-list 可能基於錯誤的 HEAD 執行，導致資料不正確。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並返回非零狀態。

**判斷依據**：diff 第 31-32 行：`git checkout` 與 `git merge` 未檢查退出狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 變數可能為空，導致 `[ "$ahead" -gt 0 ]` 比較失敗</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `[ "$ahead" -gt 0 ]` 會因為空字串不是整數而報錯，且 `sqlite3` 插入時 `$ahead` 為空可能導致 SQL 錯誤。

建議在取得 `ahead` 後檢查是否為數字，若不是則設為 0 或中止。

**判斷依據**：diff 第 35 行：`ahead` 可能為空，未做防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> `for d in $(ls "$ROOT")` 對包含空格或特殊字元的目錄名稱處理不當</summary>

使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或 glob 字元，會導致路徑解析錯誤。建議改用 `find` 或 glob 搭配 null 分隔符。

**判斷依據**：diff 第 72 行：`for d in $(ls "$ROOT")` 未處理特殊字元。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1739 ｜ PR #13</sub>