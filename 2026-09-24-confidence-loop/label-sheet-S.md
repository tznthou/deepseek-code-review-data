# S 盲標單（不含 confidence、severity）

## S01 ｜ py-3way ｜ `sandbox/pr_stats.py:24`

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且錯誤訊息不明確。建議：記錄錯誤並重新拋出，或回傳明確的錯誤物件，讓呼叫端處理。

evidence：diff 第 24 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

## S02 ｜ py-3way ｜ `sandbox/pr_stats.py:77`

**archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中的 `repo` 來自命令列參數，攻擊者可注入任意 shell 指令（例如 `repo` 設為 `; rm -rf /`）。建議避免使用 `shell=True`，改用參數列表傳遞，並驗證輸入。

evidence：diff 第 55 行：`shell=True` 且指令字串包含外部輸入 `repo`。

## S03 ｜ py-3way ｜ `sandbox/pr_stats.py:29`

**可變預設值 seen=[] 導致跨呼叫狀態污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。若多次呼叫此函式，先前呼叫的結果會殘留，導致作者列表重複或包含非本次 PR 的作者。建議改為 `seen=None`，並在函式內初始化為空 list。

evidence：diff 第 27 行：`seen=[]` 是可變預設值。

## S04 ｜ py-3way ｜ `sandbox/pr_stats.py:40`

**review_latency 假設 timeline 事件存在且有序**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但若 timeline 中的事件缺少 `created_at` 欄位，或事件順序未按時間排序，計算出的延遲可能不正確。建議驗證事件結構並確保排序，或使用更可靠的 API 端點。

evidence：diff 第 31-32 行：直接索引事件列表，未檢查事件內容。

## S05 ｜ py-3way ｜ `sandbox/pr_stats.py:54`

**threshold_from_env 的 int() 轉換可能拋出未處理的例外**

existing_code:
```
return {"days": int(raw)}
```

body：`int(raw)` 在環境變數 `PR_STALE_DAYS` 不是有效整數時會拋出 `ValueError`，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

evidence：diff 第 38 行：直接轉換環境變數，未處理轉換失敗。

## S06 ｜ py-3way ｜ `sandbox/pr_stats.py:69`

**export_csv 未使用 with 管理檔案，且未處理寫入錯誤**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`export_csv` 使用 `open` 和 `close`，若寫入過程中發生例外，檔案可能未正確關閉。建議使用 `with open(...) as f:` 確保資源釋放。

evidence：diff 第 48-52 行：手動開啟和關閉檔案，未使用 context manager。

## S07 ｜ py-3way ｜ `sandbox/pr_stats.py:59`

**classify 假設 PR 物件包含 additions 和 changed_files 欄位**

existing_code:
```
if pr["additions"] > 500:
        return "large"
    elif pr["changed_files"] > 20:
```

body：`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能不包含這些欄位（例如使用不同版本的 API 或權限不足），導致 `KeyError`。建議使用 `pr.get()` 並提供預設值。

evidence：diff 第 42-43 行：直接索引可能不存在的鍵。

## S08 ｜ py-3way ｜ `sandbox/pr_stats.py:83`

**main 中重複呼叫 _fetch 取得相同 PR 資料**

existing_code:
```
authors = collect_authors(repo, numbers)
    stale = threshold_from_env()

    rows = []
    for n in numbers:
        pr = _fetch(f"/repos/{repo}/pulls/{n}")
```

body：`main` 先呼叫 `collect_authors` 取得作者列表，然後在迴圈中再次呼叫 `_fetch` 取得 PR 資料，造成不必要的 API 請求。建議一次取得所有 PR 資料並重用。

evidence：diff 第 60-64 行：重複的 API 呼叫。

## S09 ｜ py-3way ｜ `sandbox/pr_stats.py:97`

**輸出檔案路徑可能包含特殊字元，導致後續指令失敗**

existing_code:
```
out = f"/tmp/pr-stats-{repo.replace('/', '-')}.csv"
```

body：`out = f"/tmp/pr-stats-{repo.replace('/', '-')}.csv"` 中，`repo` 可能包含其他特殊字元（如空格、`;`），雖然在 `archive` 中作為參數傳給 shell 指令時可能造成問題。建議對路徑進行更嚴格的清理或使用臨時目錄。

evidence：diff 第 68 行：路徑由外部輸入組成，未完全清理。

## S10 ｜ py-r1 ｜ `sandbox/pr_stats.py:24`

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 函式中的 `except: pass` 會捕捉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不記錄或重新拋出。這使得呼叫端無法得知失敗，後續程式碼（如 `pr["user"]["login"]`）在 `pr` 為 `None` 或缺少鍵時會拋出 `TypeError` 或 `KeyError`，造成程式崩潰。建議至少記錄錯誤並重新拋出，或讓函式回傳 `None` 並在呼叫端檢查。

evidence：diff 第 24-25 行：`except:` 後僅有 `pass`，且函式無回傳值，呼叫端未檢查。

## S11 ｜ py-r1 ｜ `sandbox/pr_stats.py:77`

**archive 使用 shell=True 且拼接 repo，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 變數（來自命令列參數）。攻擊者可提供如 `repo='x; rm -rf /'` 的輸入來執行任意命令。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 72 行：`shell=True` 且 f-string 包含 `repo`。

## S12 ｜ py-r1 ｜ `sandbox/pr_stats.py:29`

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若多次呼叫此函式，作者名單會不斷累積，導致結果不正確。建議改為 `seen=None` 並在函式內初始化。

evidence：diff 第 29 行：`seen=[]` 為可變預設值。

## S13 ｜ py-r1 ｜ `sandbox/pr_stats.py:37`

**review_latency 假設 timeline 存在且非空，可能拋出例外**

existing_code:
```
events = pr.get("timeline", [])
    if not events:
        return 0
    first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `pr["timeline"]`，但 GitHub API 的回應中可能沒有 `timeline` 鍵（例如未請求該欄位），導致 `KeyError`。此外，若 `timeline` 為空，函式回傳 0，但呼叫端可能未預期此情況。建議使用 `pr.get("timeline", [])` 並處理空串列。

evidence：diff 第 34-38 行：`pr.get` 已處理缺失鍵，但後續 `events[0]` 和 `events[-1]` 在空串列時會拋出 `IndexError`，但此處有 `if not events` 保護，故風險較低。然而，若 `timeline` 存在但元素缺少 `created_at`，仍會拋出 `KeyError`。

## S14 ｜ py-r1 ｜ `sandbox/pr_stats.py:69`

**export_csv 未使用 with 管理檔案，可能洩漏資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`export_csv` 直接使用 `open` 和 `close`，若在寫入過程中發生例外，檔案可能未關閉。建議使用 `with open(path, 'w') as f:` 來確保資源釋放。

evidence：diff 第 66-70 行：未使用 context manager。

## S15 ｜ py-r1 ｜ `sandbox/pr_stats.py:59`

**classify 假設 PR 一定有 additions 和 changed_files 鍵**

existing_code:
```
if pr["additions"] > 500:
        return "large"
    elif pr["changed_files"] > 20:
```

body：`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 API 回應可能缺少這些鍵（例如權限不足或欄位未包含），導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式。

evidence：diff 第 51-53 行：直接索引字典。

## S16 ｜ py-r1 ｜ `sandbox/pr_stats.py:54`

**threshold_from_env 未處理環境變數轉型失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為整數，若值不是有效整數（如 "abc"），會拋出 `ValueError` 導致程式終止。建議捕捉例外並回退到預設值或提供明確錯誤訊息。

evidence：diff 第 45 行：`int(raw)` 未包在 try-except 中。

## S17 ｜ py-r1 ｜ `sandbox/pr_stats.py:81`

**main 未驗證命令列參數，可能導致 IndexError**

existing_code:
```
repo = sys.argv[1]
    numbers = sys.argv[2:]
```

body：`main` 直接使用 `sys.argv[1]` 和 `sys.argv[2:]`，若使用者未提供足夠參數，會拋出 `IndexError`。建議檢查參數數量並提供使用說明。

evidence：diff 第 82-83 行：未檢查 `len(sys.argv)`。

## S18 ｜ py-r2 ｜ `sandbox/pr_stats.py:24`

**`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼**

existing_code:
```
except:
        pass
```

body：`_fetch` 函式使用裸 `except: pass` 吞掉所有例外，包括網路錯誤、JSON 解析錯誤等。此外，它未檢查 HTTP 回應狀態碼，若 API 回傳 404 或 401，`json.loads` 仍會嘗試解析錯誤頁面，可能拋出例外而被吞掉，導致函式回傳 `None`。後續程式碼（如 `pr["user"]["login"]`）會因 `pr` 為 `None` 而拋出 `TypeError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

evidence：diff 第 22 行：`except:` 與 `pass`，且未檢查 `resp.status`。

## S19 ｜ py-r2 ｜ `sandbox/pr_stats.py:77`

**`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 參數（來自命令列參數）與 `path`（來自內部變數，但可能受環境影響）。攻擊者可提供惡意的 `repo` 值（例如 `; rm -rf /`）來執行任意命令。建議改用參數列表形式並移除 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 76 行：`shell=True` 且 f-string 包含 `repo` 變數。

## S20 ｜ py-r2 ｜ `sandbox/pr_stats.py:29`

**可變預設值 `seen=[]` 導致跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 函式的 `seen` 參數預設為空列表，這是一個可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致非預期行為。建議改為 `seen=None` 並在函式內初始化。

evidence：diff 第 31 行：`seen=[]`。

## S21 ｜ py-r2 ｜ `sandbox/pr_stats.py:69`

**`export_csv` 未使用 `with` 管理檔案資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`export_csv` 函式直接使用 `open` 和 `close`，若在寫入過程中發生例外，檔案可能未正確關閉，導致資源洩漏。建議改用 `with open(path, "w") as f:` 來確保檔案總會被關閉。

evidence：diff 第 78-82 行：手動 `open` 與 `close`。

## S22 ｜ py-r2 ｜ `sandbox/pr_stats.py:54`

**`threshold_from_env` 未處理環境變數轉換失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 函式直接使用 `int(raw)` 轉換環境變數 `PR_STALE_DAYS`，若該變數不是有效整數（例如設為 `abc`），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

evidence：diff 第 49 行：`int(raw)` 未包在 try-except 中。

## S23 ｜ py-r2 ｜ `sandbox/pr_stats.py:59`

**`classify` 假設 PR 一定有 `additions` 和 `changed_files` 欄位**

existing_code:
```
if pr["additions"] > 500:
```

body：`classify` 函式直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能因權限或 API 版本而缺少這些欄位，導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

evidence：diff 第 54 行：直接索引 `pr["additions"]`。

## S24 ｜ py-r2 ｜ `sandbox/pr_stats.py:37`

**`review_latency` 假設 `timeline` 事件存在且非空**

existing_code:
```
events = pr.get("timeline", [])
    if not events:
        return 0
    first = events[0]["created_at"]
```

body：`review_latency` 函式使用 `pr.get("timeline", [])` 取得事件列表，但若 `timeline` 欄位存在但為 `None`，則 `if not events` 會通過（因為 `None` 為假），但後續 `events[0]` 會拋出 `TypeError`。建議檢查 `events` 是否為列表且非空。

evidence：diff 第 40-43 行：`events` 可能為 `None`。

## S25 ｜ py-r3 ｜ `sandbox/pr_stats.py:22`

**`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、JSON 解析錯誤），且未檢查 HTTP 狀態碼（例如 404、401）。這會導致呼叫端在 API 失敗時拿到 `None`，後續程式碼（如 `pr["user"]["login"]`）會拋出 `TypeError` 或 `KeyError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

evidence：diff 第 22 行：`except:` 後直接 `pass`，且未檢查 `resp.status`。

## S26 ｜ py-r3 ｜ `sandbox/pr_stats.py:77`

**`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數，攻擊者可注入額外命令（例如 `repo` 設為 `x; rm -rf /`）。即使 `path` 是內部產生的，`repo` 仍完全由使用者控制。建議：改用參數列表形式（`subprocess.run(["tar", "czf", f"{path}.tgz", path])`），並分開執行 `gh` 命令，避免 `shell=True`。

evidence：diff 第 72 行：`shell=True` 且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

## S27 ｜ py-r3 ｜ `sandbox/pr_stats.py:29`

**`collect_authors` 使用可變預設參數 `seen=[]`**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 預設為空列表，但列表是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致資料污染。建議改為 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 27 行：可變預設參數。

## S28 ｜ py-r3 ｜ `sandbox/pr_stats.py:69`

**`export_csv` 未使用 `with` 開啟檔案，可能洩漏資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`f = open(path, "w")` 後手動 `f.close()`，若寫入過程拋出例外（例如磁碟滿、權限不足），檔案控制代碼不會被關閉，造成資源洩漏。建議使用 `with open(path, "w") as f:` 確保自動關閉。

evidence：diff 第 64-68 行：手動開啟與關閉檔案。

## S29 ｜ py-r3 ｜ `sandbox/pr_stats.py:54`

**`threshold_from_env` 未處理環境變數轉換例外**

existing_code:
```
return {"days": int(raw)}
```

body：`int(raw)` 可能拋出 `ValueError`（例如 `PR_STALE_DAYS=abc`），導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

evidence：diff 第 48 行：直接 `int(raw)` 未捕捉例外。

## S30 ｜ py-r3 ｜ `sandbox/pr_stats.py:37`

**`review_latency` 假設 `timeline` 欄位存在且非空**

existing_code:
```
events = pr.get("timeline", [])
    if not events:
        return 0
    first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`events = pr.get("timeline", [])` 若 `timeline` 不存在會回傳空列表，但後續 `events[0]` 和 `events[-1]` 在空列表時會拋出 `IndexError`。雖然目前有 `if not events: return 0` 保護，但若 `timeline` 存在但為空列表，仍會觸發。建議明確檢查 `if not events: return 0` 已足夠，但需確保 `timeline` 鍵存在時一定是列表。

evidence：diff 第 31-35 行：`events` 可能為空列表，但 `if not events` 已處理，此處為低風險。

## S31 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:47`

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 查詢**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱或 branch 名稱包含單引號，攻擊者可以注入任意 SQL 指令。例如，若 repo 名稱為 `x'; DROP TABLE runs; --`，則會執行 `DROP TABLE runs`。建議改用參數化查詢（sqlite3 支援 `?` 佔位符），或至少對輸入進行跳脫。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## S32 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:56`

**命令注入：`eval` 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 `$d`（`ls` 的輸出），可能包含惡意內容。例如，若 repo 目錄名稱為 `x; rm -rf /`，則會執行 `rm -rf /`。建議改用陣列或直接執行，避免 `eval`。

evidence：diff 第 51 行：`eval "$hook $repo"`

## S33 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:37`

**錯誤處理不足：`git checkout` 與 `git merge` 失敗後仍繼續執行**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`git checkout $BRANCH` 或 `git merge --ff-only` 失敗時，腳本仍會繼續執行後續的 `git rev-list` 與 SQL 插入，可能記錄錯誤的資料。建議檢查每個 git 指令的退出碼，失敗時跳過該 repo 或中止。

evidence：diff 第 31-32 行：`git checkout $BRANCH 2>>"$LOG"` 與 `git merge --ff-only "origin/$BRANCH" 2>>"$LOG"`

## S34 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:87`

**路徑處理不當：`ls` 輸出未處理空白或特殊字元**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出按空白分割，導致包含空白的目錄名稱被拆成多個 token。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

evidence：diff 第 61 行：`for d in $(ls "$ROOT"); do`

## S35 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:41`

**未檢查 `ahead` 是否為有效數字**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ...)` 若 git 指令失敗，`ahead` 可能為空字串或錯誤訊息，導致後續的 `[ "$ahead" -gt 0 ]` 比較出錯，或 SQL 插入失敗。建議檢查 git 指令的退出碼，並確保 `ahead` 是整數。

evidence：diff 第 35 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

## S36 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:62`

**`cleanup_cache` 使用 `rm -rf` 刪除快取，若 `$ROOT` 未正確設定可能造成災難**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 為空或未定義，可能刪除根目錄下的 `.cache`。建議檢查 `$ROOT` 是否為有效目錄，並避免使用 `rm -rf` 搭配變數。

evidence：diff 第 57 行：`rm -rf "$ROOT"/.cache/*`

## S37 ｜ sh-r1 ｜ `sandbox/repo_sync.sh:68`

**`summarize` 中的 `total` 可能包含非數字內容**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null || echo 0)
```

body：`total=$(grep -c . "$LOG" 2>/dev/null || echo 0)` 若 `grep` 失敗，`total` 可能為空字串，導致後續的 `[ "$total" -gt 100 ]` 比較出錯。建議確保 `total` 為整數。

evidence：diff 第 67 行：`total=$(grep -c . "$LOG" 2>/dev/null || echo 0)`

## S38 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:47`

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以字串拼接方式插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 參數來利用此漏洞。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成 `INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))`，導致資料表被刪除。

**建議修法**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫（如 `sqlite3` 的 `:memory:` 或使用 `printf '%q'`）。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經任何處理直接嵌入 SQL 字串。

## S39 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:56`

**命令注入：`eval` 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 皆來自外部輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元（如 `;`、`$(...)`、反引號），可導致任意命令執行。

**失敗情境**：若 `$ROOT` 為 `/tmp/evil; rm -rf /`，則 `eval` 會執行 `rm -rf /`。

**建議修法**：避免使用 `eval`，改為直接執行：`"$hook" "$repo"`，並確保 `$hook` 與 `$repo` 不包含特殊字元（可先驗證）。

evidence：diff 第 58 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

## S40 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:62`

**路徑處理不當：`cleanup_cache` 使用 `rm -rf` 搭配未驗證的 `$ROOT`**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空白或特殊字元，或使用者誤將 `$ROOT` 設為 `/`，可能導致災難性刪除。此外，`$ROOT` 未經驗證是否為預期目錄。

**失敗情境**：若 `$ROOT` 為 `/`，則會執行 `rm -rf //.cache/*`，可能刪除系統檔案。

**建議修法**：驗證 `$ROOT` 為絕對路徑且非根目錄，並使用更安全的刪除方式（如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

evidence：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`，`$ROOT` 未經驗證。

## S41 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:34`

**錯誤處理不足：`git` 指令失敗未檢查，可能導致後續操作基於錯誤狀態**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 函式中，`git fetch`、`git checkout`、`git merge` 的輸出僅重導向至 log，未檢查其退出碼。若 fetch 失敗（如網路問題），後續 checkout 或 merge 可能基於過時的遠端分支，導致錯誤的同步結果。

**失敗情境**：`git fetch` 因網路中斷失敗，但腳本繼續執行 `git checkout` 與 `git merge`，可能合併到舊的 commit，造成資料不一致。

**建議修法**：在每個 `git` 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo 或中止。

evidence：diff 第 34-36 行：三個 `git` 指令均未檢查退出碼。

## S42 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:87`

**效能問題：`for d in $(ls "$ROOT")` 使用 `ls` 解析目錄，且未處理含空白名稱**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式使用 `for d in $(ls "$ROOT")` 迭代目錄。`ls` 的輸出會進行分詞，若目錄名稱包含空白或換行，會被錯誤拆分。此外，`ls` 在大型目錄下可能較慢，且其輸出格式可能因環境而異。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致後續路徑錯誤。

**建議修法**：使用 `for d in "$ROOT"/*/; do` 或 `find "$ROOT" -maxdepth 1 -type d` 搭配 `while read` 迴圈，並正確處理空白。

evidence：diff 第 80 行：`for d in $(ls "$ROOT"); do`。

## S43 ｜ sh-r2 ｜ `sandbox/repo_sync.sh:88`

**變數作用域：`local` 使用於函式外，可能導致非預期行為**

existing_code:
```
local target="$ROOT/$d"
```

body：在 `main` 函式中，`local target="$ROOT/$d"` 使用了 `local`，但 `local` 僅能在函式內使用。此處 `main` 是函式，因此合法，但若未來重構將此段移出函式，會導致錯誤。此外，`local` 在 bash 中會遮蔽全域變數，可能造成混淆。

**建議修法**：若確定在函式內，可保留，但建議改用一般變數賦值，或明確註明。

evidence：diff 第 82 行：`local target="$ROOT/$d"`。

## S44 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:47`

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 查詢。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 語句。例如，若 repo 名稱為 `x'); DROP TABLE runs;--`，則會執行惡意 SQL。建議改用參數化查詢（例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`），或至少使用 `sqlite3` 的 `-quote` 選項或手動跳脫單引號。

evidence：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

## S45 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:56`

**使用 eval 執行 hook 可能導致命令注入**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval "$hook $repo"` 執行外部 hook。若 `$hook` 或 `$repo` 包含惡意內容（例如 repo 名稱包含 `; rm -rf /`），將導致任意命令執行。建議避免使用 `eval`，改為直接執行：`"$hook" "$repo"`。

evidence：第 51 行使用 eval 執行未受信任的輸入。

## S46 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:37`

**git checkout 與 merge 失敗時未中止，可能導致資料不一致**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 函式中，`git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導向至 log，未檢查退出碼。若 checkout 或 merge 失敗（例如 branch 不存在、合併衝突），後續仍會計算 ahead 並寫入資料庫，造成錯誤的同步狀態。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：第 28-29 行未檢查 git 指令的退出碼。

## S47 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:62`

**cleanup_cache 使用 rm -rf 可能誤刪重要檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議先驗證 `$ROOT` 存在且為目錄，並避免使用 `*` 萬用字元，或改用 `find` 搭配更嚴格的條件。

evidence：第 55 行直接刪除目錄內容，缺乏防護。

## S48 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:41`

**ahead 計算可能失敗，導致 SQL 插入空值**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若執行失敗（例如 origin/$BRANCH 不存在），`ahead` 將為空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查 `git rev-list` 的退出碼，失敗時設定預設值或跳過。

evidence：第 31 行未處理指令失敗的情況。

## S49 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:87`

**使用 ls 解析目錄名稱可能因特殊字元出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或萬用字元，將導致錯誤分割。建議改用 `for d in "$ROOT"/*/` 並搭配 `basename`，或使用 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：第 66 行使用 ls 輸出進行迴圈。

## S50 ｜ sh-r3 ｜ `sandbox/repo_sync.sh:87`

**未驗證 $ROOT 是否為有效目錄**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式未檢查 `$ROOT` 是否存在且為目錄。若使用者提供不存在的路徑，`ls` 會失敗，但腳本仍會繼續執行並嘗試進入不存在的目錄。建議在開頭加上 `[ -d "$ROOT" ] || { echo "錯誤：$ROOT 不是目錄" >&2; exit 1; }`。

evidence：第 66 行之前未驗證 $ROOT。
