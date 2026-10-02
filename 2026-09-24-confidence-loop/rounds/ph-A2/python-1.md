<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於：錯誤處理幾乎完全缺失（_fetch 吞掉所有例外、export_csv 未關檔、archive 使用 shell=True 拼接指令），以及多個正確性問題（可變預設值、review_latency 依賴不存在的 timeline 欄位、classify 假設 additions/changed_files 存在）。最該先修的是 _fetch 的錯誤處理與 archive 的指令注入風險。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，呼叫端無法得知失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 依賴不存在的 timeline 欄位，永遠回傳 0 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 additions 和 changed_files 存在，可能 KeyError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能未關閉 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出 ValueError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | GITHUB_TOKEN 可能不存在，導致 KeyError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，呼叫端無法得知失敗</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors`、`main`）會直接對回傳值做 `pr["user"]` 或 `pr["additions"]`，導致 `TypeError: 'NoneType' object is not subscriptable` 或 `KeyError`。此外，裸 `except:` 也會攔截 `KeyboardInterrupt` 和 `SystemExit`。

建議：
- 至少記錄錯誤並重新拋出，或回傳明確的錯誤值。
- 使用 `except Exception as e:` 並 `raise` 或 `return None`，讓呼叫端處理。
- 考慮使用 `urllib.error.HTTPError` 處理非 200 狀態碼。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數（`sys.argv`），攻擊者可注入任意 shell 指令。例如 `repo` 設為 `x; rm -rf /` 會執行刪除指令。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 若必須使用 shell，請對輸入進行嚴格驗證或使用 `shlex.quote`。

**判斷依據**：diff 第 73 行：`shell=True` 且 f-string 包含外部輸入 `path` 和 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積</summary>

`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值是一個 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若呼叫多次，作者會被重複加入，且無法清空。

建議：
- 改為 `seen=None`，在函式內 `if seen is None: seen = []`。

**判斷依據**：diff 第 28 行：可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 依賴不存在的 timeline 欄位，永遠回傳 0</summary>

`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中沒有 `timeline` 欄位（需另外請求 `/issues/{n}/timeline` 或使用 `events_url`）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。

建議：
- 使用正確的 API 端點取得事件，或改用 `created_at` 和 `updated_at` 計算。

**判斷依據**：diff 第 35 行：`pr.get("timeline", [])`，但 `_fetch` 只呼叫 `/pulls/{n}`，回應中無 `timeline`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 additions 和 changed_files 存在，可能 KeyError</summary>

`pr["additions"]` 和 `pr["changed_files"]` 直接取值，但若 API 回應缺少這些欄位（例如權限不足或 API 變更），會拋出 `KeyError`。

建議：
- 使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)`，或先驗證欄位存在。

**判斷依據**：diff 第 58-60 行：直接使用 `pr["additions"]` 和 `pr["changed_files"]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能未關閉</summary>

`f = open(path, "w")` 後若 `f.write` 拋出例外（例如磁碟滿），檔案不會被關閉，造成資源洩漏。

建議：
- 使用 `with open(path, "w") as f:` 確保檔案關閉。

**判斷依據**：diff 第 68-72 行：手動 open/close，無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出 ValueError</summary>

`int(raw)` 若環境變數 `PR_STALE_DAYS` 不是有效整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式崩潰。

建議：
- 使用 try/except 捕捉轉換錯誤，或提供預設值。

**判斷依據**：diff 第 48 行：`int(raw)` 無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> GITHUB_TOKEN 可能不存在，導致 KeyError</summary>

`os.environ["GITHUB_TOKEN"]` 若環境變數未設定，會拋出 `KeyError`。

建議：
- 使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 None，或提供明確錯誤訊息。

**判斷依據**：diff 第 21 行：直接存取環境變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2098 ｜ PR #12</sub>