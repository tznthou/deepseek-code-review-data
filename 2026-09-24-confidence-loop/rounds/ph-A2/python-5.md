<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性（shell=True 指令注入、token 可能外洩）、以及可變預設值導致的狀態污染。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們會直接造成錯誤結果或安全漏洞。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:27` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配使用者輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態污染 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出未處理的例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 函式直接存取可能不存在的鍵 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，且未處理寫入錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:77` | archive 函式未檢查 subprocess.run 的回傳值 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:27</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當成 dict 來存取鍵（例如 `pr["user"]["login"]`），當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，造成程式崩潰。

具體失敗情境：
- GitHub API 回傳 404（PR 不存在）或 401（token 無效）時，`urlopen` 會拋出 `HTTPError`，被 `except` 吞掉，`_fetch` 回傳 `None`，接著 `pr["user"]` 就會拋出 `TypeError: 'NoneType' object is not subscriptable`。
- 網路逾時或 DNS 失敗時，同樣會回傳 `None` 並導致後續崩潰。

建議：
- 讓 `_fetch` 在失敗時拋出例外（或回傳明確的錯誤值），並在呼叫端處理。
- 至少記錄錯誤訊息，不要完全靜默。

**判斷依據**：diff 第 27 行 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 31 行）和 `main`（第 73 行）被直接當成 dict 使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配使用者輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 且 `shell=True`，指令字串由 `repo` 和 `path` 拼接而成。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可以注入額外的 shell 指令。

具體攻擊情境：
- 使用者執行 `python3 pr_stats.py 'repo; rm -rf ~' 1`，`repo` 的值會讓指令變成 `tar czf /tmp/pr-stats-repo; rm -rf ~.tgz /tmp/pr-stats-repo; rm -rf ~ && gh repo view repo; rm -rf ~`，導致任意指令執行。
- 即使 `repo` 是受信任的輸入，這種寫法也容易因為特殊字元（空格、分號、引號）而出錯。

建議：
- 使用參數列表形式，避免 `shell=True`。
- 若必須使用 shell，請對所有外部輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 61 行，`repo` 來自 `sys.argv[1]`（第 66 行），未經驗證直接嵌入 shell 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態污染</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值。Python 在函式定義時只建立一次該 list，之後每次呼叫都會共用同一個 list 物件。如果呼叫者沒有傳入 `seen`，多次呼叫會累積之前的結果。

具體情境：
- 在同一個 process 中呼叫 `collect_authors('repo', [1])` 兩次，第二次呼叫會回傳 `['user1', 'user1']` 而不是 `['user1']`。
- 這在測試或互動式環境中很容易造成難以追蹤的 bug。

建議：
- 改用 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 31 行，`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 33 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出未處理的例外</summary>

`threshold_from_env` 的參數 `default={"days": 7}` 是可變預設值，雖然函式內沒有修改 `default`，但若未來修改就可能引入 bug。更嚴重的問題是 `int(raw)` 沒有處理轉換失敗：如果環境變數 `PR_STALE_DAYS` 不是整數（例如設為 `abc`），會拋出 `ValueError` 且沒有被捕捉，導致程式崩潰。

具體情境：
- 使用者設定 `PR_STALE_DAYS=abc`，程式在 `int(raw)` 處拋出 `ValueError`。

建議：
- 將預設值改為 `None` 並在函式內處理。
- 對 `int(raw)` 加上 try/except，或使用更安全的轉換方式。

**判斷依據**：diff 第 44-47 行，`default` 是可變 dict，且 `int(raw)` 未處理例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 函式直接存取可能不存在的鍵</summary>

`classify` 函式直接使用 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`。如果 `_fetch` 回傳的 JSON 缺少這些鍵（例如 API 回應格式變更或某些 PR 沒有這些欄位），會拋出 `KeyError`。

具體情境：
- GitHub API 在某些情況下可能不會回傳 `additions` 或 `changed_files`（例如權限不足或 API 版本變更），導致程式崩潰。

建議：
- 使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證鍵是否存在。

**判斷依據**：diff 第 52-56 行，直接使用 `pr[...]` 而沒有檢查鍵是否存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，且未處理寫入錯誤</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，如果 `write` 過程中發生例外（例如磁碟滿、權限不足），檔案不會被正確關閉，可能造成資源洩漏或檔案內容不完整。

具體情境：
- 寫入到唯讀目錄或磁碟空間不足時，`open` 或 `write` 會拋出例外，但 `f.close()` 不會被執行。

建議：
- 使用 `with open(path, "w") as f:` 確保檔案總是被關閉。

**判斷依據**：diff 第 58-62 行，手動開啟和關閉檔案，沒有使用 context manager。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:77</code> archive 函式未檢查 subprocess.run 的回傳值</summary>

`subprocess.run` 預設不會在子程序失敗時拋出例外，而是回傳一個 `CompletedProcess` 物件，其中 `returncode` 屬性表示退出碼。這裡沒有檢查 `returncode`，所以即使 `tar` 或 `gh` 指令失敗，程式也會繼續執行並回報成功。

具體情境：
- 如果 `tar` 因為路徑不存在而失敗，程式不會察覺，後續的 `print` 仍會顯示成功訊息。

建議：
- 檢查 `returncode`，或使用 `subprocess.run(..., check=True)` 在失敗時拋出例外。

**判斷依據**：diff 第 61 行，未檢查 `subprocess.run` 的回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2503 ｜ PR #12</sub>