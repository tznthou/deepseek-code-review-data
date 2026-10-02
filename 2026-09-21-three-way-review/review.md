<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 的指令注入、token 可能外洩）、以及可變預設值導致的狀態污染。建議先修正這些問題再合併。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態污染 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的例外 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，且未處理寫入錯誤 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 PR 物件包含 additions 和 changed_files 欄位 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:83` | main 中重複呼叫 _fetch 取得相同 PR 資料 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:97` | 輸出檔案路徑可能包含特殊字元，導致後續指令失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且錯誤訊息不明確。建議：記錄錯誤並重新拋出，或回傳明確的錯誤物件，讓呼叫端處理。

**判斷依據**：diff 第 24 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中的 `repo` 來自命令列參數，攻擊者可注入任意 shell 指令（例如 `repo` 設為 `; rm -rf /`）。建議避免使用 `shell=True`，改用參數列表傳遞，並驗證輸入。

**判斷依據**：diff 第 55 行：`shell=True` 且指令字串包含外部輸入 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態污染</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。若多次呼叫此函式，先前呼叫的結果會殘留，導致作者列表重複或包含非本次 PR 的作者。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 27 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序</summary>

`review_latency` 直接存取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但若 timeline 中的事件缺少 `created_at` 欄位，或事件順序未按時間排序，計算出的延遲可能不正確。建議驗證事件結構並確保排序，或使用更可靠的 API 端點。

**判斷依據**：diff 第 31-32 行：直接索引事件列表，未檢查事件內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的例外</summary>

`int(raw)` 在環境變數 `PR_STALE_DAYS` 不是有效整數時會拋出 `ValueError`，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 38 行：直接轉換環境變數，未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，且未處理寫入錯誤</summary>

`export_csv` 使用 `open` 和 `close`，若寫入過程中發生例外，檔案可能未正確關閉。建議使用 `with open(...) as f:` 確保資源釋放。

**判斷依據**：diff 第 48-52 行：手動開啟和關閉檔案，未使用 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 物件包含 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能不包含這些欄位（例如使用不同版本的 API 或權限不足），導致 `KeyError`。建議使用 `pr.get()` 並提供預設值。

**判斷依據**：diff 第 42-43 行：直接索引可能不存在的鍵。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:83</code> main 中重複呼叫 _fetch 取得相同 PR 資料</summary>

`main` 先呼叫 `collect_authors` 取得作者列表，然後在迴圈中再次呼叫 `_fetch` 取得 PR 資料，造成不必要的 API 請求。建議一次取得所有 PR 資料並重用。

**判斷依據**：diff 第 60-64 行：重複的 API 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:97</code> 輸出檔案路徑可能包含特殊字元，導致後續指令失敗</summary>

`out = f"/tmp/pr-stats-{repo.replace('/', '-')}.csv"` 中，`repo` 可能包含其他特殊字元（如空格、`;`），雖然在 `archive` 中作為參數傳給 shell 指令時可能造成問題。建議對路徑進行更嚴格的清理或使用臨時目錄。

**判斷依據**：diff 第 68 行：路徑由外部輸入組成，未完全清理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3255 (cache hit 2432) ｜ completion tokens 1988</sub>