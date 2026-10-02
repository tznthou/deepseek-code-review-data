<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。整體結構清楚，有基本的參數驗證與錯誤處理，但存在幾個需要修正的問題：最嚴重的是 SQL 注入風險（repo 名稱與 branch 名稱直接拼接進 SQL 字串），以及使用 `eval` 執行 hook 可能導致任意程式碼執行。此外，`ls` 解析目錄名稱在包含空白時會出錯，`git checkout` 未加 `--` 可能將 branch 名稱誤判為選項，且多個 repo 共用同一個 log 檔可能造成內容交錯。建議先修正安全性問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 名稱未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 使用 `eval` 執行 hook 可能導致任意程式碼執行 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄名稱，無法處理包含空白或換行的路徑 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 未使用 `--` 分隔選項與 branch 名稱 | 0.80 |
| 🔸 | Minor | `sandbox/repo_sync.sh:13` | 多個 repo 共用同一個 log 檔，可能造成內容交錯 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 名稱未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 將 `$name` 與 `$BRANCH` 直接拼接進 SQL 字串。雖然 branch 名稱有正規表示式驗證，但 repo 名稱（來自目錄名稱）完全未驗證，攻擊者可以建立名稱包含單引號的目錄（例如 `'; DROP TABLE runs; --`），導致 SQL 注入，可能破壞資料庫或執行任意 SQL。

**失敗情境**：在 `$ROOT` 下建立一個名為 `evil'; DROP TABLE runs; --` 的目錄（且內含 `.git` 子目錄），執行腳本後，`runs` 資料表會被刪除。

**建議修法**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫（如 `sqlite3` 的 `:name` 參數）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 來自 `basename "$dir"`，`$dir` 來自 `ls "$ROOT"` 的輸出，完全由使用者控制。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 使用 `eval` 執行 hook 可能導致任意程式碼執行</summary>

`run_hook` 中使用 `eval "$hook $repo"` 執行 hook 腳本。`$hook` 路徑是固定的（`$ROOT/.hooks/post-sync`），但 `$repo` 來自目錄名稱，未經驗證。攻擊者可以建立名稱包含 shell 特殊字元的目錄（例如 `foo; rm -rf /`），當 hook 存在且可執行時，`eval` 會將該名稱當作指令的一部分執行，造成任意程式碼執行。

**失敗情境**：在 `$ROOT` 下建立名為 `x; touch /tmp/pwned` 的目錄（含 `.git`），並放置可執行的 `$ROOT/.hooks/post-sync`，執行腳本後 `/tmp/pwned` 會被建立。

**建議修法**：不要使用 `eval`，直接執行 `"$hook" "$repo"`，並確保 `$repo` 作為參數傳遞，而非指令的一部分。

**判斷依據**：diff 第 50 行：`eval "$hook $repo"`，其中 `$repo` 來自 `run_hook "$d"`，`$d` 來自 `ls "$ROOT"` 的輸出。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄名稱，無法處理包含空白或換行的路徑</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白和換行分割，因此如果 repo 目錄名稱包含空白（例如 `my repo`），會被拆成多個 token，導致 `$target` 路徑錯誤，腳本無法正確處理該 repo。

**失敗情境**：在 `$ROOT` 下建立名為 `my repo` 的目錄（含 `.git`），執行腳本時，迴圈會嘗試處理 `my` 和 `repo` 兩個不存在的路徑，該 repo 不會被同步。

**建議修法**：使用 `find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0` 搭配 `while IFS= read -r -d '' dir` 迴圈，或使用 `shopt -s nullglob` 與 glob 展開。

**判斷依據**：diff 第 73 行：`for d in $(ls "$ROOT"); do`，這是常見的錯誤用法，無法處理特殊字元。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 未使用 `--` 分隔選項與 branch 名稱</summary>

`git checkout $BRANCH` 中，如果 `$BRANCH` 以 `-` 開頭（例如 `-foo`），Git 會將其視為選項而非 branch 名稱，可能導致非預期行為。雖然 branch 名稱的正規表示式允許 `-`，但未排除以 `-` 開頭的情況。

**失敗情境**：若 `$BRANCH` 為 `-b`，`git checkout -b` 會建立新分支，而不是切換到名為 `-b` 的分支。

**建議修法**：使用 `git checkout -- "$BRANCH"`，或在正規表示式中禁止以 `-` 開頭。

**判斷依據**：diff 第 33 行：`git checkout $BRANCH 2>>"$LOG"`，且第 14 行的正規表示式 `^[A-Za-z0-9._/-]+$` 允許以 `-` 開頭。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:13</code> 多個 repo 共用同一個 log 檔，可能造成內容交錯</summary>

所有 repo 的同步過程都將輸出附加到同一個 `$LOG` 檔（`/tmp/repo_sync.log`），且 `sync_one` 中的 `git` 指令使用 `2>>"$LOG"` 並行寫入。如果多個 repo 同時執行（雖然目前是循序），或 log 檔被其他程序寫入，內容可能交錯，影響後續的 `summarize` 與除錯。

**建議修法**：為每個 repo 使用獨立的 log 檔，或在寫入時加上鎖定機制。

**判斷依據**：diff 第 15 行：`LOG=/tmp/repo_sync.log`，且多處使用 `2>>"$LOG"` 寫入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2696 (cache hit 768) ｜ completion tokens 1955 ｜ PR #13</sub>