<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到團隊頻道 webhook。整體結構清楚，但存在幾個值得注意的問題：`commits_between` 沒有檢查 `git log` 的退出碼，可能把錯誤輸出當成正常結果；`list_tags` 在只有一個 tag 時會因為 `tags.index(tag) - 1` 變成 -1 而選到最後一個 tag，造成錯誤的範圍；`max_items` 對負數沒有防護，會讓切片行為出乎意料；此外 webhook URL 未驗證 scheme，可能被用於 SSRF。建議先修正這些正確性與安全性問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查退出碼，可能把錯誤輸出當成 commit 清單 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個 tag 時會選到錯誤的 prev tag | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | NOTES_MAX 為負數時切片行為出乎意料 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查退出碼，可能把錯誤輸出當成 commit 清單</summary>

`subprocess.run` 沒有設定 `check=True`，且回傳的 `proc.returncode` 完全沒有被檢查。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串或錯誤訊息，但程式會繼續執行，最後可能貼出空的或不正確的 release notes。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並記錄錯誤後中止。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個 tag 時會選到錯誤的 prev tag</summary>

當 repo 中只有一個符合條件的 tag（例如剛建立第一個 release）時，`tags.index(tag)` 會是 0，`tags.index(tag) - 1` 變成 -1，導致 `prev` 被設為最後一個 tag（也就是自己），`prev..tag` 範圍會是空的，程式會回報「沒有新 commit」。

建議：在 `tags.index(tag) == 0` 時，改用 `git rev-list --max-parents=0 HEAD` 或要求使用者提供 prev tag。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，沒有處理 index 為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> NOTES_MAX 為負數時切片行為出乎意料</summary>

`max_items()` 只檢查是否能轉成整數，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=-5`，`commits[: -5]` 會回傳除了最後 5 筆以外的所有 commit，而不是預期的「最多 5 筆」。

建議：轉換後檢查 `value > 0`，否則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 函式直接回傳 `int(raw)`，沒有檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`NOTES_WEBHOOK` 環境變數由使用者控制，但程式直接將它傳給 `urllib.request.urlopen`。如果攻擊者能影響環境變數（例如 CI 設定），可以指定 `file:///etc/passwd` 或內網位址，造成資訊洩漏或 SSRF。

建議：檢查 URL 的 scheme 必須是 `https`（或至少 `http`），並考慮限制目標網域。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 建立 Request，沒有驗證 scheme。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1183 ｜ PR #14</sub>