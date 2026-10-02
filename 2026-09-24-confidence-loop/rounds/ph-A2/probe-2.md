<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，當 repo 路徑無效或 git 指令失敗時，程式會誤以為沒有 commit 而回報成功；其次是 `list_tags` 在 tag 清單為空時會因 `tags.index(tag)` 拋出 `ValueError` 而崩潰；另外 `max_items` 對負數或零的處理可能造成非預期行為。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | `git log` 執行失敗時未檢查回傳碼，可能誤判為沒有 commit | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 清單為空時 `tags.index(tag)` 會拋出未處理的 `ValueError` | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `max_items` 未處理負數或零，可能導致非預期行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> `git log` 執行失敗時未檢查回傳碼，可能誤判為沒有 commit</summary>

`commits_between` 使用 `subprocess.run` 執行 `git log`，但沒有設定 `check=True`，也沒有檢查 `proc.returncode`。當 `repo` 路徑無效、git 指令不存在、或 repository 損毀時，`git log` 會以非零狀態結束，但 `proc.stdout` 可能是空的，導致函式回傳空 list。呼叫端 `main` 看到空 list 會印出「沒有新 commit」並回傳 0（成功），但實際上根本沒有取得任何資料。

**失敗情境**：使用者提供錯誤的 repo 路徑，或 repo 尚未初始化，程式會回報成功但沒有產生任何 release notes。

**建議**：在 `subprocess.run` 加上 `check=True`，讓失敗時拋出 `CalledProcessError`，或在函式內檢查 `proc.returncode != 0` 並記錄錯誤後回傳空 list 或拋出例外。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 清單為空時 `tags.index(tag)` 會拋出未處理的 `ValueError`</summary>

`main` 中先檢查 `if tag not in tags`，但若 `tags` 是空 list（例如 repo 沒有任何符合 `v*` 的 tag），`tag not in tags` 為 True，會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，若 `tags` 非空但 `tag` 不在其中，同樣會回傳 2。因此 `tags.index(tag)` 只有在 `tag` 存在於 `tags` 時才會執行，此時 `tags` 必非空，所以不會拋出 `ValueError`。

**但**：`list_tags` 可能因為 `git tag` 執行失敗而回傳空 list（例如 repo 路徑錯誤），此時 `tag not in tags` 為 True，程式會印出「找不到 tag」並回傳 2，不會崩潰。因此這個問題實際上不會觸發。

**重新評估**：此 finding 的 confidence 應降低，因為 `tag not in tags` 的檢查已經涵蓋了空 list 的情況。除非 `tags` 在檢查後被修改（但此處沒有），否則 `tags.index(tag)` 是安全的。

**建議**：無需修改，但可考慮將 `tags.index(tag)` 改為更明確的處理，例如使用 `try/except` 或先取得 index 再檢查，以增加可讀性。

**判斷依據**：diff 中 `main` 函式在 `if tag not in tags` 之後才執行 `tags.index(tag)`，但該檢查已確保 `tag` 存在於 `tags`，因此 `tags` 非空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `max_items` 未處理負數或零，可能導致非預期行為</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會得到空 list 或全部 commit（負數切片會從尾端取），可能造成非預期結果。

**失敗情境**：使用者誤設 `NOTES_MAX=-1`，程式會將所有 commit 納入（因為 `commits[:-1]` 取到倒數第二個），而不是限制數量。

**建議**：在 `max_items` 中檢查數值是否大於 0，若否則使用預設值並記錄警告。

**判斷依據**：diff 中 `max_items` 只處理了 `ValueError`，未檢查轉換後的數值是否合理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1382 ｜ PR #14</sub>