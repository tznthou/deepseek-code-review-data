<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite。主要風險在於 SQL 注入（repo 名稱與 branch 未經參數化）、`eval` 執行未受信任的 hook 路徑、以及多個錯誤處理與可移植性問題。最優先應修復 SQL 注入與 `eval` 的使用，並補上錯誤檢查與測試。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQL 注入：repo 名稱與 branch 未經參數化直接插入 SQL | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | 使用 `eval` 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:37` | `git checkout` 與 `git merge` 失敗時未中止，可能導致錯誤資料寫入 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | `ahead` 可能為空字串，導致 SQL 語法錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難 | 0.75 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 `ls` 解析目錄列表，檔名含空格或換行時會出錯 | 0.70 |
| 🔸 | Minor | `sandbox/repo_sync.sh:88` | `local` 在函式外使用，非 POSIX 標準 | 0.60 |
| 🔸 | Minor | `sandbox/repo_sync.sh:68` | `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `\|\| total=0` 處理 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQL 注入：repo 名稱與 branch 未經參數化直接插入 SQL</summary>

`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `'; DROP TABLE runs; --`），將導致 SQL 注入，可能破壞資料庫或執行任意 SQL。

**失敗情境**：假設 `$ROOT` 下有一個名為 `evil'; DROP TABLE runs; --` 的目錄，執行腳本後 `runs` 表將被刪除。

**建議修法**：使用 `sqlite3` 的參數綁定功能，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行單引號轉義（但參數綁定更安全）。

**判斷依據**：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> 使用 `eval` 執行未受信任的 hook 路徑</summary>

`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 來自 `$ROOT/.hooks/post-sync`，而 `$ROOT` 是使用者提供的參數。若攻擊者能控制 `$ROOT` 的內容（例如提供一個包含惡意 `.hooks/post-sync` 的目錄），則可注入任意命令。

**失敗情境**：假設 `$ROOT/.hooks/post-sync` 內容為 `echo pwned; rm -rf /`，執行時將造成嚴重破壞。

**建議修法**：直接執行 hook 檔案，不要使用 `eval`：
```bash
"$hook" "$repo"
```
並確保 hook 檔案權限正確（僅可執行，不可寫）。

**判斷依據**：diff 第 51 行：`eval "$hook $repo"`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:37</code> `git checkout` 與 `git merge` 失敗時未中止，可能導致錯誤資料寫入</summary>

`sync_one` 中 `git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"` 的錯誤僅被重導向至 log，未檢查退出碼。若 checkout 或 merge 失敗（例如 branch 不存在、有衝突），腳本仍會繼續執行，並將錯誤的 `ahead` 值寫入資料庫。

**失敗情境**：若 `$BRANCH` 不存在於 remote，`git checkout` 失敗，但 `ahead` 可能被計算為 0 或非預期值，導致報表資料錯誤。

**建議修法**：在每個 git 指令後檢查退出碼，失敗時記錄錯誤並跳過該 repo 或中止。

**判斷依據**：diff 第 36-37 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> `ahead` 可能為空字串，導致 SQL 語法錯誤</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `sqlite3` 指令中的 `$ahead` 會使 SQL 語句變成 `..., , datetime('now'))`，導致語法錯誤。

**失敗情境**：若 `origin/$BRANCH` 不存在，`git rev-list` 回傳非零，`ahead` 為空，SQL 插入失敗。

**建議修法**：檢查 `git rev-list` 的退出碼，失敗時設定 `ahead=0` 或跳過寫入。

**判斷依據**：diff 第 40 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> `cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難</summary>

`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 為空字串或未定義，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。雖然 `main` 有檢查 `$BRANCH`，但未檢查 `$ROOT` 是否為空。

**失敗情境**：使用者未提供第一個參數，`$ROOT` 為空，腳本將嘗試刪除 `/.cache/*`。

**建議修法**：在 `main` 中檢查 `$ROOT` 是否為空，並確保 `$ROOT` 是絕對路徑且存在。

**判斷依據**：diff 第 58 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 `ls` 解析目錄列表，檔名含空格或換行時會出錯</summary>

`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或特殊字元，將被錯誤分割。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，迴圈會將其視為兩個項目 `my` 和 `repo`，導致路徑錯誤。

**建議修法**：使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 迴圈。

**判斷依據**：diff 第 70 行

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:88</code> `local` 在函式外使用，非 POSIX 標準</summary>

`main` 函式中的 `local target="$ROOT/$d"` 使用了 `local`，但 `local` 並非 POSIX 標準，某些 shell（如 dash）可能不支援。腳本 shebang 為 `#!/usr/bin/env bash`，因此實際使用 bash 執行，但若環境中 bash 路徑不同或使用者以 sh 執行，可能出錯。

**建議修法**：移除 `local` 或改用其他方式（例如直接賦值）。

**判斷依據**：diff 第 72 行

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:68</code> `summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `|| total=0` 處理</summary>

`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `$LOG` 不存在時 `grep` 回傳非零，`total` 會被設為 0，但 `grep` 的錯誤訊息已被重導向，因此不會顯示。此寫法可接受，但可讀性較差。

**建議修法**：可改用 `[ -f "$LOG" ] && total=$(wc -l < "$LOG") || total=0`。

**判斷依據**：diff 第 64 行

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2642 (cache hit 896) ｜ completion tokens 2384 ｜ PR #13</sub>