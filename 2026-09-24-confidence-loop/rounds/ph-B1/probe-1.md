<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並貼到 webhook。主要風險在於 `commits_between` 未檢查 `git log` 的失敗，可能導致後續程式在空輸出上執行並誤報成功；`max_items` 對負數或零值未做下限處理，可能產生空公告；`list_tags` 未處理 `git tag` 失敗，可能讓程式在無 tag 時崩潰。整體結構清晰，但錯誤處理需要加強。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能導致誤報成功 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:42` | `max_items` 未處理負數或零，可能產生空公告 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:50` | `list_tags` 未處理 `git tag` 失敗，可能導致程式崩潰 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能導致誤報成功</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損壞、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list。後續 `main` 會因 `commits` 為空而回傳 0（成功），但實際上沒有產生任何公告。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中 `if not commits:` 會回傳 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:42</code> `max_items` 未處理負數或零，可能產生空公告</summary>

`max_items` 直接將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或 0，`commits[: max_items()]` 會得到空 list，導致 `group` 回傳空 sections，`render` 只輸出標題，最後仍會呼叫 `post` 貼出無內容的公告。建議限制最小值為 1，或對非法值回退到預設值。

**判斷依據**：diff 中 `max_items` 只處理 ValueError，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:50</code> `list_tags` 未處理 `git tag` 失敗，可能導致程式崩潰</summary>

`list_tags` 使用 `check=True`，若 `git tag` 因 repo 不存在或權限問題失敗，會拋出 `subprocess.CalledProcessError`，但 `main` 未捕捉此例外，程式會以 traceback 結束。建議在 `main` 中捕捉並回傳錯誤碼，或改用 `check=False` 並檢查回傳碼。

**判斷依據**：diff 中 `list_tags` 使用 `check=True`，但 `main` 呼叫時未包在 try/except 中。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 1408) ｜ completion tokens 976 ｜ PR #14</sub>