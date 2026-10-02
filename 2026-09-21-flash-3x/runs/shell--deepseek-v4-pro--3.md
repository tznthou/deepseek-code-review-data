<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個批次同步多個 Git repo 的 shell script，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入、路徑處理不當、錯誤處理不足，以及使用 `eval` 執行 hook。最優先應修復 SQL 注入與 `eval` 的使用，並改善錯誤處理與路徑驗證。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 使用 eval 執行 hook 可能導致命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗時未中止，可能導致資料不一致 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 可能誤刪重要檔案 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗，導致 SQL 插入空值 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄名稱可能因特殊字元出錯 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | 未驗證 $ROOT 是否為有效目錄 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 查詢。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 語句。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢（例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`），或至少使用 `sqlite3` 的 `-quote` 選項或手動跳脫單引號。

**判斷依據**：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 使用 eval 執行 hook 可能導致命令注入</summary>

`run_hook` 函式使用 `eval "$hook $repo"` 執行外部 hook。若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱包含 `; rm -rf /`），將導致任意命令執行。建議避免使用 `eval`，改為直接執行：`"$hook" "$repo"`。

**判斷依據**：第 51 行使用 eval 執行未受信任的輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗時未中止，可能導致資料不一致</summary>

`sync_one` 函式中，`git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導向至 log，未檢查退出碼。若 checkout 或 merge 失敗（例如 branch 不存在、合併衝突），後續仍會計算 ahead 並寫入資料庫，造成錯誤的同步狀態。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 28-29 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 可能誤刪重要檔案</summary>

`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議先驗證 `$ROOT` 存在且為目錄，並避免使用 `*` 萬用字元，或改用 `find` 搭配更嚴格的條件。

**判斷依據**：第 55 行直接刪除目錄內容，缺乏防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗，導致 SQL 插入空值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若執行失敗（例如 origin/$BRANCH 不存在），`ahead` 將為空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查 `git rev-list` 的退出碼，失敗時設定預設值或跳過。

**判斷依據**：第 31 行未處理指令失敗的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄名稱可能因特殊字元出錯</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或萬用字元，將導致錯誤分割。建議改用 `for d in "$ROOT"/*/` 並搭配 `basename`，或使用 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：第 66 行使用 ls 輸出進行迴圈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> 未驗證 $ROOT 是否為有效目錄</summary>

`main` 函式未檢查 `$ROOT` 是否存在且為目錄。若使用者提供不存在的路徑，`ls` 會失敗，但腳本仍會繼續執行並嘗試進入不存在的目錄。建議在開頭加上 `[ -d "$ROOT" ] || { echo "錯誤：$ROOT 不是目錄" >&2; exit 1; }`。

**判斷依據**：第 66 行之前未驗證 $ROOT。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2517 (cache hit 2432) ｜ completion tokens 1666</sub>