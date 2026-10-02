<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、錯誤處理不足、以及使用全域變數與 ls 解析目錄等可靠性問題。最應優先修復 SQL 注入與 eval 的使用，並加強錯誤處理。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | git checkout 與 merge 失敗未中止，可能導致錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 可能為空字串，導致 SQL 寫入失敗或錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 刪除目錄內容，路徑未驗證 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:47` | SQL 寫入未處理 ahead 為非數字的情況 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 與 `BRANCH` 直接以字串串接方式插入 SQL 查詢，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'; DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行單引號跳脫（`${name//\'/\'\'}`）。

**判斷依據**：第 42 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$ROOT` 或 repo 名稱包含特殊字元（如空白、分號、命令替換），可能導致任意命令執行。例如 repo 名稱為 `foo; rm -rf ~` 時，會執行 `rm -rf ~`。

建議避免使用 eval，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 hook 路徑與參數正確引用。

**判斷依據**：第 51 行使用 eval 執行字串，未對參數進行安全處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> git checkout 與 merge 失敗未中止，可能導致錯誤結果</summary>

`git checkout $BRANCH` 與 `git merge --ff-only` 的錯誤僅被重導向至 log，但腳本仍繼續執行後續的 `git rev-list` 與 SQL 寫入。若 checkout 或 merge 失敗（例如 branch 不存在、有衝突），`ahead` 可能計算錯誤或為空，導致寫入不正確的資料。

建議在每個 git 指令後檢查 exit code，失敗時中止該 repo 的處理並記錄錯誤。

**判斷依據**：第 34-35 行未檢查指令執行結果，錯誤僅寫入 log。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 可能為空字串，導致 SQL 寫入失敗或錯誤</summary>

`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。

建議在取得 ahead 後檢查是否為數字，若不是則設為 0 或中止處理。

**判斷依據**：第 38 行未處理 git 指令失敗時 ahead 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 刪除目錄內容，路徑未驗證</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。此外，若 `.cache` 不存在，`rm` 會報錯但腳本仍繼續執行。

建議檢查 `$ROOT` 是否為有效目錄，並使用更安全的刪除方式（例如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

**判斷依據**：第 57 行直接使用 rm -rf，未對路徑進行驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若 repo 目錄名稱包含空白，會被拆成多個項目，導致後續路徑錯誤。

建議改用 glob 或 `find`：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

**判斷依據**：第 70 行使用 ls 的輸出進行迴圈，未考慮檔名中的空白。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:47</code> SQL 寫入未處理 ahead 為非數字的情況</summary>

即使 ahead 為空或非數字，SQL 插入仍會執行，可能導致資料庫寫入失敗或寫入錯誤資料。建議在寫入前驗證 ahead 為整數。

**判斷依據**：第 42 行未對 ahead 進行型別檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 因檔案不存在而失敗，`total` 會被設為 0，但若 grep 因其他原因失敗（如權限問題），也會被設為 0，可能隱藏錯誤。建議分開處理檔案不存在與其他錯誤。

**判斷依據**：第 64 行將所有 grep 失敗都視為 total=0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1977 ｜ PR #13</sub>