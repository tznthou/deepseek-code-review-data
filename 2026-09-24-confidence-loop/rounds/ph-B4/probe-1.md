<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並透過 webhook 發布。主要風險在於錯誤處理不完整（git 指令失敗未檢查、webhook 回應未驗證內容）、邊界條件（tag 為第一個版本時會 IndexError）、以及潛在的資訊洩漏（webhook URL 可能含 secret 被記錄）。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能產生不完整的 release notes | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:94` | webhook 回應僅檢查狀態碼，未驗證回應內容，可能誤判成功 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 是第一個版本時會 IndexError | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:97` | webhook URL 可能包含 secret，錯誤訊息中洩漏 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | NOTES_MAX 為負數或零時未處理 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能產生不完整的 release notes</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，程式會繼續執行，可能產生空的或不完整的 commit 清單，最後發布錯誤的公告。建議加上 `check=True` 或明確檢查 `returncode` 並處理錯誤。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:94</code> webhook 回應僅檢查狀態碼，未驗證回應內容，可能誤判成功</summary>

`post` 函式只檢查 HTTP 狀態碼是否在 200-299，但有些 webhook 服務（如 Slack）在請求格式錯誤時仍回傳 200，但回應內容包含錯誤訊息。這會導致程式誤以為發布成功，實際上頻道沒有收到訊息。建議檢查回應內容，例如 Slack 回傳的 `ok` 欄位。

**判斷依據**：diff 中 `post` 函式僅回傳狀態碼檢查結果，未讀取或驗證回應內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 是第一個版本時會 IndexError</summary>

在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 的第一個元素。如果使用者指定了最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致錯誤的比較範圍。建議檢查 `tags.index(tag) == 0` 並處理此情況。

**判斷依據**：diff 中該行直接使用 `-1` 索引，未處理 `tag` 為第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:97</code> webhook URL 可能包含 secret，錯誤訊息中洩漏</summary>

`post` 函式在 `URLError` 的錯誤訊息中直接印出 `url`。如果 webhook URL 包含 token 或簽名（例如 `https://hooks.example.com/services/T000/B000/XXXX` 中的 `XXXX`），這些敏感資訊會出現在 stderr 或日誌中。建議在記錄時遮蔽 URL 中的敏感部分。

**判斷依據**：diff 中錯誤訊息包含完整的 `url`，而 `url` 來自環境變數 `NOTES_WEBHOOK`，可能含有 secret。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> NOTES_MAX 為負數或零時未處理</summary>

`max_items` 函式將 `NOTES_MAX` 轉為整數，但未檢查是否為正數。如果設定為負數或零，`commits[: max_items()]` 會產生空列表或錯誤切片，導致公告內容不正確。建議限制最小值為 1 或使用預設值。

**判斷依據**：diff 中 `max_items` 僅處理 `ValueError`，未檢查數值範圍。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1247 ｜ PR #14</sub>