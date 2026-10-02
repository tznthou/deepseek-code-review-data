<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於 `commits_between` 未檢查 git 指令的失敗，可能導致後續處理空輸出或錯誤資料；此外 `prev` 的取得在 tag 為第一個時會拋出 IndexError。整體結構清晰，但錯誤處理與邊界條件需要補強。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續處理錯誤 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個 tag 時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:125` | `commits[0]` 在 commits 為空時會拋出 IndexError | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:31` | `load_config` 僅處理 FileNotFoundError 和 JSONDecodeError，其他例外（如權限錯誤）會導致程式崩潰 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續處理錯誤</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑錯誤、權限不足），`proc.stdout` 可能為空字串，函式會回傳空 list，導致後續 `commits[0]` 拋出 IndexError，或產生不完整的 release notes。建議加上 `check=True` 或檢查 returncode 並拋出例外。

**判斷依據**：diff 中 `commits_between` 函式的 subprocess.run 呼叫沒有 check=True，且未檢查 returncode。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個 tag 時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError</summary>

如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個 tag），`tags.index(tag)` 為 0，`tags[-1]` 會取到最後一個 tag，而不是前一個 tag，這可能不是預期行為。更嚴重的是，如果 tags 為空（雖然前面已檢查 tag 存在，但若 tag 存在於 tags 中，tags 至少有一個元素），但若 tag 是第一個，`tags[-1]` 會取到最後一個，造成錯誤的 prev。建議明確檢查 index 是否為 0，並處理沒有前一個 tag 的情況。

**判斷依據**：diff 中 main 函式取得 prev 的方式，未處理 tag 為第一個的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:125</code> `commits[0]` 在 commits 為空時會拋出 IndexError</summary>

雖然前面有 `if not commits: return 0`，但 `commits_between` 可能因為 git 指令失敗而回傳空 list（見另一個 finding），此時 `commits[0]` 會拋出 IndexError。建議在取得 `latest` 前再次確認 commits 非空，或讓 `commits_between` 在失敗時拋出例外。

**判斷依據**：diff 中 main 函式直接取 commits[0]，但 commits 可能因 git 失敗而為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:31</code> `load_config` 僅處理 FileNotFoundError 和 JSONDecodeError，其他例外（如權限錯誤）會導致程式崩潰</summary>

`load_config` 使用 `open` 讀取檔案，若檔案存在但無法讀取（例如權限不足），會拋出 PermissionError，未被捕捉，導致程式以 traceback 結束。建議捕捉 OSError 或更廣泛的例外，並提供友善錯誤訊息。

**判斷依據**：diff 中 load_config 的例外處理僅限於 FileNotFoundError 和 JSONDecodeError。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1134 ｜ PR #14</sub>