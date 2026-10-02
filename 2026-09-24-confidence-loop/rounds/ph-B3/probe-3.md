<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於 `commits_between` 未檢查子程序失敗，可能導致後續索引錯誤；`list_tags` 在 tag 清單為空時會因索引 -1 而取到最後一個元素，造成錯誤的 prev tag；`max_items` 對負數或非整數輸入處理不完整；webhook URL 未驗證 scheme，可能造成 SSRF；以及 `post` 函式未檢查 HTTP 狀態碼，可能誤報成功。建議優先修正子程序錯誤處理與 tag 清單邊界。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 子程序失敗未檢查，可能導致後續 IndexError | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 清單為空時，prev 會取到最後一個元素而非第一個 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:37` | NOTES_MAX 負數或非整數處理不完整 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能造成 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | HTTP 狀態碼未檢查，可能誤報成功 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 子程序失敗未檢查，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑無效、權限不足或 git 本身錯誤而失敗，`proc.stdout` 可能為空字串，後續 `commits[0][0]` 會拋出 `IndexError`，程式直接崩潰且無明確錯誤訊息。建議加上 `check=True` 或檢查 `returncode`，並在失敗時記錄錯誤並回傳非零 exit code。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中直接使用 `commits[0][0]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 清單為空時，prev 會取到最後一個元素而非第一個</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tags` 為空時，`tags.index(tag)` 會拋出 `ValueError`，但若 `tags` 非空且 `tag` 位於第一個位置，`tags.index(tag) - 1` 會是 -1，取到最後一個 tag，而非前一個版本。這會導致 release notes 範圍錯誤。建議先檢查 `tags.index(tag) > 0`，否則回報錯誤。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未處理邊界。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:37</code> NOTES_MAX 負數或非整數處理不完整</summary>

`max_items` 只處理 `ValueError`，但若 `NOTES_MAX` 設為負數，`int(raw)` 會成功，回傳負數，導致 `commits[: max_items()]` 切片行為異常（可能回傳空列表）。建議檢查數值是否為正整數，否則回退預設值。

**判斷依據**：diff 中 `max_items` 函式未檢查轉換後的數值是否為正整數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能造成 SSRF</summary>

`post` 函式直接使用 `urllib.request.urlopen` 開啟使用者提供的 URL，未限制 scheme 為 `https`。攻擊者若控制 `NOTES_WEBHOOK` 環境變數，可指定 `file://` 或 `gopher://` 等 scheme，讀取本機檔案或進行內網探測。建議驗證 URL 的 scheme 必須為 `https` 或 `http`（若允許），並考慮使用白名單。

**判斷依據**：diff 中 `post` 函式未對 `url` 進行 scheme 驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> HTTP 狀態碼未檢查，可能誤報成功</summary>

`post` 函式僅檢查 `resp.status` 是否在 200-299 之間，但 `urllib.request.urlopen` 對 4xx/5xx 回應會拋出 `HTTPError`，該例外是 `URLError` 的子類別，會被捕捉並記錄錯誤，但函式回傳 `False`。然而，若伺服器回傳 3xx 且未自動跟隨重定向，`urlopen` 可能拋出 `HTTPError`，同樣被捕捉。但若伺服器回傳 2xx 以外的狀態碼且未拋出例外（例如某些自訂 handler），則可能回傳 `True`。建議明確檢查 `resp.status` 並處理非 2xx 情況。

**判斷依據**：diff 中 `post` 函式依賴 `urlopen` 的例外行為，未明確處理所有非 2xx 狀態。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1494 ｜ PR #14</sub>