<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支批次同步多個 repo 的 shell 腳本，會 fetch/checkout/merge 後把結果寫入 sqlite 並產生摘要。主要風險集中在 shell 注入與資料寫入：`$BRANCH` 未加引號直接進 git 指令、`$name`/`$BRANCH` 未經處理就拼進 SQL、`run_hook` 使用 `eval` 執行路徑、以及 `cleanup_cache` 對 `$ROOT` 未驗證就 `rm -rf`。這些在 `$ROOT` 或 repo 目錄名稱由外部控制時可能造成指令注入或誤刪檔案，建議優先修正。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 以字串拼接寫入，repo 名稱含單引號會注入或寫入失敗 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 未加引號，branch 含空白或 glob 會被拆成多個參數 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:56` | run_hook 使用 eval 執行路徑，repo 名稱可注入指令 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 對未驗證的 $ROOT 執行 rm -rf | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈以 ls 展開，含空白或換行的目錄名會被拆開 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 可能為空字串，數值比較與 SQL 寫入會出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:33` | sync_one 內 cd 後未回到原目錄，後續 repo 相對路徑可能出錯 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 以字串拼接寫入，repo 名稱含單引號會注入或寫入失敗</summary>

`$name` 來自 `basename "$dir"`，完全由檔案系統上的目錄名稱決定，未做任何跳脫就拼進 SQL 字串。若某個 repo 目錄名為 `foo'); DROP TABLE runs;--`，產生的語句會變成 `INSERT INTO runs VALUES('foo'); DROP TABLE runs;--', ...`，直接破壞資料表；即使只是名稱含單引號（如 `it's`）也會讓 INSERT 語法錯誤、該筆紀錄遺失。建議改用參數化寫法，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?1,?2,?3,datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對單引號做 `''` 轉義。

**判斷依據**：diff 第 34 行直接以單引號包住 `$name`、`$BRANCH` 變數拼接 SQL，且 `name=$(basename "$dir")` 未經任何驗證或轉義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 未加引號，branch 含空白或 glob 會被拆成多個參數</summary>

`git checkout $BRANCH` 未加引號。雖然開頭的正則 `^[A-Za-z0-9._/-]+$` 擋掉了空白與多數特殊字元，但 `*`、`?`、`[` 等 glob 字元仍被允許（`.` 與 `-` 在字元類別中，`*` 不在，但 `[` 也不在——請注意此正則實際上不允許 `*`，然而未加引號仍會在含 `[` 等情況下有 word splitting/globbing 風險）。更關鍵的是 `git merge --ff-only "origin/$BRANCH"` 這行有加引號、`git checkout` 這行沒有，行為不一致。建議統一改為 `git checkout "$BRANCH"`，避免未來放寬正則時產生非預期展開。

**判斷依據**：diff 第 31 行 `git checkout $BRANCH` 未加引號，而同函式第 32 行 `git merge --ff-only "origin/$BRANCH"` 有加引號，兩者不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:56</code> run_hook 使用 eval 執行路徑，repo 名稱可注入指令</summary>

`eval "$hook $repo"` 會把 `$repo`（來自 `$d`，即 `ls "$ROOT"` 的輸出）當成 shell 程式碼解析。若 `$ROOT` 下存在名稱如 `x; rm -rf ~` 的目錄，`eval` 會執行其中的 `rm -rf ~`。即使 hook 本身可信任，`$repo` 也不該進入 `eval`。建議改為 `"$hook" "$repo"` 直接呼叫，不要用 `eval`。

**判斷依據**：diff 第 52 行 `eval "$hook $repo"`，其中 `$repo` 由 `run_hook "$d"` 傳入，`$d` 來自 `for d in $(ls "$ROOT")`，屬外部可控輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 對未驗證的 $ROOT 執行 rm -rf</summary>

`rm -rf "$ROOT"/.cache/*` 在 `$ROOT` 為空或指向非預期路徑時行為危險。`main` 只檢查 `$BRANCH` 是否為空，沒有檢查 `$ROOT`；若使用者只帶一個參數（`$ROOT` 有值、`$BRANCH` 為空）會先 exit，但若 `$ROOT` 被設為 `/` 或 `$HOME`，就會刪除 `/.cache/*` 或 `~/.cache/*`。建議在 `main` 開頭驗證 `$ROOT` 非空且為存在的目錄，並在 `cleanup_cache` 內再次確認路徑。

**判斷依據**：diff 第 57 行 `rm -rf "$ROOT"/.cache/*`，而 `main` 中僅檢查 `[ -z "$BRANCH" ]`，未對 `$ROOT` 做任何驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈以 ls 展開，含空白或換行的目錄名會被拆開</summary>

`for d in $(ls "$ROOT")` 依賴 word splitting，目錄名稱含空白、tab 或換行時會被拆成多個項目，導致 `$ROOT/$d` 指向不存在的路徑而被 `continue` 跳過，該 repo 靜默漏同步。建議改用 `for target in "$ROOT"/*/; do` 或 `find ... -print0` 搭配 `while IFS= read -r -d ''`。

**判斷依據**：diff 第 78 行 `for d in $(ls "$ROOT"); do`，未使用 null 分隔或 glob 直接展開。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空字串，數值比較與 SQL 寫入會出錯</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 在 `origin/$BRANCH` 不存在（例如 fetch 失敗或 branch 拼錯）時會輸出空字串。接著 `[ "$ahead" -gt 0 ]` 會因空字串而報 `integer expression expected`，且 SQL 會寫入 `VALUES(..., , ...)` 造成語法錯誤。建議加上 `ahead=${ahead:-0}` 或檢查 `git rev-parse --verify` 後再取值。

**判斷依據**：diff 第 42 行以 `2>/dev/null` 吞掉錯誤，失敗時 `$ahead` 為空，第 44 行 `[ "$ahead" -gt 0 ]` 與第 47 行 SQL 皆未防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:33</code> sync_one 內 cd 後未回到原目錄，後續 repo 相對路徑可能出錯</summary>

`sync_one` 內執行 `cd "$dir"` 後沒有 `cd` 回原目錄。由於 `$dir` 是絕對路徑（`$ROOT/$d`），下一輪迴圈的 `$target` 仍是絕對路徑，因此目前不會出錯；但 `run_hook` 使用 `$ROOT/.hooks/post-sync` 也是絕對路徑，暫時安全。不過一旦未來有人在迴圈中加入相對路徑操作就會踩雷。建議在 `sync_one` 內用子 shell 或 `cd "$dir" || return` 並在結束時 `cd -`，或改用 `git -C "$dir"`。

**判斷依據**：diff 第 38 行 `cd "$dir"`，函式結束前未見任何 `cd` 回原目錄的動作。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 2520 (cache hit 2304) ｜ completion tokens 2121</sub>