<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於安全性（shell=True 指令注入、token 可能外洩）、錯誤處理（_fetch 吞掉所有例外）、以及可變預設值導致的狀態累積。建議先修復 archive 的指令注入與 _fetch 的錯誤處理，再考慮合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入造成指令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 的預設值為可變字典，且 int() 轉換可能拋出例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且未檢查子程序回傳值 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入造成指令注入</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 與 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`。建議改用參數陣列並移除 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 88 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`（第 82 行），未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except` 區塊只有 `pass`，當網路錯誤、API 回傳非 2xx、或 JSON 解析失敗時，函式會回傳 `None`。呼叫端（如 `collect_authors` 第 31 行、`main` 第 94 行）直接對回傳值做 `pr["user"]` 或 `pr["additions"]`，會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或讓呼叫端處理 `None`。

**判斷依據**：diff 第 24-25 行：`except:` 後僅 `pass`，且第 31 行 `pr["user"]["login"]` 未檢查 `pr` 是否為 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態累積</summary>

`collect_authors` 的參數 `seen` 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，造成非預期行為。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 29 行：`def collect_authors(repo, numbers, seen=[]):`，且函式內有 `seen.append(...)`（第 31 行），會修改預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 的預設值為可變字典，且 int() 轉換可能拋出例外</summary>

`threshold_from_env` 的參數 `default` 預設為 `{"days": 7}`，是可變字典，若函式內修改它會影響後續呼叫（目前未修改，但風險存在）。另外，`int(raw)` 若環境變數不是整數會拋出 `ValueError`，導致程式崩潰。建議改用不可變預設值並處理轉換錯誤。

**判斷依據**：diff 第 45 行：`def threshold_from_env(default={"days": 7}):`，且第 48 行 `int(raw)` 未捕捉例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且未檢查子程序回傳值</summary>

即使不考慮注入，`subprocess.run` 未設定 `check=True`，若 `tar` 或 `gh` 指令失敗，程式仍會繼續執行並回報成功。建議加上 `check=True` 或檢查回傳碼。

**判斷依據**：diff 第 88 行：`subprocess.run(...)` 未指定 `check=True`，也未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError</summary>

`os.environ["GITHUB_TOKEN"]` 若環境變數未設定會拋出 `KeyError`，且錯誤訊息可能洩漏 token 的存在性。建議使用 `os.environ.get` 並提供明確錯誤訊息。

**判斷依據**：diff 第 21 行：直接存取 `os.environ["GITHUB_TOKEN"]`，未處理缺失情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close`，若寫入過程拋出例外，檔案不會被關閉。建議改用 `with open(...) as f:`。

**判斷依據**：diff 第 61-65 行：手動開啟與關閉檔案，未使用 context manager。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1705 ｜ PR #12</sub>