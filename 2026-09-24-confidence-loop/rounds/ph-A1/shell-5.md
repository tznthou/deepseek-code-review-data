<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險集中在 shell 注入（SQLite 與 eval）、錯誤處理不足（git 指令失敗仍繼續執行）、以及路徑處理不嚴謹（ls 解析、rm -rf 使用）。最優先應修補 SQL 注入與 eval 的使用，並加入 git 指令的錯誤檢查。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQLite 查詢存在 SQL 注入風險 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | eval 執行未受信任的 hook 路徑，可能導致任意程式碼執行 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未被偵測，可能導致錯誤結果或資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 搭配變數路徑，可能誤刪重要資料 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 寫入 NULL 或錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQLite 查詢存在 SQL 注入風險</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串拼接方式插入 SQL 語句。攻擊者若控制 repo 目錄名稱（例如建立名為 `x'); DROP TABLE runs;--` 的目錄），即可執行任意 SQL 指令，導致資料毀損或洩漏。

**失敗情境**：假設 `$ROOT` 下存在一個名為 `evil'); DROP TABLE runs;--` 的目錄，且內含 `.git` 子目錄，則 `sync_one` 會執行：
```sql
INSERT INTO runs VALUES('evil'); DROP TABLE runs;--', 'main', 0, datetime('now'))
```
這會刪除 `runs` 資料表。

**建議修法**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行跳脫（escape single quotes）。

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經處理直接嵌入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> eval 執行未受信任的 hook 路徑，可能導致任意程式碼執行</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 是由 `$ROOT/.hooks/post-sync` 組成，而 `$ROOT` 是使用者提供的參數。若攻擊者能控制 `$ROOT`（例如提供包含惡意內容的路徑），或 `$ROOT` 下的 `.hooks/post-sync` 檔案被竄改，則可注入任意 shell 指令。

**失敗情境**：假設 `$ROOT` 為 `/tmp/evil`，且 `/tmp/evil/.hooks/post-sync` 內容為 `echo pwned; rm -rf /`，則執行 `eval` 時會執行 `echo pwned; rm -rf /`，造成系統破壞。

**建議修法**：直接執行 hook 檔案，不要使用 eval：
```bash
"$hook" "$repo"
```
若需要傳遞多個參數，可使用陣列。

**判斷依據**：diff 第 53 行：`eval "$hook $repo"`，其中 `$hook` 包含使用者可控的 `$ROOT`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未被偵測，可能導致錯誤結果或資料不一致</summary>

`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出僅被重導向至 log 檔，但未檢查其 exit code。若其中任何一步失敗（例如網路問題、branch 不存在、merge 衝突），腳本仍會繼續執行，並將不正確的 `ahead` 值寫入資料庫。

**失敗情境**：假設 `git fetch` 因網路中斷而失敗，但 `git checkout` 與 `git merge` 仍會執行（可能基於舊的遠端狀態），導致 `ahead` 計算錯誤，且使用者不會收到任何錯誤通知。

**建議修法**：在每個 git 指令後檢查 exit code，例如：
```bash
git fetch origin --prune 2>>"$LOG" || { echo "fetch failed for $name" >> "$LOG"; return 1; }
```
並在 `sync_one` 回傳非零時於 `main` 中記錄錯誤。

**判斷依據**：diff 第 36-39 行：三個 git 指令均未檢查 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 搭配變數路徑，可能誤刪重要資料</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含特殊字元（例如空白或 glob 字元），可能導致刪除非預期的檔案。此外，若 `$ROOT` 為空字串，則會變成 `rm -rf /.cache/*`，可能刪除系統檔案。

**失敗情境**：假設使用者未提供 `$ROOT`（或提供空字串），則 `$ROOT` 為空，`rm -rf /.cache/*` 會嘗試刪除根目錄下的 `.cache` 內容，可能造成系統損壞。

**建議修法**：在使用前驗證 `$ROOT` 非空且為絕對路徑，並考慮使用更安全的刪除方式，例如 `find "$ROOT/.cache" -mindepth 1 -delete`。

**判斷依據**：diff 第 61 行：`rm -rf "$ROOT"/.cache/*`，其中 `$ROOT` 未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱</summary>

`main` 函式中使用 `for d in $(ls "$ROOT")` 來迭代目錄。這種方式會將 `ls` 的輸出以空白、換行等進行 word splitting，導致包含空白的目錄名稱被拆成多個部分，且可能受到 glob 擴展影響。

**失敗情境**：假設 `$ROOT` 下有一個名為 `my repo` 的目錄，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致後續路徑錯誤。

**建議修法**：使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 迴圈：
```bash
while IFS= read -r -d '' d; do
  ...
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
```

**判斷依據**：diff 第 76 行：`for d in $(ls "$ROOT"); do`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 寫入 NULL 或錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因 `[` 無法比較空字串而報錯，且 SQL 插入時 `$ahead` 為空會導致語法錯誤或寫入 NULL。

**失敗情境**：假設 `origin/$BRANCH` 不存在，`git rev-list` 回傳非零並輸出錯誤（被丟棄），`ahead` 為空。接著 `[ "$ahead" -gt 0 ]` 會輸出錯誤訊息，且 SQL 插入可能失敗。

**建議修法**：在取得 `ahead` 後檢查是否為數字，若不是則設為 0 或記錄錯誤並跳過。

**判斷依據**：diff 第 44 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`，未檢查命令是否成功。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2377 ｜ PR #13</sub>