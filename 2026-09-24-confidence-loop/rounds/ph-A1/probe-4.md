<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並將結果貼到團隊頻道的 webhook。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，當 repo 路徑無效或 git 指令失敗時，程式會靜默地產生空的 commit 清單，導致後續流程誤判為「沒有新 commit」而回報成功。另外，`max_items` 對 `NOTES_MAX` 的解析沒有處理負數或零，可能造成切片行為異常。還有一些較小的問題，例如 `load_config` 對 JSON 型別沒有驗證、`post` 沒有檢查 HTTP 狀態碼、以及 `list_tags` 在沒有符合條件的 tag 時會拋出未處理的例外。建議優先修正 `commits_between` 的錯誤處理，並補上 `NOTES_MAX` 的範圍檢查。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 執行失敗時未檢查，導致靜默產生空結果 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:42` | NOTES_MAX 未驗證範圍，負數或零會造成非預期行為 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:28` | load_config 未驗證 JSON 頂層型別，可能導致後續 AttributeError | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:95` | post 未檢查 HTTP 狀態碼，非 2xx 回應仍視為成功 | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:118` | list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 執行失敗時未檢查，導致靜默產生空結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且沒有檢查 `proc.returncode`。如果 `repo` 路徑不存在、不是 git repo，或 `prev..tag` 範圍無效，`git log` 會以非零狀態碼結束，但程式會繼續執行，將 `proc.stdout`（可能是空字串或錯誤訊息）解析成空的 commit 清單。這會讓 `main` 誤判為「沒有新 commit」而回傳 0（成功），實際上根本沒有產生任何 release notes。

**失敗情境**：使用者提供錯誤的 repo 路徑，或 tag 名稱拼錯，程式會靜默地回報成功，但沒有貼出任何公告。

**建議**：在 `subprocess.run` 中加入 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:42</code> NOTES_MAX 未驗證範圍，負數或零會造成非預期行為</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會得到空清單或意外的切片結果（例如 `commits[:-1]` 會排除最後一個 commit）。這可能導致 release notes 內容不完整或完全空白。

**失敗情境**：CI 或部署環境誤設 `NOTES_MAX=0`，程式會貼出只有標題、沒有任何 commit 的公告。

**建議**：在轉換後檢查 `value <= 0`，若小於等於 0 則記錄警告並使用預設值，或直接回傳錯誤。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有對轉換成功的值做範圍檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:28</code> load_config 未驗證 JSON 頂層型別，可能導致後續 AttributeError</summary>

`load_config` 直接回傳 `json.load` 的結果，沒有檢查是否為 dict。如果 `.release-notes.json` 的內容是合法的 JSON 但不是物件（例如陣列或字串），`main` 中的 `cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

**失敗情境**：使用者誤將設定檔寫成 `["feat", "fix"]` 或 `"hello"`，程式會在執行到 `cfg.get` 時崩潰，且沒有友善的錯誤訊息。

**建議**：在 `load_config` 中檢查 `isinstance(data, dict)`，若不是則拋出 `SystemExit` 或記錄錯誤。

**判斷依據**：diff 中 `load_config` 函式直接回傳 `json.load` 的結果，沒有型別檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:95</code> post 未檢查 HTTP 狀態碼，非 2xx 回應仍視為成功</summary>

`post` 函式在 `urlopen` 成功後，只回傳 `200 <= resp.status < 300` 的布林值，但呼叫端 `main` 只檢查回傳值是否為 `False`，沒有區分「HTTP 錯誤」和「網路錯誤」。如果 webhook 端回傳 404 或 500，`post` 會回傳 `False`，`main` 會回傳 1（失敗），但錯誤訊息只記錄在 `post` 內部的 `log`，沒有提供足夠的上下文（例如回應內容）。這對除錯不太方便，但功能上仍能正確反映失敗。

**建議**：在 `post` 中記錄 HTTP 狀態碼和回應內容，或讓 `post` 拋出例外由 `main` 統一處理。

**判斷依據**：diff 中 `post` 函式只回傳布林值，沒有記錄 HTTP 狀態碼或回應內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:118</code> list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError</summary>

`list_tags` 回傳的 `tags` 清單可能為空（例如 repo 中沒有任何 `v*` tag）。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 這一行，如果 `tag` 不在 `tags` 中，`tags.index(tag)` 會拋出 `ValueError`，但這個例外沒有被捕捉，程式會直接崩潰。雖然 `main` 前面有檢查 `if tag not in tags`，但這個檢查是在 `list_tags` 之後，如果 `list_tags` 回傳空清單，`tag not in tags` 為真，會先記錄錯誤並回傳 2，所以實際上不會執行到 `tags.index`。然而，如果 `list_tags` 因為某種原因回傳了不包含 `tag` 的非空清單（例如 tag 格式不符），`tag not in tags` 也會攔截。因此這個問題只有在 `list_tags` 拋出例外時才會發生，但 `list_tags` 本身沒有處理 `subprocess.run` 的錯誤（見另一個 finding）。

**建議**：在 `main` 中對 `tags.index` 的呼叫加上例外處理，或改用更安全的方式取得前一個 tag。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag)`，沒有處理 `ValueError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 2111 ｜ PR #14</sub>