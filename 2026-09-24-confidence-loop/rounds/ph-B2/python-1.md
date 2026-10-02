<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未用 with）。此外，classify 對缺少欄位的 PR 會拋 KeyError，threshold_from_env 對非數字環境變數會拋 ValueError。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入造成指令注入 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 造成跨呼叫狀態累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 對缺少 additions 或 changed_files 的 PR 拋 KeyError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 對非數字環境變數拋 ValueError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能洩漏資源 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且未檢查回傳值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入造成指令注入</summary>

`archive` 函式使用 `subprocess.run(..., shell=True)`，且指令字串包含 `repo` 參數，該參數來自命令列輸入（`sys.argv[1]`），攻擊者可注入任意 shell 指令。例如 `repo` 設為 `x; rm -rf /` 會導致嚴重後果。建議改用 `subprocess.run` 的參數列表形式，並避免使用 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 60 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`，未經任何驗證。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），並回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤訊息。建議至少記錄錯誤並重新拋出，或讓呼叫端檢查回傳值。

**判斷依據**：diff 第 25-26 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 造成跨呼叫狀態累積</summary>

`collect_authors` 的 `seen=[]` 是可變預設值，每次呼叫都會累積作者，導致結果不正確。例如連續呼叫 `collect_authors(repo, [1])` 和 `collect_authors(repo, [2])` 會得到 `['user1', 'user2']` 而不是 `['user2']`。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 31 行：`def collect_authors(repo, numbers, seen=[]):`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 對缺少 additions 或 changed_files 的 PR 拋 KeyError</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 回傳的 PR 物件不一定包含這些欄位（例如某些事件或權限不足時）。若欄位缺失會拋 `KeyError`，導致程式終止。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 49 行：`if pr["additions"] > 500:`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 對非數字環境變數拋 ValueError</summary>

`threshold_from_env` 將 `PR_STALE_DAYS` 直接轉為 `int`，若環境變數不是數字（例如 `abc`）會拋 `ValueError`，且沒有處理。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 55 行：`return {"days": int(raw)}`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，若寫入過程拋出例外，檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 62 行：`f = open(path, "w")`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且未檢查回傳值</summary>

即使不考慮注入，`subprocess.run` 的回傳值未被檢查，若 `tar` 或 `gh` 失敗，程式仍會繼續執行並回報成功。建議檢查 `returncode` 並在失敗時拋出例外。

**判斷依據**：diff 第 68 行：`subprocess.run(...)` 未接住回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1605 ｜ PR #12</sub>