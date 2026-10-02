<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗回傳碼，可能導致空公告或錯誤內容；`list_tags` 在只有一個符合條件的 tag 時會因索引 -1 而選到錯誤的 prev；`max_items` 對負數或非整數的環境變數處理不完整；`post` 未驗證 URL scheme，可能被用於 SSRF。整體功能完整，但上述問題需要修正。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能產生空公告 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個符合條件的 tag 時，`prev` 會取到最後一個 tag 而非前一個 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:35` | `NOTES_MAX` 為負數時會導致 `commits[:max_items()]` 切片行為異常 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | `post` 未驗證 URL scheme，可能被用於 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能產生空公告</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損壞、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，導致後續產生空公告並貼到 webhook。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外。

**判斷依據**：diff 中 `commits_between` 函式呼叫 `subprocess.run` 沒有 `check=True`，且未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個符合條件的 tag 時，`prev` 會取到最後一個 tag 而非前一個</summary>

`list_tags` 回傳所有符合 `TAG_RE` 的 tag，若 repo 中只有一個符合條件的 tag（例如只有 `v1.0.0`），則 `tags.index(tag)` 為 0，`prev = tags[-1]` 會是 `v1.0.0` 本身，導致 `prev..tag` 範圍為空，`commits_between` 回傳空 list，最後輸出「沒有新 commit」。建議在 `tags.index(tag) == 0` 時處理（例如從 repo 初始 commit 開始，或提示使用者）。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未處理 index 為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:35</code> `NOTES_MAX` 為負數時會導致 `commits[:max_items()]` 切片行為異常</summary>

`max_items` 只處理了非整數的情況，若 `NOTES_MAX` 設為負數（例如 `-1`），`int(raw)` 會成功，回傳負數。之後 `commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit。建議在 `max_items` 中檢查數值是否為正整數，否則回傳預設值。

**判斷依據**：diff 中 `max_items` 函式只捕捉 `ValueError`，未檢查轉換後的數值是否為正。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> `post` 未驗證 URL scheme，可能被用於 SSRF</summary>

`NOTES_WEBHOOK` 由環境變數控制，攻擊者若可控制該變數，可將 URL 設為 `file:///etc/passwd` 或內網位址，`urllib.request.urlopen` 會嘗試讀取或連線。雖然此工具通常由開發者自行執行，但若在 CI 或共享環境中使用，可能造成資訊洩漏。建議限制 scheme 為 `https` 或 `http`，並考慮阻擋內網位址。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 建立 Request，未檢查 scheme。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1242 ｜ PR #14</sub>