<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及併發與效能問題。最該先修的是 sync_one 中的 SQL 注入與 run_hook 的 eval 使用，因為它們可能被惡意 repo 名稱或 hook 內容利用。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗時未中止，可能導致錯誤的 ahead 計算 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算在 git rev-list 失敗時可能得到空值，導致 SQL 錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 搭配變數，若 ROOT 為空或錯誤可能刪除大量檔案 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:68` | summarize 中 grep -c 可能因檔案不存在而失敗，但錯誤處理不完整 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名包含空格或換行時會出錯 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | local 關鍵字在 for 迴圈內使用，可能不符合 POSIX，但 bash 支援 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 將 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法，甚至可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數做單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 46 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑與 repo 名稱</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 程式碼執行。若 hook 路徑或 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），可能造成任意命令執行。即使 hook 檔案本身是受信任的，repo 名稱來自目錄名稱，攻擊者可能建立惡意名稱的 repo 目錄。

建議避免 eval，改用直接執行：
```bash
"$hook" "$repo"
```
並確保 hook 路徑與 repo 名稱不包含特殊字元，或使用 `--` 分隔參數。

**判斷依據**：diff 第 57 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗時未中止，可能導致錯誤的 ahead 計算</summary>

`git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"` 的錯誤僅被重導向到 log，腳本仍會繼續執行。若 checkout 失敗（例如 branch 不存在），後續 merge 可能失敗，但 `ahead` 仍會計算，可能得到錯誤的數值並寫入資料庫。

建議在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo。例如：
```bash
git checkout "$BRANCH" 2>>"$LOG" || { echo "checkout failed" >> "$LOG"; return 1; }
```

**判斷依據**：diff 第 38-39 行：`git checkout $BRANCH 2>>"$LOG"` 與 `git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算在 git rev-list 失敗時可能得到空值，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 origin/$BRANCH 不存在），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。

建議在指令失敗時設定預設值，例如：
```bash
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null) || ahead=0
```

**判斷依據**：diff 第 41 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 搭配變數，若 ROOT 為空或錯誤可能刪除大量檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未設定或為空，會變成 `rm -rf /.cache/*`，可能刪除系統檔案。雖然 main 中有檢查 BRANCH，但未檢查 ROOT 是否為空。

建議在 main 中增加對 ROOT 的檢查，並在 rm 前確認路徑非空且為預期目錄。例如：
```bash
if [ -z "$ROOT" ]; then echo "ROOT is required"; exit 1; fi
```

**判斷依據**：diff 第 63 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 grep -c 可能因檔案不存在而失敗，但錯誤處理不完整</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 LOG 檔案不存在，grep 會回傳非零，但 `total` 可能已被設為空字串，`|| total=0` 不一定會執行（因為命令替換的 exit code 是 grep 的，但若 grep 失敗，`total` 可能為空）。後續 `[ "$total" -gt 100 ]` 會因空字串而報錯。

建議改為：
```bash
total=$(grep -c . "$LOG" 2>/dev/null || echo 0)
```

**判斷依據**：diff 第 72 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名包含空格或換行時會出錯</summary>

`for d in $(ls "$ROOT")` 會將 ls 的輸出以空白分割，若 repo 目錄名稱包含空格，會被拆成多個項目。建議改用 glob：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
```

**判斷依據**：diff 第 79 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> local 關鍵字在 for 迴圈內使用，可能不符合 POSIX，但 bash 支援</summary>

`local target="$ROOT/$d"` 在函數外使用 local 是 bash 擴充，若腳本以 sh 執行會失敗。但 shebang 是 bash，所以可接受。若希望相容 sh，應移除 local。

**判斷依據**：diff 第 81 行：`local target="$ROOT/$d"`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2288 ｜ PR #13</sub>