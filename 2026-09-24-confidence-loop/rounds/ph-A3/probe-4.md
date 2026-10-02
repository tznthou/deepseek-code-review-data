<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，分組後貼到團隊頻道的 webhook。主要風險在於錯誤處理與輸入驗證：commits_between 沒有檢查 git log 的失敗，可能導致後續索引錯誤；max_items 對負數或超大值沒有設限，可能造成輸出異常；webhook URL 未驗證 scheme，可能被用來打內網服務。建議先修正這三個問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能導致後續 IndexError | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:45` | NOTES_MAX 未限制範圍，負值或超大值可能造成異常 | 0.70 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:33` | load_config 只處理 FileNotFoundError 和 JSONDecodeError，其他例外會直接 crash | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空 list。接著在 `main` 中 `commits[0][0]` 會拋出 `IndexError`，程式直接 crash。建議加上 `check=True`，或在呼叫後檢查 `proc.returncode` 並處理錯誤。

**判斷依據**：diff 中 `commits_between` 的 `subprocess.run` 沒有 `check=True`，且 `main` 中 `latest = commits[0][0]` 直接索引第一個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:45</code> NOTES_MAX 未限制範圍，負值或超大值可能造成異常</summary>

`max_items` 只檢查是否能轉成整數，沒有檢查範圍。如果使用者設定 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個以外的所有 commit，可能不是預期行為；如果設定超大值（例如 10^9），雖然切片本身不會出錯，但後續 render 可能產生極大的字串，造成記憶體壓力。建議加上範圍檢查（例如 1 到某個合理上限）。

**判斷依據**：diff 中 `max_items` 直接回傳 `int(raw)`，沒有範圍驗證；`main` 中使用 `commits[: max_items()]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，沒有檢查 scheme。如果攻擊者能控制這個環境變數（例如透過 CI 設定），可以指定 `file:///etc/passwd` 或 `http://169.254.169.254/...` 等，導致讀取本機檔案或打內網服務。建議限制 scheme 為 `https`（或至少 `http` 和 `https`），並考慮阻擋內網 IP。

**判斷依據**：diff 中 `post` 直接使用 `url` 參數，沒有驗證 scheme；`url` 來自環境變數 `NOTES_WEBHOOK`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:33</code> load_config 只處理 FileNotFoundError 和 JSONDecodeError，其他例外會直接 crash</summary>

`load_config` 開啟檔案時可能拋出 `PermissionError`、`IsADirectoryError` 等，這些沒有被捕捉，會讓程式直接 crash。雖然設定檔是選配的，但若檔案存在卻無法讀取，應該給出明確錯誤訊息。建議捕捉 `OSError` 並記錄錯誤後回傳空 dict 或退出。

**判斷依據**：diff 中 `load_config` 的 except 子句只涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1247 ｜ PR #14</sub>