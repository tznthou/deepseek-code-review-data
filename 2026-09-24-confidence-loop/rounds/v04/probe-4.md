<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查 `git log` 的失敗，可能導致後續程式碼在錯誤的資料上執行；此外，`prev` 的取得方式在 tag 是第一個版本時會拋出 IndexError。整體結構清晰，但建議先修正錯誤處理與邊界條件。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 的執行結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時會拋出 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:103` | 設定檔載入可能拋出未處理的例外 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 的執行結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，導致後續流程誤以為沒有 commit 而回傳成功（return 0）。建議加上 `check=True` 或檢查 returncode，並在失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時會拋出 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`-1` 會取到最後一個元素，而不是報錯。這會導致錯誤的 `prev`，進而產生錯誤的 commit 範圍。應檢查 `tags.index(tag) == 0` 並處理此情況（例如提示沒有前一個 tag 或使用其他基準）。

**判斷依據**：diff 中該行直接使用 `-1` 索引，未處理邊界。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:103</code> 設定檔載入可能拋出未處理的例外</summary>

`load_config` 在檔案存在但內容不是合法 JSON 時會拋出 `SystemExit`，但若檔案權限不足或讀取時發生其他 I/O 錯誤，會拋出未捕捉的 `OSError`，導致程式直接崩潰。建議捕捉 `OSError` 並提供友善錯誤訊息。

**判斷依據**：diff 中 `load_config` 只處理了 `FileNotFoundError` 和 `JSONDecodeError`，未處理其他 `OSError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 887 ｜ PR #14</sub>