<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於錯誤處理不完整：`commits_between` 未檢查 git 指令的失敗，可能導致後續以空清單或錯誤資料繼續執行；`load_config` 只處理 JSON 解析錯誤，其他檔案讀取錯誤會直接崩潰；`post` 未處理 HTTP 錯誤狀態碼，可能誤報成功。此外，`max_items` 對負數或零的輸入未做下限檢查，可能造成切片行為異常。整體而言，功能完整但需加強錯誤處理與輸入驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續處理錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:34` | load_config 未處理 JSON 以外的檔案讀取錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:94` | post 未處理 HTTP 錯誤狀態碼，可能誤報成功 | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | max_items 未限制 NOTES_MAX 的下限，可能導致切片行為異常 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續處理錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空或包含錯誤訊息，函式仍會回傳空清單或解析出錯誤的 commit 資料。建議加上 `check=True` 或明確檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且未設定 `check=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:34</code> load_config 未處理 JSON 以外的檔案讀取錯誤</summary>

`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案存在但無法讀取（例如權限不足、I/O 錯誤），會拋出未處理的 `OSError` 導致程式崩潰。建議捕捉 `OSError` 並記錄警告後回傳空 dict，或讓錯誤向上傳播並在 main 中處理。

**判斷依據**：diff 中 `load_config` 的 except 子句僅涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`，未涵蓋其他可能的 `OSError`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:94</code> post 未處理 HTTP 錯誤狀態碼，可能誤報成功</summary>

`post` 僅在 `urllib.error.URLError` 時回傳 False，但若伺服器回傳 4xx/5xx 狀態碼，`urlopen` 會拋出 `urllib.error.HTTPError`（為 `URLError` 子類別），因此會被捕捉並回傳 False。然而，若伺服器回傳 3xx 重定向，`urlopen` 預設會自動跟隨，最終可能得到 2xx 或拋出例外。但若伺服器回傳 204 No Content，`resp.status` 為 204，符合 `200 <= resp.status < 300`，回傳 True，但實際上可能未成功處理。建議明確檢查 `resp.status` 是否為 2xx，並考慮處理非 2xx 的 HTTP 狀態碼。

**判斷依據**：diff 中 `post` 函式僅依賴 `urlopen` 的例外處理，未明確處理 HTTP 狀態碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> max_items 未限制 NOTES_MAX 的下限，可能導致切片行為異常</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為 0 或負數，`commits[: max_items()]` 會回傳空清單或錯誤切片，導致公告內容不完整或程式錯誤。建議加上下限檢查，例如 `max(1, int(raw))` 或明確拒絕非正整數。

**判斷依據**：diff 中 `max_items` 僅處理 ValueError，未檢查轉換後的數值是否為正整數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 1408) ｜ completion tokens 1275 ｜ PR #14</sub>