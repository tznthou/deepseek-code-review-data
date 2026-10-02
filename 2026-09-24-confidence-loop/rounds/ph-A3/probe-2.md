<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查 git 指令的失敗，可能導致後續以空清單或錯誤資料繼續執行；此外 `prev` 的取得在 tag 是第一個版本時會拋出 IndexError。整體結構清楚，但錯誤處理與邊界條件需要補強。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查 returncode，可能產生錯誤結果 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | `max_items()` 未處理負數或過大的值 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查 returncode，可能產生錯誤結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空清單，導致後續流程誤以為沒有 commit 而提前結束，或產生不完整的 release notes。

建議：加上 `check=True`，或明確檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError</summary>

如果 `tag` 是 `tags` 清單中的第一個元素（例如 repo 只有一個 tag），`tags.index(tag)` 回傳 0，`tags[0 - 1]` 會存取 `tags[-1]`，也就是最後一個元素，這通常不是預期的前一個版本，而且如果 `tags` 是空的（但前面已檢查 `tag in tags`，所以不會是空的），會拋出 IndexError。

建議：檢查 `tags.index(tag) == 0` 的情況，並決定如何處理（例如回報錯誤或使用其他基準）。

**判斷依據**：diff 中直接使用 `tags.index(tag) - 1` 作為索引，沒有處理 tag 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> `max_items()` 未處理負數或過大的值</summary>

`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為負數或過大。如果設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit；如果設定為極大值，可能導致記憶體問題（雖然 commit 數量通常有限）。

建議：限制範圍，例如 `max(0, min(value, 1000))`。

**判斷依據**：diff 中 `max_items()` 直接回傳 `int(raw)`，沒有範圍檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 905 ｜ PR #14</sub>