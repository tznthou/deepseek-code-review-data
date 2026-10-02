# ph-A2 人工標記單（盲標：不含 confidence、severity）

自動 60 筆、人工 29 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-A2:python:1:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，呼叫端無法得知失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors`、`main`）會直接對回傳值做 `pr["user"]` 或 `pr["additions"]`，導致 `TypeError: 'NoneType' object is not subscriptable` 或 `KeyError`。此外，裸 `except:` 也會攔截 `KeyboardInterrupt` 和 `SystemExit`。

建議：
- 至少記錄錯誤並重新拋出，或回傳明確的錯誤值。
- 使用 `except Exception as e:` 並 `raise` 或 `return None`，讓呼叫端處理。
- 考慮使用 `urllib.error.HTTPError` 處理非 200 狀態碼。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A2:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3, PY-A4

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值是一個 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若呼叫多次，作者會被重複加入，且無法清空。

建議：
- 改為 `seen=None`，在函式內 `if seen is None: seen = []`。

evidence：diff 第 28 行：可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A2:python:1:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 依賴不存在的 timeline 欄位，永遠回傳 0**

existing_code:
```
events = pr.get("timeline", [])
```

body：`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中沒有 `timeline` 欄位（需另外請求 `/issues/{n}/timeline` 或使用 `events_url`）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。

建議：
- 使用正確的 API 端點取得事件，或改用 `created_at` 和 `updated_at` 計算。

evidence：diff 第 35 行：`pr.get("timeline", [])`，但 `_fetch` 只呼叫 `/pulls/{n}`，回應中無 `timeline`。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A2:python:2:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**例外被完全吞掉，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx 狀態碼或 JSON 解析失敗時，函式會回傳 None。呼叫端（collect_authors 和 main）直接對回傳值進行索引或屬性存取，例如 pr["user"]["login"]，會引發 TypeError 或 KeyError，且錯誤訊息不明確。

建議：至少記錄例外（logging.exception），或重新拋出，讓呼叫端能處理。若希望函式回傳 None，呼叫端應檢查 None 並提供明確錯誤訊息。

evidence：diff 第 24-25 行顯示 except: pass，且後續 collect_authors 與 main 直接使用 pr["user"]["login"] 等索引。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A2:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設參數 seen=[] 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：collect_authors 的 seen 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若多次呼叫 collect_authors 而未傳入 seen，結果會累積先前呼叫的作者，導致資料污染。

建議：使用 None 作為預設值，並在函式內初始化為空串列。

evidence：diff 第 28 行顯示 seen=[]。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A2:python:2:5 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 依賴不存在的 timeline 欄位，可能引發 KeyError**

existing_code:
```
events = pr.get("timeline", [])
```

body：review_latency 使用 pr.get("timeline", [])，但 GitHub Pull Request API 的回應中沒有 timeline 欄位（timeline 是另一個 API 端點）。因此 events 永遠為空，函式回傳 0，無法計算實際延遲。若未來 API 變更，可能導致 KeyError。

建議：確認正確的 API 端點或欄位，或明確處理缺失情況。

evidence：diff 第 35 行顯示 pr.get("timeline", [])。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A2:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 `seen=[]` 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。在 Python 中，預設值只會在函式定義時建立一次，之後每次呼叫若未提供 `seen` 參數，都會共用同一個 list。這會導致多次呼叫 `collect_authors` 時，作者名單會不斷累積，而不是每次重新開始。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 30 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A2:python:3:5 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**`review_latency` 計算邏輯可能不正確**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 從 `pr.get("timeline", [])` 取得事件列表，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位（需要另外請求 timeline API）。因此 `events` 會是空列表，函式回傳 0，導致延遲指標永遠為 0。

建議：確認 API 回應是否包含 timeline，若無則需額外請求或改用其他欄位（如 `created_at` 和 `updated_at`）。

evidence：diff 第 34 行：`pr.get("timeline", [])` 但 GitHub PR API 回應中沒有 `timeline` 欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A2:python:4:5 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 假設 pr 有 timeline 欄位，但 API 回應可能沒有**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub Pull Request API 的回應中並不一定包含 `timeline` 欄位（除非特別要求）。若 `timeline` 不存在，`events` 會是空 list，函式回傳 0，但這可能不是真正的延遲。

失敗情境：呼叫 `_fetch` 取得 PR 資料時，若未要求 timeline，`pr` 中沒有 `timeline` 鍵，`review_latency` 回傳 0，導致 CSV 中的 latency 欄位全部為 0，失去統計意義。

建議：確認 API 回應結構，或明確處理缺少 timeline 的情況（例如回傳 None 或拋出例外）。

evidence：diff 第 34 行：使用 `get` 提供預設值，但未檢查 `timeline` 是否為有效資料。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A2:python:4:7 ｜ `sandbox/pr_stats.py:72` ｜ 候選：無

**main 中重複呼叫 _fetch，且未檢查回傳值**

existing_code:
```
pr = _fetch(f"/repos/{repo}/pulls/{n}")
```

body：`main` 在迴圈中對每個 PR 呼叫 `_fetch`，但 `_fetch` 可能回傳 `None`（因為錯誤被吞掉），導致後續 `pr["user"]` 拋出 `TypeError`。此外，`collect_authors` 已經呼叫過 `_fetch`，這裡又重複呼叫，造成不必要的 API 請求。

失敗情境：若某個 PR 的 API 請求失敗，`_fetch` 回傳 `None`，`pr["user"]` 拋出 `TypeError`，程式崩潰。

建議：在 `_fetch` 中讓錯誤向上傳播，或在 `main` 中檢查回傳值。另外，可以考慮重用 `collect_authors` 的結果，避免重複請求。

evidence：diff 第 72 行：直接使用 `_fetch` 的回傳值，未檢查是否為 `None`。

- 規則提示 PY-A6：open 沒用 with

## ph-A2:python:4:8 ｜ `sandbox/pr_stats.py:77` ｜ 候選：無

**archive 中的 gh repo view 可能將 token 暴露在命令列**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 執行 `gh repo view {repo}`，而 `gh` 命令可能使用環境變數中的 `GITHUB_TOKEN` 進行認證。在某些系統上，命令列參數可能被其他使用者透過 `ps` 看到，導致 token 外洩。

失敗情境：在多使用者系統上，其他使用者可以透過 `ps aux` 看到 `gh repo view` 的參數，若 `gh` 將 token 作為參數傳遞（而非從環境變數讀取），token 會暴露。

建議：確認 `gh` 如何處理認證，避免在命令列中傳遞敏感資訊。

evidence：diff 第 63 行：指令中包含 `gh repo view {repo}`，可能涉及認證。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## ph-A2:python:4:9 ｜ `sandbox/pr_stats.py:97` ｜ 候選：PY-A7b, PY-K-tmp

**輸出檔案路徑可能包含特殊字元，導致命令注入或路徑問題**

existing_code:
```
out = f"/tmp/pr-stats-{repo.replace('/', '-')}.csv"
```

body：`out` 的檔名由 `repo` 替換 `/` 為 `-` 而來，但 `repo` 可能包含其他特殊字元（如 `;`、`&`、空格），在 `archive` 的 shell 指令中可能造成問題。

失敗情境：`repo` 為 `a; rm -rf /`，`out` 變成 `/tmp/pr-stats-a; rm -rf /.csv`，在 `archive` 的 shell 指令中可能被解釋為多個命令。

建議：對 `repo` 進行更嚴格的驗證或轉義，或避免在 shell 指令中使用未清理的輸入。

evidence：diff 第 78 行：`repo` 未經過完整清理，僅替換 `/`。

- 規則提示 PY-A7b：out 由 repo 組成、replace 只換 /，再進 archive 的 shell=True
- 規則提示 PY-K-tmp：固定、可預測的 /tmp 檔名

## ph-A2:python:5:1 ｜ `sandbox/pr_stats.py:27` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當成 dict 來存取鍵（例如 `pr["user"]["login"]`），當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，造成程式崩潰。

具體失敗情境：
- GitHub API 回傳 404（PR 不存在）或 401（token 無效）時，`urlopen` 會拋出 `HTTPError`，被 `except` 吞掉，`_fetch` 回傳 `None`，接著 `pr["user"]` 就會拋出 `TypeError: 'NoneType' object is not subscriptable`。
- 網路逾時或 DNS 失敗時，同樣會回傳 `None` 並導致後續崩潰。

建議：
- 讓 `_fetch` 在失敗時拋出例外（或回傳明確的錯誤值），並在呼叫端處理。
- 至少記錄錯誤訊息，不要完全靜默。

evidence：diff 第 27 行 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 31 行）和 `main`（第 73 行）被直接當成 dict 使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A2:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 seen=[] 導致跨呼叫狀態污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。Python 在函式定義時只建立一次該 list，之後每次呼叫都會共用同一個 list 物件。如果呼叫者沒有傳入 `seen`，多次呼叫會累積之前的結果。

具體情境：
- 在同一個 process 中呼叫 `collect_authors('repo', [1])` 兩次，第二次呼叫會回傳 `['user1', 'user1']` 而不是 `['user1']`。
- 這在測試或互動式環境中很容易造成難以追蹤的 bug。

建議：
- 改用 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 31 行，`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 33 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A2:python:5:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出未處理的例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
    raw = os.environ.get("PR_STALE_DAYS", "")
    if raw:
        return {"days": int(raw)}
```

body：`threshold_from_env` 的參數 `default={"days": 7}` 是可變預設值，雖然函式內沒有修改 `default`，但若未來修改就可能引入 bug。更嚴重的問題是 `int(raw)` 沒有處理轉換失敗：如果環境變數 `PR_STALE_DAYS` 不是整數（例如設為 `abc`），會拋出 `ValueError` 且沒有被捕捉，導致程式崩潰。

具體情境：
- 使用者設定 `PR_STALE_DAYS=abc`，程式在 `int(raw)` 處拋出 `ValueError`。

建議：
- 將預設值改為 `None` 並在函式內處理。
- 對 `int(raw)` 加上 try/except，或使用更安全的轉換方式。

evidence：diff 第 44-47 行，`default` 是可變 dict，且 `int(raw)` 未處理例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## ph-A2:python:5:7 ｜ `sandbox/pr_stats.py:77` ｜ 候選：無

**archive 函式未檢查 subprocess.run 的回傳值**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run` 預設不會在子程序失敗時拋出例外，而是回傳一個 `CompletedProcess` 物件，其中 `returncode` 屬性表示退出碼。這裡沒有檢查 `returncode`，所以即使 `tar` 或 `gh` 指令失敗，程式也會繼續執行並回報成功。

具體情境：
- 如果 `tar` 因為路徑不存在而失敗，程式不會察覺，後續的 `print` 仍會顯示成功訊息。

建議：
- 檢查 `returncode`，或使用 `subprocess.run(..., check=True)` 在失敗時拋出例外。

evidence：diff 第 61 行，未檢查 `subprocess.run` 的回傳值。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## ph-A2:shell:1:3 ｜ `sandbox/repo_sync.sh:37` ｜ 候選：SH-B1(unless)

**git checkout 未加引號，branch 名稱可能被 shell 展開**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 未將 `$BRANCH` 加上雙引號。雖然前面有格式驗證，但若 branch 名稱包含 glob 字元（例如 `*`）或空白（雖然格式驗證已排除空白），仍可能造成非預期行為。建議改為 `git checkout "$BRANCH"`。

evidence：第 34 行未對 `$BRANCH` 加引號。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-A2:shell:1:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能失敗，導致變數為空或非數字**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查指令是否成功，失敗時設定預設值或中止。

evidence：第 38 行未檢查 rev-list 的 exit code。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:shell:2:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆後插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成：
```sql
INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))
```
這會刪除 `runs` 資料表。

**建議**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式，並對輸入進行跳脫。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:shell:2:2 ｜ `sandbox/repo_sync.sh:56` ｜ 候選：SH-S2, SH-C1

**命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 repo 目錄名稱，可能包含 shell 特殊字元（例如 `; rm -rf ~`）。攻擊者若能在 repo 根目錄建立惡意名稱的目錄，即可執行任意命令。

**失敗情境**：假設 repo 目錄名稱為 `test; touch /tmp/pwned`，則 `eval` 會執行 `touch /tmp/pwned`。

**建議**：避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 都以引號包覆。

evidence：diff 第 52 行：`eval "$hook $repo"`

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:shell:4:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 可能為空字串，導致 SQL 寫入失敗或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。

建議在取得 ahead 後檢查是否為數字，若不是則設為 0 或中止處理。

evidence：第 38 行未處理 git 指令失敗時 ahead 為空的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:shell:4:7 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-S3

**SQL 寫入未處理 ahead 為非數字的情況**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：即使 ahead 為空或非數字，SQL 插入仍會執行，可能導致資料庫寫入失敗或寫入錯誤資料。建議在寫入前驗證 ahead 為整數。

evidence：第 42 行未對 ahead 進行型別檢查。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:shell:5:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若指令失敗（例如 branch 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入會失敗。建議檢查 ahead 是否為數字，失敗時設為 0 或中止。

evidence：第 34 行未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A2:probe:1:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 是第一個 tag 時會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 會是 0，`0 - 1` 變成 -1，`tags[-1]` 會取到最後一個 tag，而不是報錯。這會導致 release notes 的範圍錯誤（從最後一個 tag 到第一個 tag）。

建議：檢查 `tags.index(tag) == 0` 時，提示使用者這是第一個 tag，沒有前一個 tag 可以比較。

evidence：diff 中 `main` 函式的這一行，沒有處理 `tag` 是第一個 tag 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A2:probe:1:3 ｜ `sandbox/release_notes.py:34` ｜ 候選：無

**NOTES_MAX 為負數或零時切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了非整數的情況，沒有檢查負數或零。如果使用者設定 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個 commit 以外的所有 commit；如果設定 `NOTES_MAX=0`，會回傳空 list，導致公告沒有內容。

建議：在 `max_items` 中檢查 `value <= 0` 時回傳預設值或記錄警告。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有處理負數或零。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-A2:probe:2:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 清單為空時 `tags.index(tag)` 會拋出未處理的 `ValueError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中先檢查 `if tag not in tags`，但若 `tags` 是空 list（例如 repo 沒有任何符合 `v*` 的 tag），`tag not in tags` 為 True，會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，若 `tags` 非空但 `tag` 不在其中，同樣會回傳 2。因此 `tags.index(tag)` 只有在 `tag` 存在於 `tags` 時才會執行，此時 `tags` 必非空，所以不會拋出 `ValueError`。

**但**：`list_tags` 可能因為 `git tag` 執行失敗而回傳空 list（例如 repo 路徑錯誤），此時 `tag not in tags` 為 True，程式會印出「找不到 tag」並回傳 2，不會崩潰。因此這個問題實際上不會觸發。

**重新評估**：此 finding 的 confidence 應降低，因為 `tag not in tags` 的檢查已經涵蓋了空 list 的情況。除非 `tags` 在檢查後被修改（但此處沒有），否則 `tags.index(tag)` 是安全的。

**建議**：無需修改，但可考慮將 `tags.index(tag)` 改為更明確的處理，例如使用 `try/except` 或先取得 index 再檢查，以增加可讀性。

evidence：diff 中 `main` 函式在 `if tag not in tags` 之後才執行 `tags.index(tag)`，但該檢查已確保 `tag` 存在於 `tags`，因此 `tags` 非空。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A2:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個 tag 時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個 tag），`tags.index(tag)` 為 0，`tags[-1]` 會取到最後一個 tag，而不是前一個 tag，這可能不是預期行為。更嚴重的是，如果 tags 為空（雖然前面已檢查 tag 存在，但若 tag 存在於 tags 中，tags 至少有一個元素），但若 tag 是第一個，`tags[-1]` 會取到最後一個，造成錯誤的 prev。建議明確檢查 index 是否為 0，並處理沒有前一個 tag 的情況。

evidence：diff 中 main 函式取得 prev 的方式，未處理 tag 為第一個的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A2:probe:3:3 ｜ `sandbox/release_notes.py:125` ｜ 候選：PR-B9, PR-X5, PR-B2(unless)

**`commits[0]` 在 commits 為空時會拋出 IndexError**

existing_code:
```
latest = commits[0][0]
```

body：雖然前面有 `if not commits: return 0`，但 `commits_between` 可能因為 git 指令失敗而回傳空 list（見另一個 finding），此時 `commits[0]` 會拋出 IndexError。建議在取得 `latest` 前再次確認 commits 非空，或讓 `commits_between` 在失敗時拋出例外。

evidence：diff 中 main 函式直接取 commits[0]，但 commits 可能因 git 失敗而為空。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）
- 規則提示 PR-X5：設定檔是合法 JSON 但不是物件時 AttributeError；設定檔由操作者自己維護

## ph-A2:probe:4:2 ｜ `sandbox/release_notes.py:43` ｜ 候選：無

**NOTES_MAX 未設上限，可能造成資源耗盡**

existing_code:
```
try:
        return int(raw)
    except ValueError:
```

body：`max_items` 直接將環境變數 `NOTES_MAX` 轉成整數，沒有上限。如果使用者設定一個極大的值（例如 10^9），`commits[: max_items()]` 會嘗試建立一個巨大的列表，可能耗盡記憶體。此外，webhook payload 也可能過大而被拒絕。

建議：設定一個合理的上限（例如 1000），或至少檢查是否為正整數。

evidence：diff 中 `return int(raw)` 沒有範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-A2:python:2:6 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**環境變數轉換為整數未處理例外**

existing_code:
```
return {"days": int(raw)}
```

body：threshold_from_env 使用 int(raw) 轉換環境變數 PR_STALE_DAYS，若使用者設定非數字字串（例如 "abc"），會拋出 ValueError 且未處理，導致程式崩潰。

建議：捕捉 ValueError 並提供有意義的錯誤訊息，或使用預設值。

evidence：diff 第 44 行顯示 int(raw)。

## ph-A2:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**collect_authors 使用可變預設值，跨呼叫累積結果**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時結果累積，且呼叫者無法預期初始狀態。

失敗情境：第一次呼叫 `collect_authors(repo, [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors(repo, [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：改用 `seen=None`，在函式內初始化為空 list。

evidence：diff 第 28 行：參數預設值為 `[]`，且函式內對 `seen` 進行 `append` 操作。

## ph-A2:shell:1:4 ｜ `sandbox/repo_sync.sh:38` ｜ 自動：SH-K-gitfail → valid

**git merge 未檢查失敗，可能導致後續操作在錯誤狀態下執行**

existing_code:
```
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`git merge --ff-only "origin/$BRANCH"` 若因衝突或非 fast-forward 而失敗，腳本不會中止，仍會繼續計算 ahead 並寫入資料庫。這可能導致資料庫記錄不正確的同步結果。建議在 merge 後檢查 exit code，失敗時記錄錯誤並跳過該 repo。

evidence：第 36 行未檢查 merge 的 exit code。

## ph-A2:shell:3:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 將 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法，甚至可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數做單引號跳脫（`${name//\'/\'\'}`）。

evidence：diff 第 46 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## ph-A2:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`name` 與 `BRANCH` 直接以字串串接方式插入 SQL 查詢，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'; DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行單引號跳脫（`${name//\'/\'\'}`）。

evidence：第 42 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

## ph-A2:shell:5:3 ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**cleanup_cache 使用 rm -rf 且路徑未驗證，可能誤刪重要資料**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用萬用字元，或改用更安全的刪除方式（例如 find 搭配 -delete）。

evidence：第 63 行直接使用 rm -rf 搭配萬用字元，未做任何防護。

## ph-A2:probe:3:4 ｜ `sandbox/release_notes.py:31` ｜ 自動：PR-B2 → invalid

**`load_config` 僅處理 FileNotFoundError 和 JSONDecodeError，其他例外（如權限錯誤）會導致程式崩潰**

existing_code:
```
try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 使用 `open` 讀取檔案，若檔案存在但無法讀取（例如權限不足），會拋出 PermissionError，未被捕捉，導致程式以 traceback 結束。建議捕捉 OSError 或更廣泛的例外，並提供友善錯誤訊息。

evidence：diff 中 load_config 的例外處理僅限於 FileNotFoundError 和 JSONDecodeError。
