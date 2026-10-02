<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險包括：SQL 注入（repo 名稱與 branch 未正確跳脫）、`eval` 執行未受信任的 hook 路徑、`ls` 解析路徑的脆弱性、錯誤處理不足（`cd`、`git checkout`、`git merge` 失敗時仍繼續執行）、以及 `cleanup_cache` 可能刪除任意目錄。建議先修正安全性與錯誤處理問題，再考慮合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未跳脫 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | `eval` 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 可能刪除任意目錄 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | `ls` 解析路徑脆弱，且未處理特殊檔名 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:33` | `cd` 失敗時未中止，可能操作錯誤目錄 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 與 `git merge` 失敗時未處理 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 可能為空，導致 SQL 錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:47` | SQL 插入未使用參數化查詢 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未跳脫</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 包含單引號，將破壞 SQL 語法或注入任意 SQL。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，將導致資料表被刪除。建議使用參數化查詢（sqlite3 支援 `?` 佔位符）或正確跳脫輸入。

**判斷依據**：第 44 行直接將變數嵌入 SQL 字串，未做任何跳脫。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> `eval` 執行未受信任的 hook 路徑</summary>

`eval "$hook $repo"` 會執行 `$hook` 的內容。若 `$ROOT/.hooks/post-sync` 檔案被惡意修改（例如包含 `rm -rf /`），將造成嚴重後果。此外，`$repo` 未加引號，若 repo 名稱包含空格或特殊字元，可能導致命令注入。建議避免使用 `eval`，改為直接執行 `"$hook" "$repo"`，並確保 hook 檔案權限受控。

**判斷依據**：第 55 行使用 `eval` 執行未受信任的 hook 路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 可能刪除任意目錄</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除不該刪除的檔案。例如，若 `$ROOT` 為 `/`，則會嘗試刪除 `/.cache/*`，可能影響系統。建議檢查 `$ROOT` 是否為有效目錄，並避免使用 `rm -rf` 搭配變數路徑，或至少確認路徑非空且為預期目錄。

**判斷依據**：第 60 行使用 `rm -rf` 搭配變數路徑，未做任何防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> `ls` 解析路徑脆弱，且未處理特殊檔名</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迭代，若目錄名稱包含空格、換行或 glob 字元，將導致錯誤。此外，`ls` 的輸出可能包含非目錄項目，需在迴圈內檢查。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-mindepth 1 -maxdepth 1 -type d`。

**判斷依據**：第 68 行使用 `ls` 輸出進行迴圈，未處理特殊檔名。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:33</code> `cd` 失敗時未中止，可能操作錯誤目錄</summary>

`cd "$dir"` 若失敗（例如目錄不存在或權限不足），腳本仍會繼續執行後續的 `git` 指令，可能操作錯誤的 repo。建議在 `cd` 失敗時立即返回錯誤，例如 `cd "$dir" || return 1`。

**判斷依據**：第 31 行未檢查 `cd` 的返回值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 與 `git merge` 失敗時未處理</summary>

`git checkout $BRANCH` 和 `git merge --ff-only "origin/$BRANCH"` 若失敗（例如 branch 不存在、合併衝突），腳本仍會繼續執行，並將錯誤結果寫入資料庫。建議檢查這些指令的返回值，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 34-35 行未檢查 git 指令的返回值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 可能為空，導致 SQL 錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串，後續的 `[ "$ahead" -gt 0 ]` 和 SQL 插入會出錯。建議在失敗時設定預設值（如 0）並記錄錯誤。

**判斷依據**：第 37 行未處理 `git rev-list` 失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:47</code> SQL 插入未使用參數化查詢</summary>

即使不考慮注入，直接拼接 SQL 字串也容易出錯。建議使用 `sqlite3` 的參數化查詢功能，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

**判斷依據**：第 44 行使用字串拼接而非參數化查詢。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 256) ｜ completion tokens 1897 ｜ PR #13</sub>