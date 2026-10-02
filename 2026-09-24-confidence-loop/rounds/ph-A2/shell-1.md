<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、錯誤處理不足，以及變數未加引號導致的路徑問題。最優先應修復 SQL 注入與 eval 的使用，並加強錯誤處理。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 未加引號，branch 名稱可能被 shell 展開 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:38` | git merge 未檢查失敗，可能導致後續操作在錯誤狀態下執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致變數為空或非數字 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用未加引號的 glob，可能誤刪檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而誤設為 0 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空白或換行會出錯 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`name` 來自 `basename "$dir"`，`BRANCH` 雖有格式驗證，但兩者都直接以單引號字串拼接進 SQL 語句。若 repo 目錄名稱包含單引號（例如 `my'repo`），會破壞 SQL 語法甚至執行任意 SQL。攻擊者若能在 `$ROOT` 下建立惡意名稱的目錄，即可操縱資料庫。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `:name` 綁定參數。

**判斷依據**：第 48 行直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與 repo 名稱</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。`$hook` 是固定路徑，但 `$repo` 來自 `basename "$dir"`，若 repo 目錄名稱包含 shell 特殊字元（例如 `; rm -rf ~`），可能導致任意指令執行。

建議避免使用 eval，改為直接執行：
```bash
"$hook" "$repo"
```
若需要傳遞多個參數，應使用陣列。

**判斷依據**：第 57 行使用 eval 執行包含未受信任變數的字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 未加引號，branch 名稱可能被 shell 展開</summary>

`git checkout $BRANCH` 未將 `$BRANCH` 加上雙引號。雖然前面有格式驗證，但若 branch 名稱包含 glob 字元（例如 `*`）或空白（雖然格式驗證已排除空白），仍可能造成非預期行為。建議改為 `git checkout "$BRANCH"`。

**判斷依據**：第 34 行未對 `$BRANCH` 加引號。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:38</code> git merge 未檢查失敗，可能導致後續操作在錯誤狀態下執行</summary>

`git merge --ff-only "origin/$BRANCH"` 若因衝突或非 fast-forward 而失敗，腳本不會中止，仍會繼續計算 ahead 並寫入資料庫。這可能導致資料庫記錄不正確的同步結果。建議在 merge 後檢查 exit code，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 36 行未檢查 merge 的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致變數為空或非數字</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查指令是否成功，失敗時設定預設值或中止。

**判斷依據**：第 38 行未檢查 rev-list 的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用未加引號的 glob，可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 包含空白或特殊字元，glob 可能展開成多個路徑，導致刪除非預期的檔案。此外，若 `.cache` 目錄不存在，`rm` 會報錯但腳本繼續執行。建議先檢查目錄是否存在，並使用 `find` 或正確引號處理。

**判斷依據**：第 63 行未對 glob 加引號，且未檢查目錄存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而誤設為 0</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 `$LOG` 不存在或無法讀取，grep 回傳非零，`total` 會被設為 0，但實際上可能有錯誤。建議先檢查檔案是否存在，或使用 `wc -l` 並處理錯誤。

**判斷依據**：第 72 行將 grep 失敗視為 0 筆紀錄。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 `ls` 的輸出以空白分隔，若 repo 目錄名稱包含空白或換行，迴圈會錯誤分割。建議改用 `find` 或 glob：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  ...
```

**判斷依據**：第 80 行使用 `ls` 輸出進行迴圈。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1923 ｜ PR #13</sub>