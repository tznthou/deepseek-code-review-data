<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite，並提供每日維運報表。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復 SQL 注入與命令注入漏洞，並改善錯誤處理與路徑驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：`cleanup_cache` 使用未驗證的 `$ROOT` 進行 `rm -rf` | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：`git fetch`、`checkout`、`merge` 失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 未處理 `ahead` 為空或非數字的情況 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `\|\| total=0` 處理 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能因檔名包含換行或空格而失敗 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆後插入 SQL 語句，但未對單引號進行跳脫。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 指令，導致資料庫內容被竄改或刪除。例如：建立一個名為 `x' ; DROP TABLE runs; --` 的 repo 目錄，執行腳本後 `runs` 表將被刪除。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook，其中 `$hook` 與 `$repo` 皆來自外部輸入（`$ROOT` 與 repo 目錄名稱）。攻擊者可建立惡意 repo 目錄名稱（例如 `$(malicious_command)`）或控制 `$ROOT` 路徑，導致任意命令執行。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 路徑安全。

**判斷依據**：第 50 行使用 eval 執行包含外部輸入的字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：`cleanup_cache` 使用未驗證的 `$ROOT` 進行 `rm -rf`</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未正確設定或包含符號連結，可能導致刪除任意檔案。例如：若 `$ROOT` 為 `/`，則會嘗試刪除 `/.cache/*`，可能影響系統。

建議在使用前驗證 `$ROOT` 為絕對路徑且存在，並避免使用 `rm -rf` 搭配未受信任的路徑。

**判斷依據**：第 55 行直接使用 `$ROOT` 進行刪除，未做任何檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：`git fetch`、`checkout`、`merge` 失敗仍繼續執行</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查其退出狀態。若 fetch 失敗（例如網路問題）或 checkout 失敗（例如 branch 不存在），腳本仍會繼續執行，可能導致後續操作基於錯誤狀態，並將失敗結果寫入資料庫。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 31-33 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 未處理 `ahead` 為空或非數字的情況</summary>

`ahead=$(git rev-list --count ...)` 若 git 指令失敗，`ahead` 可能為空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致 SQL 錯誤。

建議在取得 `ahead` 後檢查是否為數字，否則設定為 0 或跳過。

**判斷依據**：第 36 行未驗證 `ahead` 的值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `|| total=0` 處理</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `$LOG` 不存在時，`grep` 回傳非零，`total` 會被設為 0，但 `grep` 的錯誤輸出已被重導向，因此不會顯示錯誤。此處理方式可接受，但建議明確檢查檔案是否存在。

**判斷依據**：第 61 行使用 `||` 處理錯誤，但未檢查檔案存在性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格或換行，將被錯誤分割。建議改用 `find` 或 glob：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

**判斷依據**：第 68 行使用 `ls` 輸出進行迴圈。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1870 ｜ PR #13</sub>