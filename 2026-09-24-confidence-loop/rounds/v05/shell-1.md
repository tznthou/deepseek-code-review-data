<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入、命令注入（eval）、路徑處理不當、錯誤處理不足，以及併發與效能問題。最優先應修復 SQL 注入與 eval 的使用，並改善錯誤處理與日誌記錄。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入風險：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | 路徑處理不當：cleanup_cache 使用未加引號的 glob，可能誤刪檔案 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | 錯誤處理不足：git 指令失敗仍繼續執行，可能導致資料不一致 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | 變數未初始化：ahead 可能為空，導致數值比較錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 迴圈中使用 ls 解析目錄，可能因檔名包含換行或空格而失敗 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:12` | 缺少併發控制：多個實例同時執行可能互相干擾 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | 效能問題：summarize 使用 grep -c 計算行數，可能讀取整個檔案 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句</summary>

`$name` 與 `$BRANCH` 直接拼接進 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'; DROP TABLE runs; --` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：第 42 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入風險：eval 執行未受信任的 hook 路徑與參數</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$ROOT` 或 repo 名稱包含惡意內容（例如 `; rm -rf ~`），將導致任意命令執行。

建議避免使用 eval，改用直接執行並正確引用變數：
```bash
"$hook" "$repo"
```

**判斷依據**：第 52 行使用 eval 執行字串，變數未經安全處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> 路徑處理不當：cleanup_cache 使用未加引號的 glob，可能誤刪檔案</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 包含空格或特殊字元，glob 可能展開成多個參數，導致刪除非預期的檔案。此外，若 `.cache` 不存在，`rm` 會報錯但腳本仍繼續執行。

建議先檢查目錄是否存在，並正確引用：
```bash
if [ -d "$ROOT/.cache" ]; then
  rm -rf "$ROOT/.cache"/*
fi
```

**判斷依據**：第 58 行 glob 未加引號，且未檢查目錄存在性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> 錯誤處理不足：git 指令失敗仍繼續執行，可能導致資料不一致</summary>

`git fetch`、`git checkout`、`git merge` 的失敗僅被重導向至日誌，腳本仍繼續執行後續步驟。例如 checkout 失敗時，`git merge` 可能基於錯誤的 branch 執行，導致錯誤的同步結果。

建議在每個 git 指令後檢查退出碼，失敗時中止該 repo 的處理並記錄錯誤。

**判斷依據**：第 33-35 行未檢查 git 指令的退出碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> 變數未初始化：ahead 可能為空，導致數值比較錯誤</summary>

若 `git rev-list --count` 失敗（例如 branch 不存在），`ahead` 會是空字串，後續的 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗。

建議在取得 ahead 後檢查是否為數字，或提供預設值：
```bash
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null) || ahead=0
```

**判斷依據**：第 39 行未處理指令失敗時 ahead 為空的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 迴圈中使用 ls 解析目錄，可能因檔名包含換行或空格而失敗</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若目錄名稱包含空格或換行，將導致錯誤。

建議改用 glob 或 find：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

**判斷依據**：第 76 行使用 ls 輸出進行迴圈，未正確處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:12</code> 缺少併發控制：多個實例同時執行可能互相干擾</summary>

腳本使用固定的 DB 與 LOG 路徑（/tmp/repo_sync.db、/tmp/repo_sync.log），若同時執行多個實例，會互相覆寫資料或日誌。

建議使用 lock 檔案或將輸出路徑改為基於 PID 或時間戳的暫存檔。

**判斷依據**：第 13-14 行使用固定路徑，未考慮併發執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> 效能問題：summarize 使用 grep -c 計算行數，可能讀取整個檔案</summary>

`grep -c . "$LOG"` 會讀取整個日誌檔來計算行數，若日誌很大可能影響效能。

建議改用 `wc -l < "$LOG"` 來取得行數。

**判斷依據**：第 64 行使用 grep -c 計算行數，效率較低。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 1915 ｜ PR #13</sub>