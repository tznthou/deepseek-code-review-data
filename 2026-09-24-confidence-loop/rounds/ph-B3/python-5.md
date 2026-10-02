<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險在於：錯誤處理幾乎完全缺失（_fetch 吞掉所有例外、export_csv 未關檔、archive 使用 shell=True 且未檢查回傳值）、可變預設值 seen=[] 造成跨呼叫污染、以及環境變數轉型失敗未處理。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 對環境變數做 int() 轉換，未處理 ValueError | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:63` | classify 使用 startswith("fix") 判斷，可能誤分類 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致回傳 `None`。呼叫端（`collect_authors` 與 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，會拋出 `TypeError` 或 `AttributeError`。例如：GitHub API 回 404（PR 不存在）時，`urlopen` 會拋出 `HTTPError`，被吞掉後 `pr` 為 `None`，下一行 `pr["user"]` 就崩潰。建議：至少記錄錯誤並重新拋出，或讓呼叫端檢查 `None`。

**判斷依據**：diff 第 25-26 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值被 `collect_authors` 和 `main` 直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串由外部輸入拼接，存在命令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`repo` 來自命令列參數（使用者可控），且 `path` 由 `repo` 衍生。攻擊者可注入額外 shell 指令，例如 `repo` 設為 `x; rm -rf /`。即使 `repo` 來自內部，使用 `shell=True` 也容易因特殊字元出錯。建議改用參數列表形式，避免 `shell=True`，並將 `tar` 與 `gh` 分開呼叫。

**判斷依據**：diff 第 70 行：`shell=True` 且 f-string 包含 `repo` 與 `path`，兩者皆受外部輸入影響。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼</summary>

`open(path, "w")` 後手動 `close()`，若寫入過程拋出例外（例如磁碟滿、權限不足），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 63-67 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`def collect_authors(repo, numbers, seen=[])` 的預設值 `[]` 在函式定義時建立一次，之後每次呼叫都會沿用同一個 list。若函式被多次呼叫（例如測試或迴圈中），`seen` 會不斷累積，導致結果包含前次呼叫的作者。建議改為 `seen=None`，在函式內初始化。

**判斷依據**：diff 第 30 行：可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 對環境變數做 int() 轉換，未處理 ValueError</summary>

`int(raw)` 若 `PR_STALE_DAYS` 不是合法整數（例如設為 `abc`），會拋出 `ValueError` 且未捕捉，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 48 行：直接 `int(raw)`，無 try/except。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:63</code> classify 使用 startswith("fix") 判斷，可能誤分類</summary>

`pr["title"].startswith("fix")` 會將標題開頭為 `fix` 但實際不是修復的 PR（例如 `fixation`）歸類為 `fix`。建議使用更精確的判斷，例如正規表示式或檢查完整單字。

**判斷依據**：diff 第 53 行：`startswith("fix")` 過於寬鬆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1535 ｜ PR #12</sub>