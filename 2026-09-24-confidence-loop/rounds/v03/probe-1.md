<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git log 整理 commit 並貼到 webhook。主要風險在於 `commits_between` 沒有檢查 `git log` 的失敗（例如 repo 路徑錯誤或 git 指令不存在），會讓程式在沒有資料的情況下繼續執行並可能貼出空白公告；另外 `max_items` 對負數或非整數的環境變數處理不夠嚴謹，可能造成切片行為不如預期。整體結構清楚，但建議先修正錯誤處理與輸入驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能貼出空白公告 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | NOTES_MAX 為負數或非整數時行為不一致 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能貼出空白公告</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑不存在、git 未安裝或權限不足而失敗，`proc.stdout` 會是空字串，函式會回傳空 list。後續 `main` 會因為 `commits` 為空而直接回傳 0，不會貼出公告，但若 `commits` 非空（例如 git 輸出部分內容後失敗），程式仍會繼續執行並可能貼出不完整的公告。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且回傳值未檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> NOTES_MAX 為負數或非整數時行為不一致</summary>

`max_items` 只處理了 `ValueError`，但 `int(raw)` 也可能拋出 `TypeError`（不太可能，因為 raw 是字串）。另外，如果 `NOTES_MAX` 是負數，`commits[: max_items()]` 會回傳除了最後幾個元素以外的所有 commit，這可能不是預期行為。建議加上範圍檢查，例如 `max(0, value)` 或明確拒絕負數。

**判斷依據**：diff 中 `max_items` 函式沒有處理負數或非整數輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 函式直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，沒有驗證 scheme 是否為 http/https。如果攻擊者能控制環境變數（例如在 CI 中注入），可能導致請求發送到內部服務。但這需要攻擊者已有環境變數控制權，風險較低。建議加上 scheme 檢查。

**判斷依據**：diff 中 `post` 函式未對 URL 進行驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3863 (cache hit 1536) ｜ completion tokens 930 ｜ PR #14</sub>