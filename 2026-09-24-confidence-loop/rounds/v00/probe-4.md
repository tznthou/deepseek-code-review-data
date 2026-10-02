<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，當 repo 路徑無效或 git 指令失敗時，程式會繼續用空輸出往下走，最後可能貼出空公告。另外 `max_items` 對負數沒有防護，會造成切片意外截斷。安全性方面，webhook URL 與 repo 路徑都來自環境或參數，但沒有明顯的注入風險。建議先修正 git 指令的錯誤處理，再考慮其他小問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 執行失敗時未檢查，可能產生空公告 | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 為負數時會意外截斷 commit 列表 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | webhook 回應非 2xx 時未記錄回應內容 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 執行失敗時未檢查，可能產生空公告</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有傳入 `check=True`，也沒有檢查 `proc.returncode`。如果 `repo` 路徑不是有效的 git 儲存庫，或 `git log` 因其他原因失敗，`proc.stdout` 會是空字串，函式回傳空 list。後續 `main` 會因為 `commits` 為空而直接回傳 0，不會貼出任何東西，但也不會回報錯誤。更糟的是，如果 `git log` 部分失敗但仍有輸出（例如 rev 不存在），程式可能貼出不完整的公告。建議加上 `check=True` 或明確檢查 `proc.returncode`，並在失敗時記錄錯誤並回傳非零 exit code。

**判斷依據**：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `subprocess.run` 未設 `check=True`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 為負數時會意外截斷 commit 列表</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為負數。在 `main` 中，`commits[: max_items()]` 若 `max_items()` 回傳負數，Python 切片會從尾端倒數，導致只取最後幾個 commit，而不是全部或前 N 個。例如 `NOTES_MAX=-1` 會讓公告只包含最後一個 commit。建議在轉換後檢查是否為正整數，若不是則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的整數是否為負數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> webhook 回應非 2xx 時未記錄回應內容</summary>

`post` 函式在 `urlopen` 成功取得回應後，只檢查 status code 是否在 200-299 之間，若不是則回傳 False，但沒有記錄回應的 status code 或 body。這會讓除錯變得困難，因為無法知道 webhook 端拒絕的具體原因（例如 400 或 403）。建議在非 2xx 時記錄 `resp.status` 和 `resp.read()` 的內容（注意不要洩漏敏感資訊）。

**判斷依據**：diff 中 `post` 函式在回應非 2xx 時直接回傳 False，沒有記錄任何資訊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 1066 ｜ PR #14</sub>