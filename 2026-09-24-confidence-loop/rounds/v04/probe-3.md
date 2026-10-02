<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的失敗，可能導致後續程式碼在錯誤的資料上執行；另外 `load_config` 對 JSON 型別沒有驗證，若設定檔不是物件會造成執行期錯誤；`max_items` 對負數或非整數的處理也不夠嚴謹。建議先修正這些問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | `commits_between` 未檢查 `git log` 的失敗 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:30` | `load_config` 未驗證 JSON 頂層型別 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `max_items` 未處理負數或非整數值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> `commits_between` 未檢查 `git log` 的失敗</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 失敗時（例如 repo 路徑無效、git 指令不存在、或 `prev..tag` 範圍無效），`proc.returncode` 非零但程式不會拋出例外。後續程式碼會繼續執行，並把 `proc.stdout`（可能是空字串或錯誤訊息）當成正常輸出處理，導致產生錯誤的 release notes 或誤報成功。

建議加上 `check=True`，讓失敗時拋出 `subprocess.CalledProcessError`，由呼叫端處理或讓程式直接失敗。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且回傳值 `proc` 的 `returncode` 未被檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:30</code> `load_config` 未驗證 JSON 頂層型別</summary>

`load_config` 直接回傳 `json.load` 的結果，但沒有檢查它是否為 dict。如果 `.release-notes.json` 的內容是陣列、字串或數字，`cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

建議在 `json.load` 後檢查 `isinstance(data, dict)`，若不是則拋出明確的錯誤訊息。

**判斷依據**：diff 中 `load_config` 函式直接回傳 `json.load(fh)` 的結果，沒有型別檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `max_items` 未處理負數或非整數值</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉成整數，但沒有檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，導致截斷錯誤。另外，若值為 `0`，會回傳空列表，可能不是預期行為。

建議加上檢查，確保值為正整數，否則使用預設值。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 968 ｜ PR #14</sub>