<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite，並包含 hook 執行與日誌摘要功能。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及變數作用域問題。最嚴重的是 sync_one 中直接將 repo 名稱與 branch 插入 SQL 語句，且 run_hook 使用 eval 執行未受信任的 hook 路徑，可能導致任意程式碼執行。建議先修正這些安全性問題，再考慮合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 可能刪除任意目錄 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數作用域錯誤：ahead 可能未初始化 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，可能受特殊檔名影響 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

在 `sync_one` 中，`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 和 `$BRANCH` 嵌入 SQL 字串。雖然 `$BRANCH` 已用正規表達式限制字元集，但 `$name` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"` 的輸出，攻擊者若能在 repo 根目錄建立名稱包含單引號的目錄（例如 `'; DROP TABLE runs; --`），即可注入任意 SQL 語句，造成資料毀損或洩漏。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 和 `$BRANCH` 進行單引號跳脫。

**判斷依據**：diff 第 42 行新增的 SQL 插入語句，直接使用變數拼接。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑</summary>

`run_hook` 中的 `eval "$hook $repo"` 會將 `$hook` 和 `$repo` 的內容當作 shell 程式碼執行。`$hook` 是 `$ROOT/.hooks/post-sync`，而 `$ROOT` 來自使用者輸入，攻擊者若能控制 repo 根目錄下的 `.hooks/post-sync` 檔案內容（例如在 repo 中放置惡意腳本），即可在執行此腳本時取得任意程式碼執行權限。即使檔案權限為可執行，也不應使用 `eval`。建議改為直接執行：`"$hook" "$repo"`，並確保 hook 路徑不受使用者控制。

**判斷依據**：diff 第 50 行新增的 eval 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 可能刪除任意目錄</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 為空字串或未定義，則會變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 包含符號連結或特殊路徑，也可能造成非預期的刪除。建議在使用前檢查 `$ROOT` 是否為有效目錄，並避免使用 `rm -rf` 搭配變數展開，可改用 `find "$ROOT/.cache" -mindepth 1 -delete` 並加上防護條件。

**判斷依據**：diff 第 55 行新增的 rm -rf 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 都只將 stderr 重導向至日誌，未檢查退出碼。若 fetch 失敗（例如網路問題），後續的 checkout 和 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo，或至少讓腳本以非零狀態退出。

**判斷依據**：diff 第 33-35 行新增的 git 指令，未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數作用域錯誤：ahead 可能未初始化</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git 指令失敗（例如分支不存在），`ahead` 會是空字串。後續的 `if [ "$ahead" -gt 0 ]` 在空字串時會導致 `[: : integer expression expected` 錯誤，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。建議在取得 ahead 後檢查是否為數字，或設定預設值 0。

**判斷依據**：diff 第 38 行新增的指令，未處理失敗情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，可能受特殊檔名影響</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格或換行符號，會導致迴圈變數 `d` 被錯誤分割。建議改用 `for d in "$ROOT"/*/; do` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

**判斷依據**：diff 第 68 行新增的迴圈。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1757 ｜ PR #13</sub>