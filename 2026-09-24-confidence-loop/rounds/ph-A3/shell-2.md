<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、錯誤處理不足（set -e 缺失、git 指令失敗未檢查）、以及變數未加引號可能導致路徑問題。最優先應修補 SQL 注入與 eval 的使用，並加入錯誤處理機制。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 缺少錯誤處理：git 指令失敗仍繼續執行，可能導致錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | 變數未加引號：`git checkout $BRANCH` 可能因 branch 名稱含空格或特殊字元而失敗 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `rm -rf "$ROOT"/.cache/*` 可能因路徑未加引號或變數為空而誤刪 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | `for d in $(ls "$ROOT")` 可能因檔名包含空格或換行而失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。

**失敗情境**：假設 `$ROOT` 下有一個目錄名為 `x'; DROP TABLE runs; --`，則執行的 SQL 會變成：
```sql
INSERT INTO runs VALUES('x'; DROP TABLE runs; --', 'main', 0, datetime('now'))
```
這會導致 `runs` 資料表被刪除。

**建議修法**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 是使用者提供的參數；`$repo` 是 repo 目錄名稱。若攻擊者能控制 repo 目錄名稱（例如建立一個名為 `; rm -rf ~` 的目錄），則可注入任意命令。

**失敗情境**：假設 `$ROOT` 下有一個目錄名為 `; touch /tmp/pwned`，則 `eval` 會執行：
```bash
/root/.hooks/post-sync ; touch /tmp/pwned
```
導致任意命令執行。

**建議修法**：避免使用 `eval`，直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 以引號包覆。

**判斷依據**：diff 第 50 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 缺少錯誤處理：git 指令失敗仍繼續執行，可能導致錯誤結果</summary>

`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 等指令失敗時（例如網路問題、branch 不存在、merge 衝突），腳本不會停止，後續的 `git rev-list` 與 SQL 寫入仍會執行，可能記錄錯誤的同步結果。

**失敗情境**：若 `git fetch` 因網路中斷失敗，`origin/$BRANCH` 可能不存在，`git rev-list --count "origin/$BRANCH"..HEAD` 會回傳錯誤，`ahead` 變數可能為空或非數字，導致 SQL 寫入失敗或寫入錯誤資料。

**建議修法**：在每個 git 指令後檢查 exit code，或使用 `set -e` 並搭配 `trap` 處理錯誤。

**判斷依據**：diff 第 34-38 行：連續執行 git 指令但未檢查 exit code

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> 變數未加引號：`git checkout $BRANCH` 可能因 branch 名稱含空格或特殊字元而失敗</summary>

`git checkout $BRANCH` 未將 `$BRANCH` 以雙引號包覆。雖然開頭有驗證 branch 名稱格式，但允許的字元包含 `.`、`_`、`/`、`-`，這些字元在 shell 中通常安全，但若 branch 名稱包含空格（雖然驗證不允許）或 glob 字元（如 `*`），可能導致非預期行為。

**失敗情境**：若 branch 名稱包含 `*`（例如 `feature/*`），shell 會展開成目前目錄下的檔案名稱，導致 `git checkout` 收到錯誤參數。

**建議修法**：改為 `git checkout "$BRANCH"`。

**判斷依據**：diff 第 36 行：`git checkout $BRANCH 2>>"$LOG"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `rm -rf "$ROOT"/.cache/*` 可能因路徑未加引號或變數為空而誤刪</summary>

`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未設定或為空字串，則會變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `$ROOT` 包含空格，未加引號的部分可能導致路徑分割。

**失敗情境**：若使用者未提供第一個參數，`$ROOT` 為空，則 `rm -rf /.cache/*` 會嘗試刪除根目錄下的 `.cache` 內容，可能造成系統損壞。

**建議修法**：在使用 `$ROOT` 前檢查是否為空，並將整個路徑以雙引號包覆：`rm -rf "$ROOT/.cache"/*`。

**判斷依據**：diff 第 55 行：`rm -rf "$ROOT"/.cache/*`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> `for d in $(ls "$ROOT")` 可能因檔名包含空格或換行而失敗</summary>

使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或其他特殊字元，會被拆成多個項目，導致後續處理錯誤。

**失敗情境**：若 `$ROOT` 下有一個目錄名為 `my repo`，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致 `target` 路徑錯誤。

**建議修法**：使用 `find` 或 glob 搭配 null 分隔符，例如：
```bash
while IFS= read -r -d '' d; do
  ...
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
```

**判斷依據**：diff 第 70 行：`for d in $(ls "$ROOT"); do`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2151 ｜ PR #13</sub>