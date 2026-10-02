<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 `sandbox/repo_sync.sh`，用來批次同步多個 repo、把結果寫入 sqlite 並產生摘要。整體風險偏高：`run_hook` 使用 `eval` 執行路徑可控的腳本、`sync_one` 把未經跳脫的 `$name`/`$BRANCH` 直接串進 SQL、`cleanup_cache` 對 `$ROOT` 未驗證就 `rm -rf`，以及 `cd` 後未回到原目錄導致後續相對路徑錯亂。最該先修的是 `eval` 與 SQL 注入這兩個安全問題，其次是 `rm -rf` 的破壞性風險。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | run_hook 以 eval 執行路徑可控的腳本，具指令注入風險 | 0.90 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 以字串拼接，repo 名稱含單引號會注入或中斷語句 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 對未驗證的 $ROOT 執行 rm -rf | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | sync_one 內 cd 後未返回，迴圈中相對路徑與後續 repo 處理會錯亂 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout/merge 失敗未檢查，ahead 計算與 DB 寫入仍繼續 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 以 ls 展開目錄，含空白或特殊字元的目錄名稱會被拆成多個詞 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 的 total 計數與實際寫入筆數不一致 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> run_hook 以 eval 執行路徑可控的腳本，具指令注入風險</summary>

`eval "$hook $repo"` 會把 `$hook`（`$ROOT/.hooks/post-sync`）與 `$repo`（來自 `ls "$ROOT"` 的目錄名稱）當成 shell 程式碼解析。若 `$ROOT` 底下存在名為 `.hooks/post-sync` 的可執行檔，或某個 repo 目錄名稱含有 shell metacharacter（例如 `foo; rm -rf ~`、`$(...)`、反引號），就會在同步流程中以執行者權限執行任意指令。具體情境：攻擊者（或誤操作）在 `$ROOT` 放一個 `.hooks/post-sync`，或建立一個名稱帶 `;` 的目錄，執行 `./repo_sync.sh ~/work/repos main` 時即觸發。建議改為 `"$hook" "$repo"` 直接呼叫，不要用 `eval`；若必須傳參，用陣列 `"$hook" "$repo"` 形式。

**判斷依據**：diff 第 57 行 `eval "$hook $repo"`，其中 `$hook` 由 `$ROOT` 決定、`$repo` 來自 `ls "$ROOT"` 的目錄名稱，兩者皆非受信任輸入。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 以字串拼接，repo 名稱含單引號會注入或中斷語句</summary>

`INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))` 直接字串拼接。`$name` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"`，完全未跳脫。若某個目錄名稱含單引號（例如 `it's-repo`），SQL 會語法錯誤；若名稱刻意構造（例如 `x',0,0,0); DROP TABLE runs;--`），則可注入任意 SQL。`$BRANCH` 雖有 regex 白名單擋掉引號，但 `$name` 沒有。建議改用參數化：`sqlite3 "$DB" "INSERT INTO runs VALUES(?1,?2,?3,datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 做單引號跳脫。

**判斷依據**：diff 第 44 行，`$name` 由第 26 行 `name=$(basename "$dir")` 得來，未經任何跳脫即進入 SQL 字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 對未驗證的 $ROOT 執行 rm -rf</summary>

`rm -rf "$ROOT"/.cache/*` 在 `$ROOT` 為空或指向非預期路徑時會刪除錯誤位置。`main` 只檢查 `$BRANCH` 是否為空（第 78 行），完全沒有驗證 `$ROOT`。若使用者執行 `./repo_sync.sh "" main` 或 `./repo_sync.sh / main`，`$ROOT` 為空時展開成 `/.cache/*`，會嘗試刪除根目錄下的 `.cache` 內容。建議在 `main` 開頭檢查 `$ROOT` 非空且為存在的目錄（`[ -d "$ROOT" ]`），並在 `cleanup_cache` 內再次確認路徑非空、非 `/`。

**判斷依據**：diff 第 62 行；`main`（第 77-79 行）僅驗證 `$BRANCH`，未驗證 `$ROOT`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> sync_one 內 cd 後未返回，迴圈中相對路徑與後續 repo 處理會錯亂</summary>

`sync_one` 執行 `cd "$dir"` 後沒有任何 `cd` 回原目錄或使用子 shell。`main` 的 for 迴圈（第 84-92 行）在第一次呼叫 `sync_one` 後，行程的當前目錄已變成第一個 repo；之後 `run_hook` 使用 `$ROOT/.hooks/post-sync`（若 `$ROOT` 是相對路徑就會解析錯誤），且 `ls "$ROOT"` 已在迴圈開始前展開，但 `$ROOT` 為相對路徑時後續 `[ -d "$target/.git" ]` 也會以錯誤的基準解析。建議把 `sync_one` 的內容包在子 shell（`( cd "$dir" && ... )`）或在函式結尾 `cd` 回原目錄（先存 `local oldpwd=$PWD`）。

**判斷依據**：diff 第 31 行 `cd "$dir"`，函式內無對應的返回目錄動作；`main` 迴圈第 84-92 行在同一行程中連續呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout/merge 失敗未檢查，ahead 計算與 DB 寫入仍繼續</summary>

`git fetch`、`git checkout $BRANCH`、`git merge --ff-only` 的退出碼都沒有檢查（僅把 stderr 導向 log）。若 checkout 因本地有未提交變更而失敗，或 merge 因非 fast-forward 而失敗，腳本仍會繼續執行 `git rev-list --count` 並把結果寫入 DB，導致報表記錄了實際上未同步成功的狀態。具體情境：repo 有 dirty working tree 時 `git checkout` 失敗，`ahead` 可能為空字串，接著第 44 行 `$ahead` 展開為空會產生 `INSERT ... VALUES('x','main',,datetime('now'))` 的 SQL 語法錯誤。建議對每個 git 指令檢查 `|| { echo ...; return 1; }`，並在 `ahead` 為空時給預設值。

**判斷依據**：diff 第 35 行（及第 34、36 行）皆未檢查退出碼；第 44 行直接使用 `$ahead`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 以 ls 展開目錄，含空白或特殊字元的目錄名稱會被拆成多個詞</summary>

`for d in $(ls "$ROOT")` 依 IFS 對 `ls` 輸出做詞分割，目錄名稱含空白、換行或 glob 字元時會被錯誤拆解，導致 `$target` 指向不存在的路徑而被 `continue` 跳過，或誤指到別的目錄。建議改用 `for d in "$ROOT"/*/; do` 或 `find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0` 搭配 `while IFS= read -r -d ''`。

**判斷依據**：diff 第 85 行；`$d` 後續用於 `$ROOT/$d`（第 86 行）與 `basename`（第 26 行）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 的 total 計數與實際寫入筆數不一致</summary>

`total=$(grep -c . "$LOG")` 統計的是 log 檔中非空行數，但 log 內容包含 `git fetch`/`checkout`/`merge` 的 stderr 輸出，並非「同步筆數」。註解與輸出訊息（第 74 行「本次同步共 $total 筆紀錄」）暗示這是同步筆數，實際上會把 git 的警告訊息也算進去，報表數字會失真。建議改為在 `sync_one` 成功時累加一個計數器，或直接查詢 DB 的 `runs` 表。

**判斷依據**：diff 第 69 行；第 74 行輸出「本次同步共 $total 筆紀錄」，但 `$LOG` 同時接收 git 的 stderr（第 34-36 行）。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 2520 (cache hit 2304) ｜ completion tokens 2322</sub>