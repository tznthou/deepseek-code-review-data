<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能導致後續 IndexError）、`list_tags` 在 tag 不存在時會拋出未處理的 IndexError、`max_items` 對負數或非整數的處理不完整、`post` 未驗證 URL scheme 可能造成 SSRF、以及 `load_config` 對 JSON 型別未驗證。建議先修正錯誤處理與輸入驗證，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續 IndexError | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:50` | list_tags 在 tag 不存在時會拋出未處理的 IndexError | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | post 未驗證 URL scheme，可能造成 SSRF | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | max_items 未處理負數或非整數的 NOTES_MAX | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | load_config 未驗證 JSON 型別，可能導致後續錯誤 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.returncode` 非零但程式不會拋出例外，`proc.stdout` 可能是空字串。接著 `main` 中 `commits[0][0]` 會因為 `commits` 為空而拋出 `IndexError`，且沒有提供有用的錯誤訊息。

建議：在 `subprocess.run` 加上 `check=True`，或在取得 `commits` 後檢查是否為空並回傳明確錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，而 `main` 中 `latest = commits[0][0]` 直接取第一個元素。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:50</code> list_tags 在 tag 不存在時會拋出未處理的 IndexError</summary>

`list_tags` 使用 `subprocess.run` 且設定 `check=True`，若 `git tag` 失敗會拋出 `CalledProcessError`，但呼叫端 `main` 沒有捕捉。此外，`main` 中 `prev = tags[tags.index(tag) - 1]` 在 `tag` 是第一個 tag 時會取到 `tags[-1]`（最後一個 tag），這可能不是預期的行為；若 `tags` 為空，`tags.index(tag)` 會拋出 `ValueError`。

建議：在 `main` 中捕捉 `CalledProcessError` 並回傳錯誤碼；檢查 `tags.index(tag)` 是否為 0，若是則提示沒有前一個 tag。

**判斷依據**：diff 中 `list_tags` 使用 `check=True`，但 `main` 呼叫時未捕捉例外；`prev = tags[tags.index(tag) - 1]` 在 `tag` 是第一個 tag 時會取到最後一個 tag。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> post 未驗證 URL scheme，可能造成 SSRF</summary>

`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，而 `url` 來自環境變數 `NOTES_WEBHOOK`，攻擊者若控制該環境變數，可指定 `file://`、`ftp://` 等 scheme，導致讀取本機檔案或進行內網掃描。

建議：驗證 `url` 的 scheme 必須是 `https`，並限制 host 為允許的網域。

**判斷依據**：diff 中 `post` 未檢查 URL scheme，直接傳給 `urlopen`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> max_items 未處理負數或非整數的 NOTES_MAX</summary>

`max_items` 將 `NOTES_MAX` 轉為整數，但未檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，導致最後一個 commit 被排除，且沒有警告。另外，若 `NOTES_MAX` 為空字串，會回傳預設值，但若為 `0` 則會回傳 0，導致 `commits[:0]` 為空，後續 `latest = commits[0][0]` 會拋出 IndexError。

建議：驗證 `NOTES_MAX` 為正整數，否則回傳預設值並記錄警告。

**判斷依據**：diff 中 `max_items` 只處理 ValueError，未處理負數或 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> load_config 未驗證 JSON 型別，可能導致後續錯誤</summary>

`load_config` 回傳 `json.load` 的結果，但未檢查是否為 dict。若 `.release-notes.json` 內容是 list 或字串，`cfg.get` 會拋出 AttributeError。

建議：檢查 `isinstance(data, dict)`，否則回傳空 dict 或拋出明確錯誤。

**判斷依據**：diff 中 `load_config` 直接回傳 `json.load` 結果，未驗證型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1621 ｜ PR #14</sub>