<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 沒有檢查 `git log` 的回傳碼，可能把錯誤輸出當成正常結果；`list_tags` 在只有一個符合條件的 tag 時會因 `tags.index(tag) - 1` 變成 -1 而選到最後一個 tag；`max_items` 對負數或零沒有防護，可能讓公告內容為空。另外，`post` 沒有驗證 webhook URL 的 scheme，且錯誤訊息可能洩漏 URL。建議先修正這幾個正確性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成 commit 列表 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個符合條件的 tag 時，`prev` 會選到最後一個 tag 而非前一個 | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:111` | `max_items` 可能為負數或零，導致公告內容為空 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成 commit 列表</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 處理。建議加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個符合條件的 tag 時，`prev` 會選到最後一個 tag 而非前一個</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag。例如 repo 只有 `v1.0.0` 和 `v2.0.0`，執行 `release_notes.py repo v1.0.0` 時，`prev` 會是 `v2.0.0`，導致 `git log v2.0.0..v1.0.0` 回傳空結果或錯誤。建議先檢查 `tags.index(tag) == 0` 並處理沒有前一個 tag 的情況。

**判斷依據**：diff 中直接使用 `tags.index(tag) - 1`，沒有處理索引為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:111</code> `max_items` 可能為負數或零，導致公告內容為空</summary>

`max_items()` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。如果設定為負數或 0，`commits[: max_items()]` 會是空列表，`render` 會產生只有標題的公告。建議在 `max_items` 中檢查數值必須大於 0，否則使用預設值。

**判斷依據**：diff 中 `max_items` 只處理了 `ValueError`，沒有檢查轉換後的數值是否為正數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求</summary>

`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `https`。如果環境變數被設定為 `file://` 或 `http://`，可能導致讀取本地檔案或將資料傳送到非加密的端點。建議驗證 URL 的 scheme 必須是 `https`，並考慮使用 `urllib.parse.urlparse` 檢查。

**判斷依據**：diff 中 `url` 直接來自環境變數 `NOTES_WEBHOOK`，沒有進行 scheme 驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1239 ｜ PR #14</sub>