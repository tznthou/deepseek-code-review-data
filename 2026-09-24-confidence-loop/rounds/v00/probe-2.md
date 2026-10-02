<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，主要功能是從 git 歷史中整理兩個 tag 之間的 commit，並透過 webhook 發佈。整體結構清晰，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，可能導致在 repo 路徑無效時產生誤導性的輸出；另外 `max_items` 對負數或零的處理可能造成意外行為；`post` 函式在 webhook 回傳非 2xx 狀態碼時仍回報成功；`load_config` 對 JSON 型別沒有驗證，可能導致後續程式碼出錯。建議優先修正 `commits_between` 的錯誤處理。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `commits_between` 未檢查 `git log` 的執行結果 | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `max_items` 未處理負數或零 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | `post` 未處理非 2xx 狀態碼 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | `load_config` 未驗證 JSON 型別 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `commits_between` 未檢查 `git log` 的執行結果</summary>

`subprocess.run` 沒有設定 `check=True`，且回傳的 `proc.returncode` 沒有被檢查。如果 `repo` 路徑不是有效的 git 儲存庫，`git log` 會失敗並在 stderr 輸出錯誤，但函式仍會回傳空列表，導致 `main` 印出「之間沒有新 commit」的誤導訊息。

建議：加上 `check=True`，或在函式內檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式呼叫 `subprocess.run` 時沒有 `check=True`，且後續沒有檢查 `proc.returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `max_items` 未處理負數或零</summary>

`int(raw)` 可以成功解析負數或零，但 `commits[: max_items()]` 在 `max_items()` 回傳負數時會得到空列表（因為切片從尾端倒數），回傳 0 時也會得到空列表，導致後續 `group` 收到空列表，最終產生沒有內容的公告。

建議：在 `max_items` 中檢查數值必須大於 0，否則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 只處理了 `ValueError`，沒有檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> `post` 未處理非 2xx 狀態碼</summary>

`urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 4xx、5xx）時會拋出 `urllib.error.HTTPError`，但 `HTTPError` 是 `URLError` 的子類別，因此會被捕捉並記錄錯誤，但函式回傳 `False`。然而，如果伺服器回傳 3xx 且 `urlopen` 自動跟隨重定向，最終狀態碼可能不是 2xx，但函式仍會回傳 `True`。

建議：明確檢查 `resp.status` 是否在 200-299 範圍，否則記錄錯誤並回傳 `False`。

**判斷依據**：diff 中 `post` 函式只檢查了狀態碼範圍，但未處理重定向後的非 2xx 情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> `load_config` 未驗證 JSON 型別</summary>

`json.load` 可能回傳任何 JSON 型別（例如 list、string、number），但後續程式碼假設它是 dict（例如 `cfg.get('title', ...)`）。如果設定檔內容是 `[]` 或 `"abc"`，會拋出 `AttributeError`。

建議：在 `load_config` 中檢查 `isinstance(data, dict)`，否則拋出錯誤或回傳空 dict。

**判斷依據**：diff 中 `load_config` 直接回傳 `json.load` 的結果，沒有型別檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 1266 ｜ PR #14</sub>