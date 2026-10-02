<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及對 repo 目錄的假設過於樂觀。最優先應修復 SQL 注入與 hook 的 eval 使用，並加入錯誤檢查與交易機制。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行 hook 時未安全處理 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 且路徑未驗證，可能誤刪重要資料 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗時未中止，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空白或換行會出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:47` | SQL 寫入未使用交易，多個 repo 同步時可能部分寫入 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 來自目錄名稱，`BRANCH` 雖有格式驗證但未做 SQL 跳脫，攻擊者若能在 repo 根目錄建立惡意名稱的目錄（例如 `x'); DROP TABLE runs;--`），即可注入任意 SQL。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 47 行直接將變數嵌入 SQL 字串，未使用參數綁定。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行 hook 時未安全處理 repo 名稱</summary>

`eval "$hook $repo"` 會將 `$repo` 的內容當作 shell 程式碼執行。若 repo 名稱包含特殊字元（例如 `$(rm -rf ~)`），可能造成任意命令執行。建議改用直接執行並傳參數：`"$hook" "$repo"`，或使用陣列。

**判斷依據**：第 58 行使用 eval 拼接字串，未對 repo 名稱做任何跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 且路徑未驗證，可能誤刪重要資料</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用萬用字元，或改用更安全的刪除方式（例如 find 搭配 -delete）。

**判斷依據**：第 63 行直接使用 rm -rf 搭配萬用字元，未做任何防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗時未中止，可能導致資料不一致</summary>

`git checkout $BRANCH` 或 `git merge --ff-only` 失敗時，腳本仍會繼續執行後續的 rev-list 與 SQL 寫入，可能記錄錯誤的 ahead 值。建議在每個 git 指令後檢查 exit code，失敗即 return 非零值並記錄錯誤。

**判斷依據**：第 31-32 行未檢查指令執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若指令失敗（例如 branch 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入會失敗。建議檢查 ahead 是否為數字，失敗時設為 0 或中止。

**判斷依據**：第 34 行未處理 rev-list 失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 會將 ls 的輸出按空白分割，若 repo 目錄名稱包含空白或換行，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 while read。

**判斷依據**：第 72 行使用命令替換與 ls，未處理特殊檔名。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:47</code> SQL 寫入未使用交易，多個 repo 同步時可能部分寫入</summary>

每個 repo 的 INSERT 都是獨立交易，若中途失敗，資料庫會留下不完整的執行紀錄。建議在 main 中包一層 BEGIN/COMMIT，或至少記錄失敗的 repo。

**判斷依據**：第 47 行未使用交易。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1535 ｜ PR #13</sub>