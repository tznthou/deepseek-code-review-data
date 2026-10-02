<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源管理（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議先修復 blocker 等級的錯誤處理與安全性問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:26` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 未處理轉換失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions、changed_files、title 欄位 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:26</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 或 `pr["additions"]` 會拋出 `TypeError`，導致程式崩潰。

建議：
- 至少記錄錯誤（logging）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼（例如 `resp.status != 200` 時拋出例外）。
- 避免使用裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError` 等）。

**判斷依據**：diff 第 26 行：`except:` 後直接 `pass`，且函式無回傳值，呼叫端未檢查。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo`（來自命令列參數）和 `path`（由 repo 衍生）。攻擊者可提供惡意的 repo 名稱（例如 `foo; rm -rf /`）來執行任意指令。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若必須使用 shell，請對輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 73 行：`shell=True` 且 f-string 包含 `repo` 和 `path`，兩者皆來自外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，每次呼叫都會共用同一個 list。若多次呼叫此函式（例如在同一個程序內處理多個 repo），先前的作者會被保留，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 31 行：`seen=[]` 為可變預設值，且函式內有 `seen.append(...)` 修改該 list。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。

建議：使用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 66-70 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 未處理轉換失敗</summary>

`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為整數，若使用者設定非數字字串（例如 `abc`），會拋出 `ValueError` 導致程式崩潰。

建議：捕捉 `ValueError` 並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 44 行：`int(raw)` 無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions、changed_files、title 欄位</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 GitHub API 的回應可能缺少這些欄位（例如某些事件或權限不足時），導致 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證欄位存在。

**判斷依據**：diff 第 48-53 行：直接使用鍵值存取，無防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 欄位，會拋出 `KeyError`。此外，若 `events` 只有一個元素，`first` 和 `last` 相同，回傳 0，可能無法反映實際延遲。

建議：檢查每個事件是否有 `created_at`，或使用 `events[0].get("created_at")` 並處理缺失。

**判斷依據**：diff 第 36-37 行：直接存取鍵值，無防護。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1940 ｜ PR #12</sub>