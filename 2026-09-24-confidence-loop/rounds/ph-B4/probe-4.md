<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。主要風險在於 `commits_between` 沒有檢查 `git log` 的失敗，可能導致後續程式碼在錯誤的資料上執行；此外 `prev` 的取得在 tag 是第一個版本時會拋出 IndexError。整體結構清楚，但需要補上錯誤處理與邊界條件。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能導致後續處理錯誤資料 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:32` | `load_config` 只處理 `FileNotFoundError` 和 `JSONDecodeError`，其他例外會直接中斷程式 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能導致後續處理錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身出錯而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，然後 `main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

**判斷依據**：diff 第 56-59 行，`subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout` 而沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError</summary>

如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個符合 `v*` 的 tag），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式會直接 crash。建議在取 `prev` 前檢查 index 是否大於 0，若為 0 則提示使用者這是第一個版本，或改用其他方式取得起始點。

**判斷依據**：diff 第 104 行，直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為負數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:32</code> `load_config` 只處理 `FileNotFoundError` 和 `JSONDecodeError`，其他例外會直接中斷程式</summary>

`load_config` 在讀取設定檔時，如果檔案存在但權限不足（`PermissionError`）或編碼錯誤（`UnicodeDecodeError`），這些例外不會被捕捉，程式會直接 crash。雖然設定檔是選配的，但這類錯誤應該被視為可預期的失敗，建議捕捉 `OSError` 並記錄警告後回傳空 dict，或至少讓錯誤訊息更友善。

**判斷依據**：diff 第 34-37 行，只捕捉了兩種例外，其他 `OSError` 子類別（如 `PermissionError`）會直接傳播。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 969 ｜ PR #14</sub>