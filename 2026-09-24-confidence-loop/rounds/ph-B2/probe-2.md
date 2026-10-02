<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查 `git log` 的失敗，可能導致後續程式在錯誤的資料上執行；另外 `prev` 的取得在 tag 是第一個版本時會拋出 IndexError。整體結構清楚，但需要補上錯誤處理與邊界條件。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 `git log` 子程序的回傳碼 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 第一個 tag 時 `prev` 會拋出 IndexError | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:32` | `load_config` 可能因權限問題拋出未處理的例外 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 `git log` 子程序的回傳碼</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致後續流程誤判為「沒有新 commit」而正常結束，或產生不完整的 release notes。建議加上 `check=True` 或明確檢查 `returncode`，並在失敗時拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 未設定 `check=True`，且後續直接使用 `proc.stdout` 而未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 第一個 tag 時 `prev` 會拋出 IndexError</summary>

在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 之前一定還有其他 tag。如果使用者指定的 `tag` 是 repo 中第一個符合 `v*` 的 tag（例如 `v0.1.0`），`tags.index(tag)` 會是 0，`tags[-1]` 會取到最後一個 tag，而不是正確的前一個版本，導致 release notes 範圍錯誤。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個版本。

**判斷依據**：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1` 作為索引，未處理索引為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:32</code> `load_config` 可能因權限問題拋出未處理的例外</summary>

`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但 `open` 可能因為權限不足或其他 I/O 錯誤拋出 `PermissionError` 或 `OSError`，導致程式直接崩潰。建議捕捉更廣泛的 `OSError` 並記錄警告，或讓呼叫端處理。

**判斷依據**：diff 中 `load_config` 函式的例外處理僅涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`，未涵蓋其他可能的 `OSError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 937 ｜ PR #14</sub>