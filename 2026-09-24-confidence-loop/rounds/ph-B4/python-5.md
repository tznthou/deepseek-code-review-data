<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個從 GitHub API 撈取 PR 資料並計算指標的 Python 小工具。主要風險集中在安全性與正確性：`_fetch` 吞掉所有例外且未檢查回應狀態，可能導致後續程式碼因 `None` 或缺少鍵而崩潰；`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險；`collect_authors` 使用可變預設值 `seen=[]`，跨呼叫會累積資料；`export_csv` 未使用 `with` 管理檔案資源；`threshold_from_env` 未處理環境變數轉型失敗。建議優先修復命令注入與例外處理，再處理可變預設值與資源管理。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | 命令注入風險：`archive` 使用 `shell=True` 且拼接外部輸入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:22` | `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 `seen=[]` 導致跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:31` | `_fetch` 回傳 `None` 時未處理，導致後續程式碼崩潰 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | `threshold_from_env` 未處理環境變數轉型失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 管理檔案資源 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:77` | `archive` 未檢查 `subprocess.run` 回傳值 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:24` | `_fetch` 使用裸 `except:` 捕捉所有例外 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> 命令注入風險：`archive` 使用 `shell=True` 且拼接外部輸入</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`repo` 與 `path` 皆來自使用者輸入（命令列參數或衍生字串）。攻擊者可注入額外 shell 指令，例如 `repo` 設為 `x; rm -rf /` 或 `path` 包含特殊字元。建議改用參數列表形式並避免 `shell=True`，或至少對輸入進行嚴格驗證與轉義。

**判斷依據**：diff 第 104 行（新增側）顯示 `subprocess.run` 使用 `shell=True` 且命令字串由 f-string 拼接 `repo` 與 `path`，兩者皆非受信任輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:22</code> `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼</summary>

`_fetch` 的 `except: pass` 會捕捉所有例外（包含 `KeyboardInterrupt`、`SystemExit`），且未檢查 `resp.status`。若 API 回傳 404、500 或網路錯誤，函式回傳 `None`，後續 `pr["user"]` 等操作將拋出 `TypeError` 或 `KeyError`，且無任何錯誤訊息。建議至少記錄錯誤並重新拋出，或回傳明確的錯誤物件，並檢查回應狀態碼。

**判斷依據**：diff 第 22-24 行顯示 `_fetch` 的 `try` 區塊內呼叫 `urlopen`，但 `except` 子句僅 `pass`，且未檢查 `resp.status`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 `seen=[]` 導致跨呼叫累積資料</summary>

`collect_authors(repo, numbers, seen=[])` 使用可變預設值。若呼叫者未傳入 `seen`，則所有呼叫共用同一個 list，導致作者名單不斷累積，且可能在不同呼叫間洩漏資料。建議改為 `seen=None` 並在函式內初始化為空 list。

**判斷依據**：diff 第 29 行顯示函式定義使用 `seen=[]` 作為預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:31</code> `_fetch` 回傳 `None` 時未處理，導致後續程式碼崩潰</summary>

`_fetch` 在例外時回傳 `None`，但 `collect_authors` 與 `main` 中直接使用 `pr["user"]["login"]` 等鍵值存取。若 API 失敗，程式將拋出 `TypeError` 或 `KeyError`，且無任何錯誤訊息。建議在呼叫處檢查回傳值是否為 `None` 或改用例外傳播。

**判斷依據**：diff 第 31-32 行顯示 `_fetch` 回傳值直接以 `pr["user"]` 存取，未檢查 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> `threshold_from_env` 未處理環境變數轉型失敗</summary>

`int(raw)` 若環境變數 `PR_STALE_DAYS` 不是有效整數（例如空字串、非數字），將拋出 `ValueError` 且未捕捉，導致程式崩潰。建議使用 `try/except` 或提供預設值。

**判斷依據**：diff 第 44 行顯示直接對環境變數值呼叫 `int()`，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 管理檔案資源</summary>

`open(path, "w")` 後手動 `close()`，若寫入過程拋出例外，檔案控制代碼不會被關閉，可能導致資源洩漏。建議改用 `with open(...) as f:` 確保自動關閉。

**判斷依據**：diff 第 57-61 行顯示檔案操作未使用 `with` 語句。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:77</code> `archive` 未檢查 `subprocess.run` 回傳值</summary>

`subprocess.run` 預設不拋出例外，若 `tar` 或 `gh` 指令失敗（例如路徑不存在、權限不足），程式仍會繼續執行並回報成功。建議檢查 `returncode` 或使用 `check=True`。

**判斷依據**：diff 第 64 行顯示 `subprocess.run` 未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:24</code> `_fetch` 使用裸 `except:` 捕捉所有例外</summary>

裸 `except:` 會捕捉 `KeyboardInterrupt` 和 `SystemExit`，可能導致程式無法正常中斷。建議至少改為 `except Exception:` 並記錄錯誤。

**判斷依據**：diff 第 24 行顯示裸 `except:`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1923 ｜ PR #12</sub>