<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個 bash 腳本，用於批次同步多個 git repo 並將結果寫入 sqlite。主要風險在於 SQL 注入（repo 名稱與 branch 未經跳脫直接插入 SQL）、`eval` 執行任意 hook 指令、以及 `ls` 解析路徑時未處理特殊字元。此外，錯誤處理不足（如 `git checkout` 失敗仍繼續執行）可能導致資料不一致。建議先修正安全性問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未跳脫 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 任意指令執行：eval 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 路徑解析脆弱：ls 輸出未處理特殊字元 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | 錯誤處理不足：git checkout 失敗仍繼續執行 | 0.80 |
| 🔸 | Minor | `sandbox/repo_sync.sh:41` | ahead 計算可能失敗但未處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未跳脫</summary>

`name` 與 `BRANCH` 直接以單引號字串拼接方式插入 SQL 語句。若 repo 目錄名稱包含單引號（例如 `my'repo`），會破壞 SQL 語法，甚至可注入任意 SQL 指令。攻擊者可透過建立惡意目錄名稱來竄改或刪除資料庫內容。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 任意指令執行：eval 執行未受信任的 hook 路徑</summary>

`eval "$hook $repo"` 會執行 `$hook` 的內容。雖然 `$hook` 是固定路徑，但 `$repo` 來自 `$d`（由 `ls` 輸出），可能包含 shell 特殊字元（如 `;`、`$(...)`），導致任意指令注入。例如 repo 名稱為 `x; rm -rf ~` 時，`eval` 會執行 `rm -rf ~`。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 以引號包裹。

**判斷依據**：diff 第 52 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 路徑解析脆弱：ls 輸出未處理特殊字元</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白、換行或 glob 字元（如 `*`），會導致路徑解析錯誤或意外展開。例如目錄名為 `my repo` 會被拆成兩個 token。

建議改用 glob 或 `find`：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
```

**判斷依據**：diff 第 68 行：`for d in $(ls "$ROOT"); do`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> 錯誤處理不足：git checkout 失敗仍繼續執行</summary>

`git checkout $BRANCH` 失敗時（例如 branch 不存在），腳本仍會繼續執行 `git merge` 與後續步驟，可能導致錯誤的同步結果或資料庫寫入不正確的資料。

建議在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo：
```bash
git checkout "$BRANCH" 2>>"$LOG" || { echo "checkout failed for $name" >> "$LOG"; return 1; }
```

**判斷依據**：diff 第 32 行：`git checkout $BRANCH 2>>"$LOG"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能失敗但未處理</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `origin/$BRANCH` 不存在或 rev-list 失敗，`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入的 `ahead` 為空值可能導致資料型別不符。

建議檢查 `ahead` 是否為數字，失敗時設為 0 或記錄錯誤。

**判斷依據**：diff 第 36 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2530 (cache hit 1408) ｜ completion tokens 1427 ｜ PR #13</sub>