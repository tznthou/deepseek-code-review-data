<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及並發與效能問題。最優先應修復的是 SQL 注入與命令注入漏洞，其次是補強錯誤處理與日誌記錄。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑刪除風險：`cleanup_cache` 使用 `rm -rf` 且路徑未驗證 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:12` | 並發問題：多個實例同時執行會互相干擾 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 效能問題：在迴圈中執行 `ls` 並逐一處理，可能導致大量子程序 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆後插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成：
```sql
INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))
```
這會刪除 `runs` 資料表。

**建議**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式，並對輸入進行跳脫。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 repo 目錄名稱，可能包含 shell 特殊字元（例如 `; rm -rf ~`）。攻擊者若能在 repo 根目錄建立惡意名稱的目錄，即可執行任意命令。

**失敗情境**：假設 repo 目錄名稱為 `test; touch /tmp/pwned`，則 `eval` 會執行 `touch /tmp/pwned`。

**建議**：避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 都以引號包覆。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查退出狀態。若 fetch 失敗（例如網路問題），後續的 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。此外，`ahead` 的計算若失敗（例如 rev-list 錯誤），會得到空字串，在 `[ "$ahead" -gt 0 ]` 比較時可能出錯。

**失敗情境**：當 `git fetch` 因網路中斷失敗時，`origin/$BRANCH` 可能不存在，`git merge --ff-only` 會失敗，但腳本仍會繼續執行，並將 `ahead` 設為 0 寫入資料庫，造成誤報。

**建議**：在每個 git 指令後檢查 `$?`，若失敗則記錄錯誤並跳過該 repo，或至少讓 `ahead` 的計算失敗時設為 -1 並記錄。

**判斷依據**：diff 第 30-34 行：git 指令未檢查退出狀態

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑刪除風險：`cleanup_cache` 使用 `rm -rf` 且路徑未驗證</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。此外，若 `$ROOT` 為空字串，則會變成 `rm -rf /.cache/*`，可能刪除系統檔案。

**失敗情境**：若使用者未提供第一個參數，`$ROOT` 為空，則 `rm -rf /.cache/*` 會嘗試刪除根目錄下的 `.cache` 內容。

**建議**：在執行前檢查 `$ROOT` 是否為有效目錄，並使用更安全的刪除方式，例如 `find "$ROOT/.cache" -mindepth 1 -delete`。

**判斷依據**：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:12</code> 並發問題：多個實例同時執行會互相干擾</summary>

腳本使用固定的 `/tmp/repo_sync.db` 與 `/tmp/repo_sync.log`，若同時執行多個實例，會互相覆寫資料庫與日誌，導致資料錯亂。此外，`cleanup_cache` 與 `summarize` 也可能互相影響。

**失敗情境**：兩個實例同時執行時，一個實例的 `summarize` 可能讀取到另一個實例正在寫入的 log，或資料庫寫入衝突。

**建議**：使用唯一的暫存檔名（例如加入 PID 或時間戳），或使用 lock 機制確保同一時間只有一個實例執行。

**判斷依據**：diff 第 12-13 行：固定的暫存檔路徑

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 效能問題：在迴圈中執行 `ls` 並逐一處理，可能導致大量子程序</summary>

`main` 函式使用 `for d in $(ls "$ROOT")` 迭代目錄，這會啟動一個子 shell 並執行 `ls`。若 repo 數量很多，會造成不必要的效能開銷。此外，若目錄名稱包含空白或換行，`ls` 的輸出會被錯誤分割。

**失敗情境**：若 repo 目錄名稱包含空白（例如 `my repo`），則 `for` 迴圈會將其分割成兩個項目，導致後續處理錯誤。

**建議**：使用 `find` 或 glob 來迭代目錄，例如：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  ...
done
```

**判斷依據**：diff 第 78 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2091 ｜ PR #13</sub>