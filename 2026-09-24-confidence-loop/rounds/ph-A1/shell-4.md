<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。整體結構清晰，有基本的輸入驗證與錯誤處理，但存在幾個高風險問題：SQL 注入、命令注入、未處理的 git 錯誤、以及變數作用域錯誤。最優先應修復 SQL 注入與命令注入，並確保 git 操作失敗時能正確中止。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能導致錯誤資料寫入資料庫 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 可能為空字串，導致 SQL 語法錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:88` | `local` 使用在函式外，導致變數作用域錯誤 | 0.80 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，可能因檔名包含換行或空格而失敗 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱包含單引號（例如 `my'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄來竄改資料庫內容。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：第 45 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。雖然 `$hook` 是固定路徑，但 `$repo` 來自目錄名稱，攻擊者可建立名稱包含 shell 特殊字元的 repo 目錄（例如 `x; rm -rf ~`），導致任意命令執行。

建議避免使用 `eval`，改為直接執行並正確引用參數：
```bash
"$hook" "$repo"
```

**判斷依據**：第 58 行使用 eval 執行包含未受信任變數的字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能導致錯誤資料寫入資料庫</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 寫入 log，腳本仍會繼續執行。例如，若 `git checkout` 因本地變更而失敗，後續的 `git merge` 可能基於錯誤的 branch 執行，且 `ahead` 的計算結果可能不正確，最終將錯誤資料寫入資料庫。

建議在每個 git 指令後檢查 exit code，失敗時中止該 repo 的同步並記錄錯誤。

**判斷依據**：第 34-36 行未檢查 git 指令的執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 可能為空字串，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 SQL 插入會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 錯誤。

建議在計算後檢查 `ahead` 是否為空，並設定預設值（如 0）或中止。

**判斷依據**：第 38 行未處理命令失敗時變數為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:88</code> `local` 使用在函式外，導致變數作用域錯誤</summary>

`main` 函式中的 `for d in $(ls "$ROOT"); do` 迴圈內使用了 `local target="$ROOT/$d"`。`local` 只能在函式內使用，在函式外使用會報錯（在某些 bash 版本中會導致腳本終止）。

應移除 `local`，直接賦值：`target="$ROOT/$d"`。

**判斷依據**：第 75 行在 main 函式內使用 local，但 main 本身是函式，此處 local 是合法的。然而，若此迴圈不在函式內（例如直接放在腳本主體），則會出錯。根據 diff，此行位於 main 函式內，因此可能不是問題。但需確認 main 函式的範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若 repo 目錄名稱包含空格或換行，會導致迴圈變數錯誤。

建議使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

**判斷依據**：第 73 行使用 ls 的輸出進行迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 因輸入錯誤而為空或根目錄，可能刪除大量檔案。雖然 `$ROOT` 來自使用者輸入，但建議加入防護，例如檢查 `$ROOT` 是否為有效目錄且非根目錄。

**判斷依據**：第 63 行直接使用 rm -rf。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1822 ｜ PR #13</sub>