<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於錯誤處理不完整（git 指令失敗時未檢查回傳碼）、外部輸入（環境變數、設定檔）缺乏驗證，以及 webhook URL 未驗證可能造成 SSRF。建議先修正 commits_between 的錯誤處理與 NOTES_MAX 的驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能產生不完整的 release notes | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:35` | NOTES_MAX 未限制範圍，可能造成記憶體耗盡 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證，可能被用於 SSRF | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:50` | list_tags 使用 check=True 但未處理 CalledProcessError | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能產生不完整的 release notes</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，程式會繼續執行，把空的或部分輸出當成正常結果，最後貼出錯誤的公告。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:35</code> NOTES_MAX 未限制範圍，可能造成記憶體耗盡</summary>

`max_items()` 從環境變數讀取整數，但沒有檢查上限。如果使用者設定 `NOTES_MAX=999999999`，`commits[: max_items()]` 會嘗試建立一個巨大的 list，可能耗盡記憶體。

建議：加上合理的上限（例如 1000），或至少檢查是否為正整數。

**判斷依據**：diff 中 `max_items()` 只處理了 `ValueError`，沒有檢查轉換後的數值範圍。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證，可能被用於 SSRF</summary>

`post()` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，沒有驗證 scheme 或主機。如果攻擊者能控制環境變數（例如透過 CI 設定），可以讓程式向內部服務發送請求。

建議：檢查 URL 是否為 `https://` 且主機在允許清單中，或至少限制為 https。

**判斷依據**：diff 中 `post()` 直接使用 `url` 參數，而 `url` 來自環境變數，未做任何驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:50</code> list_tags 使用 check=True 但未處理 CalledProcessError</summary>

`list_tags` 呼叫 `subprocess.run` 時設定了 `check=True`，但沒有捕捉 `subprocess.CalledProcessError`。如果 `git tag` 失敗，程式會直接 traceback 退出，使用者只看到一堆錯誤訊息。

建議：捕捉例外並印出友善的錯誤訊息，或讓上層處理。

**判斷依據**：diff 中 `list_tags` 的 `subprocess.run` 有 `check=True`，但函式沒有 try/except 處理可能的 `CalledProcessError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1130 ｜ PR #14</sub>