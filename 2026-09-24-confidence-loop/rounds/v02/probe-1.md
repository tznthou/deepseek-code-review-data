<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查子程序失敗、`prev` 在只有一個 tag 時會取到負索引、以及 webhook URL 未驗證可能造成 SSRF。建議先修正這三個問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 子程序失敗時未檢查回傳碼 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個 tag 時 `prev` 會取到負索引 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:109` | webhook URL 未驗證，可能造成 SSRF | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | NOTES_MAX 為負數或零時未處理 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:66` | commit subject 可能包含換行字元，導致輸出格式錯亂 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 子程序失敗時未檢查回傳碼</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 `prev..tag` 範圍無效而失敗，程式會把空的 stdout 當成「沒有 commit」，繼續執行並回報成功。建議加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個 tag 時 `prev` 會取到負索引</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，導致 `commits_between` 的範圍錯誤。建議在 `tags.index(tag) == 0` 時明確處理（例如回報錯誤或使用空範圍）。

**判斷依據**：diff 中直接使用 `tags.index(tag) - 1`，未檢查是否為 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:109</code> webhook URL 未驗證，可能造成 SSRF</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，未檢查 scheme 或主機。攻擊者若可控制環境變數，可指定 `file://` 或內網位址，造成資訊洩漏或內部服務攻擊。建議限制 scheme 為 `https`，並可考慮使用 allowlist。

**判斷依據**：diff 中直接使用環境變數作為 URL，未做任何驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> NOTES_MAX 為負數或零時未處理</summary>

`max_items()` 只檢查是否為整數，未檢查是否為正數。若設定為負數，`commits[: max_items()]` 會取到空列表；若為 0 也會得到空列表，可能非預期。建議限制最小值為 1。

**判斷依據**：diff 中 `int(raw)` 成功後直接回傳，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:66</code> commit subject 可能包含換行字元，導致輸出格式錯亂</summary>

`git log --format=%h %s` 的 subject 可能包含換行（例如 merge commit 或手動輸入），`group()` 直接將 subject 放入列表，`render()` 輸出時未跳脫，可能破壞 Markdown 格式或注入額外內容。建議對 subject 做 sanitize（例如取代換行）。

**判斷依據**：diff 中直接使用 `subject`，未做任何處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 1536) ｜ completion tokens 1231 ｜ PR #14</sub>