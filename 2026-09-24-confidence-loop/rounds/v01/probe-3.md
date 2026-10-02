<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，功能是從 git 歷史中擷取兩個 tag 之間的 commit，分類後貼到團隊頻道的 webhook。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，可能導致後續程式碼在錯誤的資料上運作；另外 `max_items` 沒有處理負數或零，可能造成輸出異常；`load_config` 沒有驗證 JSON 內容型別，可能導致執行期錯誤。建議先修正這些問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `commits_between` 未檢查 `git log` 的執行結果 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:33` | `max_items` 未處理負數或零 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | `load_config` 未驗證 JSON 內容型別 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `commits_between` 未檢查 `git log` 的執行結果</summary>

`subprocess.run` 沒有設定 `check=True`，且回傳的 `proc.returncode` 沒有被檢查。如果 `git log` 因為任何原因失敗（例如 repo 路徑錯誤、git 版本不支援 `--format` 參數、或權限不足），`proc.stdout` 會是空字串，函式會回傳空 list，導致後續流程誤以為沒有 commit 而提前結束，或產生不完整的 release notes。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 時沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:33</code> `max_items` 未處理負數或零</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有驗證其值是否為正數。如果設定為負數或零，`commits[: max_items()]` 會產生空 list 或意外的切片結果（例如 `commits[:-1]` 會排除最後一個 commit），導致 release notes 內容不正確。

建議：在轉換後檢查數值是否大於 0，否則使用預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的整數是否為正數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> `load_config` 未驗證 JSON 內容型別</summary>

`load_config` 直接回傳 `json.load` 的結果，沒有檢查其型別是否為 dict。如果設定檔內容是 list、字串或數字，後續 `cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

建議：在回傳前檢查 `isinstance(data, dict)`，否則拋出錯誤或回傳空 dict。

**判斷依據**：diff 中 `load_config` 函式直接回傳 `json.load` 的結果，沒有型別檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3917 (cache hit 3840) ｜ completion tokens 976 ｜ PR #14</sub>