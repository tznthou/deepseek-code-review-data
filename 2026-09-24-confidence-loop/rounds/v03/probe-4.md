<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並貼到 webhook。整體結構清楚，但有三個問題需要處理：`commits_between` 沒有檢查 `git log` 的失敗，可能導致後續在空列表上取 `[0]` 而崩潰；`max_items()` 對負數或零沒有防護，會讓公告內容變成空字串或漏掉全部項目；`post()` 只處理 `URLError`，HTTP 錯誤（如 4xx/5xx）會被當成成功。建議先修正這三點再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，後續可能 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 設為負數或零時會產生空公告或漏掉全部 commit | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:96` | post() 未處理 HTTP 錯誤狀態碼 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，後續可能 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空列表。接著在 `main()` 中 `commits[0][0]` 會拋出 `IndexError`，程式直接崩潰。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時記錄錯誤並回傳空列表或拋出例外。

**判斷依據**：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `main()` 第 103 行直接使用 `commits[0][0]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 設為負數或零時會產生空公告或漏掉全部 commit</summary>

`max_items()` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否大於 0。若使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會變成空列表或全部被截斷，導致公告內容空白或遺漏。建議在轉換後檢查數值，若小於 1 則記錄警告並使用預設值。

**判斷依據**：diff 中 `max_items()` 沒有對轉換後的整數做範圍檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:96</code> post() 未處理 HTTP 錯誤狀態碼</summary>

`post()` 只捕捉 `urllib.error.URLError`，但 `urlopen` 在收到 4xx/5xx 回應時會拋出 `urllib.error.HTTPError`（它是 `URLError` 的子類別，所以會被捕捉），然而程式碼在 `except` 區塊中記錄錯誤並回傳 `False`，這部分正確。但若伺服器回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能回傳 200，這部分沒問題。真正的問題是：如果伺服器回傳 204 No Content，`resp.status` 是 204，條件 `200 <= resp.status < 300` 成立，回傳 `True`，但實際上 webhook 可能沒有處理。不過這屬於邊緣情況，影響不大。建議明確處理 `HTTPError` 並記錄狀態碼，或至少確認非 2xx 都視為失敗。

**判斷依據**：diff 中 `post()` 的例外處理只捕捉 `URLError`，但 `HTTPError` 是子類別，會被捕捉，但沒有特別記錄狀態碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3863 (cache hit 3840) ｜ completion tokens 1100 ｜ PR #14</sub>