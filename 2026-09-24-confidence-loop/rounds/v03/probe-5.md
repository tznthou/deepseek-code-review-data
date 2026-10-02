<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並透過 webhook 發佈。主要風險在於 `commits_between` 沒有檢查子程序失敗，可能導致後續處理空資料或錯誤資料；另外 `max_items` 對負數或零的輸入沒有防護，會讓輸出內容異常。整體功能單純，但建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 子程序失敗時未檢查回傳碼，可能導致後續處理空資料 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:34` | NOTES_MAX 設為負數或零時會產生空公告或錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 子程序失敗時未檢查回傳碼，可能導致後續處理空資料</summary>

`commits_between` 執行 `git log` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身異常而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，後續 `main` 會印出「沒有新 commit」並回傳 0，讓使用者誤以為成功。建議加上 `check=True` 或明確檢查 `returncode`，並在失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:34</code> NOTES_MAX 設為負數或零時會產生空公告或錯誤</summary>

`max_items` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否為正數。若設定為 0 或負數，`commits[: max_items()]` 會變成空 list 或從尾端切片，導致公告內容為空或不完整。建議加上 `if value < 1` 的檢查，並回退到預設值。

**判斷依據**：diff 中 `max_items` 函式只處理 `ValueError`，未檢查轉換後的值是否大於 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3863 (cache hit 3840) ｜ completion tokens 691 ｜ PR #14</sub>