<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及缺少輸入驗證。最該先修的是 _fetch 的例外處理和 archive 的 shell 注入，因為它們可能導致靜默失敗或任意指令執行。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:23` | 例外被完全吞掉，導致靜默失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令由外部輸入拼接，可能造成指令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 跨呼叫共用 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案開啟未使用 with，可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:72` | CSV 欄位未處理逗號或換行，可能破壞格式 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，可能洩漏 token | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:23</code> 例外被完全吞掉，導致靜默失敗</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外，包括網路錯誤、HTTP 錯誤、JSON 解析錯誤。呼叫端（`collect_authors` 和 `main`）會繼續執行，但 `pr` 可能是 `None`，後續 `pr["user"]` 會拋出 `TypeError`，且沒有原始錯誤資訊。建議至少記錄例外並重新拋出，或讓函式回傳 `None` 並在呼叫端檢查。

**判斷依據**：diff 第 23-24 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令由外部輸入拼接，可能造成指令注入</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`。`repo` 來自命令列參數，攻擊者可注入額外指令，例如 `repo = 'x; rm -rf /'`。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 62 行：`shell=True` 且 f-string 包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 跨呼叫共用</summary>

`collect_authors` 的 `seen=[]` 是可變預設值，每次呼叫都會累積到同一個 list，導致結果包含前一次呼叫的作者。例如第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`。建議改用 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行：函式定義使用可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError`，導致程式崩潰。如果 `PR_STALE_DAYS` 設為非數字字串，使用者會看到 traceback。建議捕捉例外並提供有意義的錯誤訊息，或使用預設值。

**判斷依據**：diff 第 36 行：`int(raw)` 未包在 try-except 中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案開啟未使用 with，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程拋出例外（例如磁碟滿），檔案不會被關閉。建議改用 `with open(path, 'w') as f:`。

**判斷依據**：diff 第 48 行：直接呼叫 `open` 而沒有使用 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:72</code> CSV 欄位未處理逗號或換行，可能破壞格式</summary>

`export_csv` 直接使用 f-string 寫入 CSV，若 `author` 或 `kind` 包含逗號或換行，會破壞 CSV 結構。建議使用 `csv` 模組的 writer。

**判斷依據**：diff 第 53 行：手動拼接 CSV 欄位，未做 escaping。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，可能洩漏 token</summary>

`_fetch` 從環境變數讀取 `GITHUB_TOKEN` 並直接放入 header，若請求被記錄或發生例外，token 可能外洩。建議使用更安全的方式管理憑證，例如從 keyring 讀取。

**判斷依據**：diff 第 21 行：直接使用環境變數作為敏感 header。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1497 ｜ PR #12</sub>