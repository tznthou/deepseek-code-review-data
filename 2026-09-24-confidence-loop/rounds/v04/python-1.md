<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及缺少輸入驗證。最該先修的是 _fetch 的例外處理和 archive 的 shell 注入問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 PR 一定有 additions 和 changed_files 欄位 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，且未處理寫入錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件有 created_at 欄位 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:48` | _to_epoch 使用 fromisoformat 可能無法解析所有 ISO 8601 格式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict，若 `_fetch` 回傳 `None`，後續 `pr["user"]` 或 `pr["additions"]` 會拋出 `TypeError`。此外，裸 `except:` 也會攔截 `KeyboardInterrupt` 和 `SystemExit`。

建議：
- 至少記錄錯誤並重新拋出，或回傳明確的錯誤值。
- 使用具體的例外型別（如 `urllib.error.URLError`, `json.JSONDecodeError`）。
- 考慮使用 `raise ... from err` 保留原始追蹤。

**判斷依據**：diff 第 24 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這兩個參數來自命令列參數或計算結果，可能包含惡意 shell 指令。例如，若 `repo` 為 `foo; rm -rf /`，則會執行任意指令。

建議：
- 避免使用 `shell=True`，改用參數列表形式：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```
- 若必須使用 shell，請對輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 74 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態</summary>

`collect_authors` 的 `seen` 參數預設為空 list，這是可變預設值。每次呼叫若未提供 `seen`，會共用同一個 list 物件，導致先前呼叫的結果殘留。例如：
```python
collect_authors('repo', [1])  # 回傳 ['user1']
collect_authors('repo', [2])  # 回傳 ['user1', 'user2']，而不是 ['user2']
```
建議改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 29 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

`threshold_from_env` 直接將 `PR_STALE_DAYS` 環境變數轉為 `int`，若該變數不是有效整數（例如設為 `abc`），會拋出 `ValueError` 且未處理，導致程式崩潰。

建議：
- 使用 try/except 捕捉 `ValueError`，並提供預設值或明確錯誤訊息。
- 或使用 `int(raw)` 前先驗證格式。

**判斷依據**：diff 第 39 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 一定有 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能因權限或 API 版本而缺少這些欄位（例如使用精簡版回應）。若欄位不存在，會拋出 `KeyError`。

建議：
- 使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)` 提供預設值。
- 或先驗證回應結構。

**判斷依據**：diff 第 44-46 行：直接使用鍵值存取，未處理缺失。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，且未處理寫入錯誤</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限不足），檔案不會被正確關閉，可能造成資源洩漏或資料不完整。

建議：
- 使用 `with open(path, "w") as f:` 確保檔案關閉。
- 考慮使用 `csv` 模組處理 CSV 格式，避免欄位中包含逗號或換行時格式錯誤。

**判斷依據**：diff 第 55-59 行：手動 open/close，且未使用 with。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件有 created_at 欄位</summary>

`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 GitHub API 的 timeline 事件可能因類型不同而缺少 `created_at`（例如某些事件只有 `submitted_at`）。若欄位缺失，會拋出 `KeyError`。

建議：
- 使用 `events[0].get("created_at")` 並檢查是否為 None。
- 或過濾出有 `created_at` 的事件。

**判斷依據**：diff 第 62-63 行：直接存取鍵值，未處理缺失。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:48</code> _to_epoch 使用 fromisoformat 可能無法解析所有 ISO 8601 格式</summary>

`_to_epoch` 使用 `datetime.datetime.fromisoformat`，但 Python 的 `fromisoformat` 在較舊版本（<3.11）不支援所有 ISO 8601 格式（例如帶有 `Z` 的字串需要先替換，這裡有做，但可能還有其他變體）。若時間戳格式不符，會拋出 `ValueError`。

建議：
- 考慮使用 `datetime.datetime.strptime` 或 `dateutil.parser` 來處理更多格式。
- 或確保 API 回傳格式固定。

**判斷依據**：diff 第 68 行：依賴 `fromisoformat` 的解析能力。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 3200) ｜ completion tokens 2299 ｜ PR #12</sub>