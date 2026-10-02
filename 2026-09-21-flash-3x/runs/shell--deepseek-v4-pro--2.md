<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與效能問題。最該先修的是 SQL 注入與命令注入漏洞，其次是路徑處理與錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`cleanup_cache` 使用 `rm -rf` 搭配未驗證的 `$ROOT` | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git` 指令失敗未檢查，可能導致後續操作基於錯誤狀態 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 效能問題：`for d in $(ls "$ROOT")` 使用 `ls` 解析目錄，且未處理含空白名稱 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | 變數作用域：`local` 使用於函式外，可能導致非預期行為 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以字串拼接方式插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 參數來利用此漏洞。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成 `INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))`，導致資料表被刪除。

**建議修法**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫（如 `sqlite3` 的 `:memory:` 或使用 `printf '%q'`）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經任何處理直接嵌入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 皆來自外部輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元（如 `;`、`$(...)`、反引號），可導致任意命令執行。

**失敗情境**：若 `$ROOT` 為 `/tmp/evil; rm -rf /`，則 `eval` 會執行 `rm -rf /`。

**建議修法**：避免使用 `eval`，改為直接執行：`"$hook" "$repo"`，並確保 `$hook` 與 `$repo` 不包含特殊字元（可先驗證）。

**判斷依據**：diff 第 58 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`cleanup_cache` 使用 `rm -rf` 搭配未驗證的 `$ROOT`</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空白或特殊字元，或使用者誤將 `$ROOT` 設為 `/`，可能導致災難性刪除。此外，`$ROOT` 未經驗證是否為預期目錄。

**失敗情境**：若 `$ROOT` 為 `/`，則會執行 `rm -rf //.cache/*`，可能刪除系統檔案。

**建議修法**：驗證 `$ROOT` 為絕對路徑且非根目錄，並使用更安全的刪除方式（如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`，`$ROOT` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git` 指令失敗未檢查，可能導致後續操作基於錯誤狀態</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查其退出碼。若 fetch 失敗（如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。

**失敗情境**：`git fetch` 因網路中斷失敗，但腳本繼續執行 `git checkout` 與 `git merge`，可能合併到舊的 commit，造成資料不一致。

**建議修法**：在每個 `git` 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止。

**判斷依據**：diff 第 34-36 行：三個 `git` 指令均未檢查退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 效能問題：`for d in $(ls "$ROOT")` 使用 `ls` 解析目錄，且未處理含空白名稱</summary>

`main` 函式使用 `for d in $(ls "$ROOT")` 迭代目錄。`ls` 的輸出會進行分詞，若目錄名稱包含空白或換行，會被錯誤拆分。此外，`ls` 在大型目錄下可能較慢，且其輸出格式可能因環境而異。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致後續路徑錯誤。

**建議修法**：使用 `for d in "$ROOT"/*/; do` 或 `find "$ROOT" -maxdepth 1 -type d` 搭配 `while read` 迴圈，並正確處理空白。

**判斷依據**：diff 第 80 行：`for d in $(ls "$ROOT"); do`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> 變數作用域：`local` 使用於函式外，可能導致非預期行為</summary>

在 `main` 函式中，`local target="$ROOT/$d"` 使用了 `local`，但 `local` 僅能在函式內使用。此處 `main` 是函式，因此合法，但若未來重構將此段移出函式，會導致錯誤。此外，`local` 在 bash 中會遮蔽全域變數，可能造成混淆。

**建議修法**：若確定在函式內，可保留，但建議改用一般變數賦值，或明確註明。

**判斷依據**：diff 第 82 行：`local target="$ROOT/$d"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2517 (cache hit 2432) ｜ completion tokens 2060</sub>