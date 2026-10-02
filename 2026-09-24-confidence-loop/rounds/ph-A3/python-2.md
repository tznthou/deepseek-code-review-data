<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性（shell=True 的指令注入、token 可能外洩）、以及可變預設值導致的狀態累積。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們會直接造成資料錯誤或安全漏洞。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值，導致跨呼叫累積作者 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 使用可變預設值，且環境變數轉換可能失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式對 pr 的鍵存取可能因缺失而拋出 KeyError | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，沒有記錄或重新拋出。當 GitHub API 呼叫失敗（例如網路錯誤、token 無效、PR 不存在）時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，且錯誤訊息不明確。建議至少記錄錯誤並重新拋出，或讓呼叫端檢查 `None`。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 72 行）被直接當成 dict 使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數或環境變數，攻擊者可注入額外指令（例如 `repo` 設為 `x; rm -rf /`）。應避免使用 `shell=True`，改用參數列表形式，並分開執行 `tar` 和 `gh` 指令。

**判斷依據**：diff 第 88 行：`shell=True` 且 f-string 包含外部輸入 `path` 和 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值，導致跨呼叫累積作者</summary>

`def collect_authors(repo, numbers, seen=[])` 的預設參數 `seen` 是 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果呼叫者沒有傳入 `seen`，作者會被累積到同一個 list 中，造成結果錯誤。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 28 行：可變預設值 `seen=[]`，且函式內對其進行 `append` 操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 使用可變預設值，且環境變數轉換可能失敗</summary>

`def threshold_from_env(default={"days": 7})` 的預設參數是 dict，雖然函式內沒有修改它，但若未來修改可能導致跨呼叫污染。此外，`int(raw)` 沒有處理 `ValueError`，當環境變數 `PR_STALE_DAYS` 不是數字時會拋出例外。建議改用 `default=None` 並在函式內設定，同時捕捉轉換例外。

**判斷依據**：diff 第 44 行：可變預設值 dict，且第 46 行 `int(raw)` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`f = open(path, "w")` 後手動 `f.close()`，但若寫入過程拋出例外（例如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 83-87 行：手動開啟和關閉檔案，沒有例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError</summary>

`os.environ["GITHUB_TOKEN"]` 在環境變數未設定時會拋出 `KeyError`，且錯誤訊息不明確。建議使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`，提供友善的錯誤訊息。

**判斷依據**：diff 第 21 行：直接索引環境變數，未處理缺失情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式對 pr 的鍵存取可能因缺失而拋出 KeyError</summary>

`pr["additions"]`、`pr["changed_files"]`、`pr["title"]` 直接索引，若 API 回應缺少這些欄位（例如權限不足或 API 變更）會拋出 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 52-56 行：直接索引 dict，未使用 `.get()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1800 ｜ PR #12</sub>