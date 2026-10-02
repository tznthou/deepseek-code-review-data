<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並透過 webhook 發布。主要風險在於 `commits_between` 未檢查 `git log` 的執行結果，可能導致後續處理空輸出或錯誤輸出；此外 `prev` 的取得依賴 `tags.index(tag)`，若 tag 是第一個版本會拋出 `IndexError`。整體程式結構清晰，但錯誤處理與邊界條件需要補強。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 `git log` 執行結果，可能導致後續處理空輸出或錯誤輸出 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | `prev` 取得方式在 tag 為第一個版本時會拋出 `IndexError` | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | `max_items` 未限制上限，可能導致 payload 過大 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:31` | `load_config` 未處理 JSON 型別錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 `git log` 執行結果，可能導致後續處理空輸出或錯誤輸出</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空字串，函式會回傳空列表，導致 `main` 誤判為「沒有新 commit」而回傳 0，或後續 `commits[0][0]` 拋出 `IndexError`。建議加上 `check=True` 或檢查 `proc.returncode`，並在失敗時記錄錯誤並回傳非零狀態。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中 `commits[0][0]` 直接取第一個元素，若 `commits` 為空會拋出 `IndexError`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> `prev` 取得方式在 tag 為第一個版本時會拋出 `IndexError`</summary>

`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 中的第一個元素。若使用者指定的是最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致 `git log` 範圍錯誤，可能產生不正確的 commit 列表或空列表。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個 tag。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 取得前一個 tag，未處理 index 為 0 的邊界。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> `max_items` 未限制上限，可能導致 payload 過大</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未設定上限。若使用者設定極大值（例如 1000000），`commits[: max_items()]` 會將大量 commit 納入訊息，可能超過 webhook 的 payload 限制或造成記憶體壓力。建議設定合理上限（例如 1000）並在超過時警告。

**判斷依據**：diff 中 `max_items` 函式直接回傳 `int(raw)`，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:31</code> `load_config` 未處理 JSON 型別錯誤</summary>

`load_config` 假設 JSON 檔案內容是 dict，但若檔案內容是 list 或字串，`json.load` 會成功回傳非 dict 型別，後續 `cfg.get` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，若不是則回報錯誤。

**判斷依據**：diff 中 `load_config` 直接回傳 `json.load(fh)` 的結果，未驗證型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1137 ｜ PR #14</sub>