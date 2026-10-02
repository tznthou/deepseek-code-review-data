<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個批次同步多個 Git repo 的 bash 腳本，並將結果寫入 SQLite 供報表使用。主要風險集中在 shell 注入（SQLite 與 eval）、錯誤處理不足（git 指令失敗仍繼續執行）、以及路徑處理不嚴謹（ls 解析、rm -rf 使用）。最優先應修補 SQL 注入與 eval 的使用，並加入 git 指令的錯誤檢查。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/repo_sync.sh:47` | SQLite 指令存在 SQL 注入風險 | 0.95 |
| 🛑 | Blocker | `sandbox/repo_sync.sh:56` | eval 執行未受信任的 hook 路徑 | 0.90 |
| ⚠️ | Major | `sandbox/repo_sync.sh:34` | git 指令失敗未中止，可能造成錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/repo_sync.sh:62` | rm -rf 使用未加防護的 glob | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:41` | ahead 計算可能因 rev-list 失敗而為空 | 0.80 |
| ⚠️ | Major | `sandbox/repo_sync.sh:87` | 使用 ls 解析目錄列表，路徑含空白或換行會出錯 | 0.75 |
| 🔸 | Minor | `sandbox/repo_sync.sh:95` | run_hook 的參數傳遞可能不正確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:47</code> SQLite 指令存在 SQL 注入風險</summary>

`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自 repo 目錄名稱，攻擊者可以建立包含單引號的目錄名稱（例如 `x'); DROP TABLE runs;--`），導致任意 SQL 執行。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少對輸入進行單引號轉義。

**判斷依據**：第 43 行直接將變數嵌入 SQL 字串，且 `$name` 未經任何驗證或轉義。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/repo_sync.sh:56</code> eval 執行未受信任的 hook 路徑</summary>

`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。`$hook` 路徑由 `$ROOT` 決定，而 `$ROOT` 是使用者提供的參數；若攻擊者能控制 `$ROOT`（例如誘使使用者指向惡意目錄），即可注入任意指令。即使 `$hook` 檔案存在且可執行，`$repo` 也可能包含特殊字元（如空白、分號）造成意外行為。建議直接執行 `"$hook" "$repo"`，不要使用 eval。

**判斷依據**：第 55 行使用 eval 執行字串，且變數內容未受完整控制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:34</code> git 指令失敗未中止，可能造成錯誤結果</summary>

`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但腳本仍繼續執行後續步驟。例如 checkout 失敗時，`git merge` 可能基於錯誤的分支執行，或 `ahead` 計算出錯。建議在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo。

**判斷依據**：第 31-33 行未檢查 git 指令的 exit code。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:62</code> rm -rf 使用未加防護的 glob</summary>

`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或未設定，可能變成 `rm -rf /.cache/*`，造成系統檔案刪除。此外，若 `.cache` 目錄不存在，glob 不會展開，指令會嘗試刪除名為 `*` 的檔案，通常無害但可能誤刪。建議先檢查 `$ROOT` 非空且 `.cache` 存在，或使用 `find` 搭配更嚴格的條件。

**判斷依據**：第 61 行直接使用 rm -rf 搭配變數路徑與 glob，缺乏防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:41</code> ahead 計算可能因 rev-list 失敗而為空</summary>

`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQLite 插入時 `$ahead` 為空可能導致錯誤。建議檢查 rev-list 的 exit code，失敗時設定預設值或跳過。

**判斷依據**：第 36 行未檢查 rev-list 的執行結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/repo_sync.sh:87</code> 使用 ls 解析目錄列表，路徑含空白或換行會出錯</summary>

`for d in $(ls "$ROOT")` 依賴 ls 的輸出以空白分隔，若 repo 目錄名稱包含空白、換行或特殊字元，迴圈會錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

**判斷依據**：第 70 行使用 ls 輸出進行迴圈，未處理特殊字元。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/repo_sync.sh:95</code> run_hook 的參數傳遞可能不正確</summary>

`run_hook "$d"` 傳入的是 repo 的 basename，但 hook 可能需要完整路徑。此外，`run_hook` 內部的 `$repo` 參數未加引號，若名稱含空白會出錯。建議傳入完整路徑並在 hook 執行時正確引用。

**判斷依據**：第 78 行傳入 basename，且 run_hook 內未正確引用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2642 (cache hit 2560) ｜ completion tokens 1749 ｜ PR #13</sub>