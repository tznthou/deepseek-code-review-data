<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能導致後續 `commits[0]` 拋出 IndexError）、`list_tags` 在只有一個 tag 時會因 `tags.index(tag) - 1` 變成 -1 而取到最後一個 tag、`max_items` 對負數或非整數輸入的處理不一致、`post` 未驗證 URL scheme 可能造成 SSRF、以及 `load_config` 對 JSON 型別未驗證。建議優先修正 `commits_between` 的錯誤處理與 `list_tags` 的邊界條件。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續 IndexError | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個 tag 時 `tags.index(tag) - 1` 會取到最後一個 tag | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:31` | NOTES_MAX 為負數或非整數時行為不一致 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能造成 SSRF | 0.60 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | 設定檔 JSON 型別未驗證 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空字串，`commits` 會是空 list。在 `main` 中，`latest = commits[0][0]` 會因此拋出 `IndexError`，程式直接 crash。建議在 `subprocess.run` 加上 `check=True`，或檢查 `proc.returncode != 0` 時記錄錯誤並回傳空 list 或拋出例外。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，而 `main` 中 `latest = commits[0][0]` 假設 `commits` 非空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個 tag 時 `tags.index(tag) - 1` 會取到最後一個 tag</summary>

在 `main` 中，`prev = tags[tags.index(tag) - 1]`。若 `tags` 只有一個元素（即目前 tag 是第一個 tag），`tags.index(tag)` 為 0，`-1` 會變成 -1，Python 會取到最後一個元素（也就是自己），導致 `prev == tag`，`git log prev..tag` 會是空範圍，`commits` 為空，進而觸發 `IndexError`。建議在 `tags.index(tag) == 0` 時處理（例如回報錯誤或使用 repo 初始 commit）。

**判斷依據**：diff 中 `prev = tags[tags.index(tag) - 1]` 未處理 `index` 為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:31</code> NOTES_MAX 為負數或非整數時行為不一致</summary>

`max_items` 對 `NOTES_MAX` 的處理：若為空字串回傳預設值；若無法轉為整數則記錄警告並回傳預設值；但若轉為負數（例如 `-1`），會直接回傳負數。在 `main` 中 `commits[: max_items()]` 若 `max_items()` 為負數，切片會取到倒數幾個元素，可能不是預期行為。建議對負數也回傳預設值或設定下限。

**判斷依據**：diff 中 `max_items` 未處理負數輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能造成 SSRF</summary>

`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查 scheme 是否為 http/https。若攻擊者能控制環境變數（例如 CI 設定），可指定 `file://` 或 `gopher://` 等 scheme，導致任意檔案讀取或內網請求。建議限制 scheme 為 `http` 或 `https`。

**判斷依據**：diff 中 `post` 未對 `url` 做 scheme 驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> 設定檔 JSON 型別未驗證</summary>

`load_config` 回傳 `json.load` 的結果，但未驗證其型別是否為 dict。若 `.release-notes.json` 內容為 list 或字串，後續 `cfg.get('title', ...)` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，否則回傳空 dict 或拋出明確錯誤。

**判斷依據**：diff 中 `load_config` 直接回傳 `json.load` 結果，未做型別檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1501 ｜ PR #14</sub>