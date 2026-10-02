<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git log 整理 commit 並貼到 webhook。主要風險在於 `commits_between` 沒有檢查 `git log` 的失敗，可能導致後續程式碼在錯誤的資料上執行；另外 `max_items()` 對負數或零的處理會讓輸出內容不符合預期。整體結構清楚，但建議先修正錯誤處理與邊界條件。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查，可能導致後續程式碼在錯誤資料上執行 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `NOTES_MAX` 設為負數或零時，輸出會是空公告 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查，可能導致後續程式碼在錯誤資料上執行</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身出錯而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，呼叫端會誤以為「沒有新 commit」而正常結束。建議加上 `check=True` 或檢查 `returncode`，並在失敗時拋出例外或回傳明確的錯誤。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `NOTES_MAX` 設為負數或零時，輸出會是空公告</summary>

`max_items()` 只檢查了是否為整數，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空 list，`render` 會產生只有標題的公告，可能造成困惑。建議加上 `if n <= 0: log(...); return DEFAULT_MAX` 或直接限制最小值為 1。

**判斷依據**：diff 中 `max_items()` 函式只處理了 `ValueError`，沒有對轉換後的整數做範圍檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3863 (cache hit 3840) ｜ completion tokens 690 ｜ PR #14</sub>