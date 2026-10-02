<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查 git 指令的失敗，可能導致後續處理空資料或錯誤資料；此外 `max_items` 未限制上限，可能造成記憶體或 payload 過大。建議先修正這兩個問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 子程序的回傳碼 | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | NOTES_MAX 未設上限，可能造成資源耗盡 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 子程序的回傳碼</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致後續流程誤以為沒有 commit 而正常結束（回傳 0），但實際上根本沒有產生 release notes。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> NOTES_MAX 未設上限，可能造成資源耗盡</summary>

`max_items` 直接將環境變數 `NOTES_MAX` 轉成整數，沒有上限。如果使用者設定一個極大的值（例如 10^9），`commits[: max_items()]` 會嘗試建立一個巨大的列表，可能耗盡記憶體。此外，webhook payload 也可能過大而被拒絕。

建議：設定一個合理的上限（例如 1000），或至少檢查是否為正整數。

**判斷依據**：diff 中 `return int(raw)` 沒有範圍檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 615 ｜ PR #14</sub>