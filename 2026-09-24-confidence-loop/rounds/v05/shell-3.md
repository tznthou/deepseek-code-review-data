<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、錯誤處理不足，以及變數未加引號可能導致路徑或分支名稱含空格時出錯。最優先應修復 SQL 注入與 eval 的使用，並補強錯誤處理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval "$hook $repo"` 執行未受信任的字串 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未加引號：`ahead` 可能為空導致 `[ "$ahead" -gt 0 ]` 報錯 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑未加引號：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `grep -c .` 計算行數可能不準確 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | `for d in $(ls "$ROOT")` 無法處理含空格或換行的目錄名稱 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自目錄名稱，完全未驗證。攻擊者若能在 repo 根目錄建立名稱包含單引號的目錄（例如 `x'); DROP TABLE runs;--`），即可注入任意 SQL。

**失敗情境**：假設 `$ROOT` 下有一個名為 `evil'); DELETE FROM runs;--` 的目錄，且內含 `.git` 子目錄，則執行到該 repo 時會執行 `DELETE FROM runs;`，導致資料被刪除。

**建議**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數做單引號跳脫（`${name//\'/\'\'}`），但參數化查詢才是正解。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 來自 `basename "$dir"`，未經驗證或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval "$hook $repo"` 執行未受信任的字串</summary>

`run_hook` 使用 `eval` 執行 hook 路徑與 repo 名稱。`$hook` 是固定路徑，但 `$repo` 來自 `$d`（目錄名稱），攻擊者可建立名稱包含 shell 指令的目錄（例如 `x; rm -rf ~`），當該目錄內有 `.git` 且 hook 檔案存在且可執行時，`eval` 會執行注入的指令。

**失敗情境**：若 `$ROOT` 下有名為 `x; touch /tmp/pwned` 的目錄，且 `$ROOT/.hooks/post-sync` 存在且可執行，則執行到該 repo 時會建立 `/tmp/pwned` 檔案。

**建議**：避免使用 `eval`，改用直接執行並傳參數：
```bash
"$hook" "$repo"
```
若 hook 需要 shell 解讀，應明確控制輸入，或改用 `bash -c` 並小心引用。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`，其中 `$repo` 來自 `$d`，未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入</summary>

`sync_one` 中所有 `git` 指令的 stderr 都被重導到 log，但 exit code 未檢查。若 `git fetch` 失敗（例如網路問題），後續 `git checkout` 或 `git merge` 可能基於過時的遠端分支執行，甚至 `git merge` 失敗後仍繼續計算 `ahead` 並寫入資料庫，造成報表數據不正確。

**失敗情境**：假設 `git fetch` 因網路中斷失敗，但本地已有舊的 `origin/$BRANCH`，`git merge --ff-only` 可能成功合併到舊狀態，而 `ahead` 計算的是與舊遠端的差異，導致回報的領先 commit 數不準確。

**建議**：在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo，例如：
```bash
git fetch origin --prune 2>>"$LOG" || { echo "[$name] fetch failed" >> "$LOG"; return 1; }
```

**判斷依據**：diff 第 34-37 行：連續執行 git 指令，未檢查 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未加引號：`ahead` 可能為空導致 `[ "$ahead" -gt 0 ]` 報錯</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。接著 `[ "$ahead" -gt 0 ]` 會因為空字串無法轉為整數而報錯，且錯誤訊息會輸出到終端（未重導），可能中斷腳本（若 `set -e` 啟用）或造成困擾。

**失敗情境**：若 `origin/$BRANCH` 不存在（例如 branch 名稱打錯但通過格式驗證），`git rev-list` 失敗，`ahead` 為空，`[ "$ahead" -gt 0 ]` 會輸出錯誤訊息，且後續 SQL 插入的 `ahead` 為空字串，可能導致型別不符。

**建議**：在計算 `ahead` 後檢查是否為數字，或提供預設值：
```bash
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null) || ahead=0
```
並在測試條件中使用 `[[ $ahead =~ ^[0-9]+$ ]] && [ "$ahead" -gt 0 ]`。

**判斷依據**：diff 第 40-42 行：`ahead` 可能為空，未處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑未加引號：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 包含空格或特殊字元，路徑可能被錯誤解析。此外，若 `.cache` 目錄不存在，`rm -rf` 不會報錯，但若 `$ROOT` 未定義或為空，可能變成 `rm -rf /.cache/*`，造成災難性刪除。

**失敗情境**：若使用者執行 `./repo_sync.sh` 未帶參數，`$ROOT` 為空，`cleanup_cache` 會執行 `rm -rf /.cache/*`，嘗試刪除根目錄下的 `.cache` 內容（若權限允許）。

**建議**：在使用 `$ROOT` 前檢查是否為空，並對路徑加引號：
```bash
[ -z "$ROOT" ] && { echo "ROOT is required" >&2; exit 1; }
rm -rf "$ROOT/.cache"/*
```

**判斷依據**：diff 第 69 行：`rm -rf "$ROOT"/.cache/*`，未檢查 `$ROOT` 是否為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `grep -c .` 計算行數可能不準確</summary>

`summarize` 使用 `grep -c . "$LOG"` 計算行數，但 `grep -c .` 只計算包含至少一個字元的行，空行不會被計入。若 log 中有空行，`total` 會低估，導致判斷是否超過 100 行的邏輯不準確。

**失敗情境**：若 log 中有 50 行內容和 60 行空行，`grep -c .` 回傳 50，不會觸發 trim，但實際檔案有 110 行。

**建議**：改用 `wc -l < "$LOG"` 計算行數。

**判斷依據**：diff 第 76 行：使用 `grep -c .` 計算行數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> `for d in $(ls "$ROOT")` 無法處理含空格或換行的目錄名稱</summary>

`main` 使用 `for d in $(ls "$ROOT")` 迭代目錄，若目錄名稱包含空格或換行，會被拆成多個項目，導致路徑錯誤。此外，`ls` 的輸出可能包含特殊字元，造成非預期行為。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，`for` 迴圈會將其拆成 `my` 和 `repo` 兩個項目，後續 `target="$ROOT/$d"` 會指向不存在的路徑。

**建議**：使用 glob 或 `find` 搭配 `-print0` 和 `while read -d ''` 來處理：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

**判斷依據**：diff 第 82 行：使用 `$(ls ...)` 進行迭代。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2800 ｜ PR #13</sub>