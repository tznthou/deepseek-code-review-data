<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步 repo 的 bash 腳本，將同步結果寫入 sqlite 並支援 hook 與快取清理。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及併發執行時可能互相干擾。最優先應修復 SQL 注入與 hook 的 eval 使用，並加強錯誤檢查與日誌記錄。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗且未處理 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，路徑含空白或換行時會出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:12` | DB 與 LOG 路徑固定於 /tmp，可能被其他使用者竄改 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 與 `BRANCH` 直接以單引號包覆後插入 SQL 字串，若 repo 目錄名稱或 branch 包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議改用 sqlite3 的參數化查詢（如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`），或至少對輸入進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 43 行，直接將變數插入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行 hook 路徑與 repo 名稱</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 命令執行。若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），將造成任意命令執行。即使 hook 路徑固定，repo 名稱仍可能被惡意利用。建議避免使用 eval，改為直接執行：`"$hook" "$repo"`，並確保 hook 路徑與 repo 名稱不包含特殊字元。

**判斷依據**：diff 第 55 行，使用 eval 執行未受信任的 repo 名稱。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob 可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 包含空白或特殊字元，可能導致路徑解析錯誤。此外，若 `.cache` 目錄不存在，glob 展開失敗時可能刪除非預期檔案。建議先檢查目錄是否存在，並使用 `find` 或 `rm -rf "$ROOT/.cache"` 後重建目錄。

**判斷依據**：diff 第 61 行，未處理路徑中的特殊字元與 glob 展開失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行</summary>

`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查退出碼。若 fetch 失敗（如網路問題）或 checkout 失敗（如 branch 不存在），腳本仍會繼續執行，可能導致後續操作基於錯誤狀態。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：diff 第 32-34 行，未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗且未處理</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（如 branch 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而終止腳本。建議檢查 `ahead` 是否為數字，失敗時設為 0 或跳過。

**判斷依據**：diff 第 36 行，未處理 rev-list 失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，路徑含空白或換行時會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 ls 的輸出以空白分隔，若 repo 目錄名稱包含空白或換行，將被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：diff 第 72 行，使用 ls 輸出進行迴圈，未處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:12</code> DB 與 LOG 路徑固定於 /tmp，可能被其他使用者竄改</summary>

`DB=/tmp/repo_sync.db` 與 `LOG=/tmp/repo_sync.log` 使用固定路徑，若系統為多使用者環境，其他使用者可能預先建立惡意檔案或符號連結，導致資料外洩或任意檔案寫入。建議使用 `mktemp` 或將檔案置於僅當前使用者可寫的目錄。

**判斷依據**：diff 第 15-16 行，固定路徑未考慮安全性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 1727 ｜ PR #13</sub>