<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，當 repo 路徑無效或 tag 不存在時，會把 stderr 的錯誤訊息當成 commit 內容，產生錯誤的公告。另外，`prev` 的取得方式在 tag 是第一個版本時會拋出 IndexError，且 `NOTES_MAX` 沒有上限，可能造成 payload 過大。建議先修正這三個問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查退出碼，錯誤訊息會被當成 commit 內容 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，prev 會拋出 IndexError | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:37` | NOTES_MAX 沒有上限，可能造成 payload 過大 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查退出碼，錯誤訊息會被當成 commit 內容</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 失敗時（例如 repo 路徑不存在、tag 不存在、或 git 本身出錯），`proc.returncode` 非零，但程式碼仍會繼續處理 `proc.stdout`。此時 stdout 可能為空，但 stderr 的錯誤訊息不會被讀取，導致後續邏輯誤以為沒有 commit 或產生錯誤的公告。

**失敗情境**：使用者執行 `python3 release_notes.py /nonexistent v1.2.3`，`git log` 會輸出錯誤到 stderr 並回傳非零退出碼，但 `commits_between` 會回傳空列表，`main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。

**建議**：在 `subprocess.run` 加上 `check=True`，讓失敗時拋出 `CalledProcessError`，由呼叫端處理或直接讓程式以非零碼結束。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，prev 會拋出 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是沒有前一個 tag。這會導致錯誤的 commit 範圍，甚至可能產生空公告或錯誤內容。

**失敗情境**：repo 只有一個 tag `v1.0.0`，使用者執行 `python3 release_notes.py repo v1.0.0`，`tags.index(tag)` 為 0，`prev` 會是 `tags[-1]`（即 `v1.0.0` 本身），`commits_between` 會執行 `git log v1.0.0..v1.0.0`，回傳空列表，程式印出「之間沒有新 commit」並回傳 0，但實際上應該要提示沒有前一個 tag 或改用其他方式。

**建議**：在取 `prev` 前檢查 `tags.index(tag) == 0`，若是則記錄錯誤並回傳非零碼，或改用 `git describe --tags --abbrev=0 <tag>^` 等方式取得前一個 tag。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，沒有處理 `tag` 是第一個元素的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:37</code> NOTES_MAX 沒有上限，可能造成 payload 過大</summary>

`max_items()` 直接將環境變數 `NOTES_MAX` 轉成整數回傳，沒有設定上限。如果使用者設定一個極大的值（例如 1000000），`commits[: max_items()]` 會嘗試將所有 commit 放入公告，可能導致 webhook payload 過大而被拒絕，或造成記憶體壓力。

**失敗情境**：使用者設定 `NOTES_MAX=1000000`，且 repo 有大量 commit，程式會產生超長的公告文字，webhook 端可能回傳 413 或直接斷線。

**建議**：在 `max_items()` 中設定一個合理的上限（例如 100），超過時記錄警告並使用上限值。

**判斷依據**：diff 中 `max_items()` 函式沒有對 `int(raw)` 的結果做上限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.Request`，沒有驗證 scheme 是否為 http/https。如果攻擊者能控制環境變數（例如在 CI 中注入），可以指定 `file://` 或 `gopher://` 等 scheme，造成 SSRF 或本地檔案讀取。

**失敗情境**：在 CI 環境中，攻擊者透過 pull request 修改 workflow 設定 `NOTES_WEBHOOK=file:///etc/passwd`，程式會嘗試將公告內容寫入本地檔案。

**建議**：在 `post()` 或 `main()` 中檢查 URL 的 scheme 是否為 `http` 或 `https`，否則拒絕執行。

**判斷依據**：diff 中 `post()` 函式直接使用 `url` 建立 Request，沒有驗證 scheme。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1616 ｜ PR #14</sub>