<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能導致後續 `commits[0]` 崩潰）、`max_items` 對負數或零的處理可能造成意外行為、`post` 未驗證 URL scheme（SSRF 風險）、以及 `load_config` 未處理權限錯誤。建議先修正 `commits_between` 的錯誤處理與 `max_items` 的輸入驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能導致後續崩潰 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:38` | `NOTES_MAX` 設為負數或零時會產生非預期結果 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | 未驗證 webhook URL 的 scheme，可能造成 SSRF | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:32` | `load_config` 未處理權限錯誤，可能導致程式崩潰 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能導致後續崩潰</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list。接著 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式以 traceback 結束，使用者只看到堆疊而沒有明確錯誤訊息。

建議：加上 `check=True` 或檢查 `proc.returncode != 0` 時記錄錯誤並回傳空 list 或拋出例外。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且 `main` 中 `latest = commits[0][0]` 直接索引第一個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:38</code> `NOTES_MAX` 設為負數或零時會產生非預期結果</summary>

`max_items` 只檢查了是否為整數，沒有檢查是否為正數。若使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別回傳空 list 或倒數第二個元素之前的全部 commit（Python 切片負索引行為）。這可能導致公告內容不完整或完全空白。

建議：在轉換後檢查 `value <= 0` 時記錄警告並回傳 `DEFAULT_MAX`。

**判斷依據**：diff 中 `max_items` 函式只處理 `ValueError`，未驗證數值範圍。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> 未驗證 webhook URL 的 scheme，可能造成 SSRF</summary>

`post` 直接將 `url` 傳給 `urllib.request.Request`，沒有檢查 scheme 是否為 `https` 或 `http`。如果 `NOTES_WEBHOOK` 被設定為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或連線到非預期的資源。雖然環境變數通常由使用者控制，但若此工具被用於 CI/CD 且環境變數來自外部輸入，就可能被利用。

建議：在 `post` 前檢查 `urlparse(url).scheme in ('http', 'https')`，否則回傳錯誤。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 建立 Request，無 scheme 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:32</code> `load_config` 未處理權限錯誤，可能導致程式崩潰</summary>

`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案存在但無讀取權限（`PermissionError`），程式會直接拋出 traceback。建議捕捉 `OSError` 並記錄警告後回傳空 dict，或讓錯誤訊息更友善。

**判斷依據**：diff 中 `load_config` 的 except 子句未包含 `PermissionError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1267 ｜ PR #14</sub>