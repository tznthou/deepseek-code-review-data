<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於 `commits_between` 未檢查 git 指令的失敗，可能導致後續處理空資料或錯誤資料；此外 `prev` 的取得在 tag 是第一個符合格式的 tag 時會拋出 IndexError。整體結構清晰，但建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能導致錯誤的 release notes | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個符合格式的 tag 時，prev 會造成 IndexError | 0.85 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能導致錯誤的 release notes</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且未檢查 `proc.returncode`。如果 git 指令失敗（例如 repo 路徑無效、git 不在 PATH、或權限不足），`proc.stdout` 會是空字串，函式會回傳空 list，後續流程會誤以為沒有 commit 而回傳 0，但實際上沒有產生任何 release notes。建議加上 `check=True` 或檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個符合格式的 tag 時，prev 會造成 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`tags[-1]` 會取到最後一個 tag，這通常不是預期的行為，且可能導致錯誤的 commit 範圍。建議檢查 `tags.index(tag) == 0` 的情況，並決定要如何處理（例如回報錯誤或使用其他基準）。

**判斷依據**：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1` 作為索引，未處理 `tag` 是第一個元素的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 673 ｜ PR #14</sub>