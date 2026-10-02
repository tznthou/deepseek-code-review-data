<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，主要功能是從 git 歷史中整理兩個 tag 之間的 commit，並透過 webhook 發布到團隊頻道。整體結構清晰，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 函式未檢查 `git log` 的執行結果，可能導致在 repo 路徑無效時程式崩潰；另外 `max_items` 函式未處理負數或零值，可能造成輸出異常；`post` 函式未驗證 webhook URL 的 scheme，存在 SSRF 風險；最後 `main` 函式在 `tag` 是第一個 tag 時會嘗試存取 `tags[-1]`，導致 IndexError。建議優先修正這些問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 執行結果，可能導致程式崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 是第一個 tag 時會 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:44` | NOTES_MAX 未處理負數或零值 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，存在 SSRF 風險 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 執行結果，可能導致程式崩潰</summary>

`commits_between` 函式呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查回傳碼。如果 `repo` 路徑無效或不是 git repository，`git log` 會失敗並將錯誤訊息寫入 stderr，但 `proc.stdout` 會是空字串，函式會回傳空列表。後續 `main` 函式會因為 `commits` 為空而回傳 0，但實際上並未產生任何 release notes，造成誤導。建議加上 `check=True` 或檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 是第一個 tag 時會 IndexError</summary>

`main` 函式中，`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 列表的第一個元素時會嘗試存取 `tags[-1]`，這會回傳最後一個 tag，而不是正確的前一個 tag（實際上沒有前一個）。這會導致錯誤的 commit 範圍，甚至可能產生空列表或錯誤的 release notes。建議檢查 `tags.index(tag) == 0` 的情況，並回傳錯誤或使用不同的邏輯。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未處理 `tag` 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:44</code> NOTES_MAX 未處理負數或零值</summary>

`max_items` 函式將環境變數 `NOTES_MAX` 轉為整數後直接回傳，未檢查是否為正數。如果設定為負數或零，`commits[: max_items()]` 會產生空列表或錯誤切片，導致輸出異常。建議加上驗證，例如 `if value < 1: return DEFAULT_MAX`。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，未檢查轉換後的值是否合理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，存在 SSRF 風險</summary>

`post` 函式直接使用 `urllib.request.urlopen` 發送請求，未檢查 URL 的 scheme。如果 `NOTES_WEBHOOK` 被設定為 `file://` 或 `ftp://` 等非 HTTP(S) 協定，可能導致本地檔案讀取或內部網路掃描。建議驗證 URL 必須以 `https://` 開頭（或至少限制為 `http://` 和 `https://`）。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 參數建立請求，未進行任何 scheme 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 1245 ｜ PR #14</sub>