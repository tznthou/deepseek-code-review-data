<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器腳本，從 git log 整理 commit 並透過 webhook 發布。主要風險在於 `commits_between` 未檢查 git 指令的失敗，可能導致後續程式在錯誤的資料上執行；另外 `max_items` 對負數或零的處理可能造成非預期行為。整體結構清楚，但建議先修正錯誤處理與輸入驗證。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 的執行結果，可能導致後續處理錯誤資料 | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | NOTES_MAX 設為負數或零時可能造成非預期行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 的執行結果，可能導致後續處理錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空列表，後續程式會誤以為沒有 commit 而正常結束，掩蓋了真正的錯誤。建議加上 `check=True` 或檢查 `returncode`，並在失敗時拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式內的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> NOTES_MAX 設為負數或零時可能造成非預期行為</summary>

`max_items` 直接將環境變數轉成整數，沒有驗證範圍。若使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別回傳空列表或全部 commit（因為切片負數索引會從尾端計算），可能導致公告內容不正確。建議加上最小值檢查，例如 `max(1, int(raw))`。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的值是否合理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 1408) ｜ completion tokens 638 ｜ PR #14</sub>