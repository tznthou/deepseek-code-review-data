<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，將同步結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及併發執行時可能造成資料庫鎖定或快取誤刪。最應優先修補的是 SQL 注入與 eval 的使用，其次是路徑驗證與錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：使用 eval 執行 hook 且未驗證 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 可能刪除任意目錄內容 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 寫入空值 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，可能受特殊檔名影響 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:47` | SQLite 資料庫可能因併發寫入而鎖定 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 指令。雖然 branch 有格式驗證，但 repo 名稱（來自檔案系統）完全未驗證。攻擊者可建立名為 `x'); DROP TABLE runs;--` 的目錄，導致資料表被刪除或資料被竄改。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：diff 第 45 行新增的 SQL 插入語句，直接使用變數拼接。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：使用 eval 執行 hook 且未驗證 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook，其中 `$repo` 來自 `$d`（目錄名稱），未經驗證。若目錄名稱包含 shell 特殊字元（如 `; rm -rf ~`），可注入任意命令。即使 hook 檔案本身可信，攻擊者仍可透過建立惡意目錄名稱來執行任意程式碼。

建議改為直接執行並傳遞參數，避免 eval：
```bash
"$hook" "$repo"
```

**判斷依據**：diff 第 54 行使用 eval 執行字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 可能刪除任意目錄內容</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。例如 `$ROOT` 為 `/` 時，將刪除 `/.cache/*`，可能影響系統。此外，若 `.cache` 為符號連結指向其他目錄，也會造成誤刪。

建議檢查 `$ROOT` 是否為有效目錄，並避免使用 `rm -rf` 搭配萬用字元，或改用更安全的清理方式。

**判斷依據**：diff 第 60 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`sync_one` 中所有 git 指令的 stderr 僅重導向至 log，未檢查退出碼。若 `git fetch` 或 `git checkout` 失敗（例如網路問題、branch 不存在），腳本仍會繼續執行後續指令，可能導致錯誤的 ahead 計算或資料庫寫入不正確的資料。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 35-37 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 寫入空值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 將為空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空，可能導致資料型別錯誤。

建議在計算後檢查 `ahead` 是否為整數，失敗時設定為 0 或跳過。

**判斷依據**：diff 第 39 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，可能受特殊檔名影響</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白、換行或 glob 字元，將導致錯誤分割。此外，若 `$ROOT` 不存在，`ls` 會輸出錯誤至 stderr，但迴圈仍可能執行。

建議改用 `for d in "$ROOT"/*/; do` 或 `find` 搭配 `-print0`。

**判斷依據**：diff 第 73 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:47</code> SQLite 資料庫可能因併發寫入而鎖定</summary>

若多個 repo 同步同時執行（例如平行處理），多個 `sqlite3` 程序同時寫入同一個資料庫可能導致 `database is locked` 錯誤。目前腳本為循序執行，但未來若改為平行處理需注意。

建議使用單一連線或加入重試機制。

**判斷依據**：diff 第 45 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1794 ｜ PR #13</sub>