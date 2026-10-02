<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並發送到 webhook。主要風險在於錯誤處理不完整：commits_between 沒有檢查 git log 的失敗、post 沒有處理 HTTP 錯誤狀態碼、max_items 沒有處理負數或過大的值。此外，程式碼中沒有明顯的安全漏洞，但 webhook URL 來自環境變數，需確保其可信。建議先修正錯誤處理，再考慮合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | commits_between 未檢查 git log 的失敗 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:96` | post 未處理 HTTP 錯誤狀態碼 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | max_items 未驗證範圍 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:50` | list_tags 未處理 git tag 失敗 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> commits_between 未檢查 git log 的失敗</summary>

`subprocess.run` 沒有設定 `check=True`，如果 `git log` 失敗（例如 repo 路徑不正確、git 指令不存在），`proc.returncode` 非零但程式不會拋出例外，而是繼續處理空的 `stdout`，導致後續邏輯誤判為沒有 commit。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:96</code> post 未處理 HTTP 錯誤狀態碼</summary>

`urllib.request.urlopen` 在 HTTP 回應狀態碼非 2xx 時會拋出 `urllib.error.HTTPError`，但目前的 `except` 只捕捉 `urllib.error.URLError`。`HTTPError` 是 `URLError` 的子類別，所以會被捕捉，但函式會回傳 `False`，導致呼叫端誤以為發送失敗。建議明確處理 `HTTPError`，並根據狀態碼決定是否重試或記錄更詳細的錯誤。

**判斷依據**：diff 中 `except` 捕捉 `URLError`，但 `HTTPError` 是其子類別，且函式回傳 `False` 表示失敗，但實際上可能只是回應狀態碼非 2xx。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> max_items 未驗證範圍</summary>

`NOTES_MAX` 環境變數轉成整數後沒有檢查是否為負數或過大。負數會導致 `commits[: max_items()]` 切片行為異常（例如 `commits[:-1]` 會排除最後一個元素），過大的值可能導致記憶體問題。建議加上範圍檢查，例如限制在 1 到某個合理上限。

**判斷依據**：diff 中 `int(raw)` 沒有範圍驗證，且後續使用 `commits[: max_items()]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:50</code> list_tags 未處理 git tag 失敗</summary>

`subprocess.run` 設定了 `check=True`，所以失敗會拋出例外，但 `main` 中沒有捕捉，導致程式直接崩潰。建議在 `main` 中捕捉 `subprocess.CalledProcessError` 並回傳錯誤碼。

**判斷依據**：diff 中 `check=True` 會拋出例外，但 `main` 沒有 try-except 處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1134 ｜ PR #14</sub>