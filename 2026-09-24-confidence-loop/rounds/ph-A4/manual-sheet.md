# ph-A4 人工標記單（盲標：不含 confidence、severity）

自動 62 筆、人工 27 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-A4:python:1:1 ｜ `sandbox/pr_stats.py:22` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。

建議：
- 至少記錄錯誤（使用 `logging`）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 避免使用裸 `except:`，改為捕捉具體例外（如 `urllib.error.URLError`, `json.JSONDecodeError`）。

evidence：diff 第 22-23 行：`except:` 後直接 `pass`，沒有記錄或重新拋出。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A4:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設參數 seen=[] 導致跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。Python 在函式定義時只建立一次該 list，因此多次呼叫會共用同一個 list，導致結果累積且難以預測。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 26 行：`seen=[]` 是可變預設參數。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A4:python:1:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 使用不存在的 timeline 欄位，可能拋出 KeyError**

existing_code:
```
events = pr.get("timeline", [])
```

body：`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中並無此欄位（需另外請求 timeline 端點）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。若未來 API 變更或誤用，可能導致 `KeyError`。

建議：確認正確的資料來源，或移除該函式。

evidence：diff 第 31 行：`pr.get("timeline", [])` 中的 `timeline` 並非標準 PR 物件欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A4:python:2:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，呼叫端無法得知失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except:` 區塊只有 `pass`，任何網路錯誤、HTTP 錯誤、JSON 解析錯誤都會被吞掉，函式回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 是 `None` 而拋出 `TypeError`，但真正的錯誤原因已被隱藏。

失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 嘗試存取 `None["user"]` 導致 `TypeError`，使用者只看到無意義的錯誤，無法得知是 API 失敗。

建議：不要捕捉所有例外，或至少記錄錯誤並重新拋出。例如：
```python
except Exception as e:
    raise RuntimeError(f"Failed to fetch {path}: {e}") from e
```

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳任何錯誤指示。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A4:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值，跨呼叫累積結果**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，每次呼叫都會共用同一個 list。如果這個函式被多次呼叫（例如在同一個行程中處理多個 repo），結果會累積，導致資料污染。

失敗情境：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['user1','user2']`，第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['user1','user2','user3']`，而不是只有 `['user3']`。

建議：使用 `None` 作為預設值，在函式內建立新的 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：參數 `seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A4:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且函式沒有回傳值，導致呼叫端（`collect_authors`、`main`）拿到 `None` 後嘗試以 `pr["user"]` 或 `pr["additions"]` 存取，觸發 `TypeError`。

失敗情境：網路逾時、GitHub API 回 404、回應不是合法 JSON 時，程式會以難以理解的 `TypeError` 崩潰，且沒有留下任何錯誤訊息。

建議：
- 捕捉具體例外（`urllib.error.URLError`、`json.JSONDecodeError` 等），記錄錯誤並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 不要使用裸 `except:`。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A4:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表物件。

失敗情境：第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`；第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`，而不是預期的 `['bob']`。

建議：將預設值改為 `None`，在函式內判斷並建立新列表：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：參數 `seen=[]` 為可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A4:python:3:4 ｜ `sandbox/pr_stats.py:21` ｜ 候選：PY-A1, PY-K-token

**GITHUB_TOKEN 可能因例外而外洩至 stderr**

existing_code:
```
req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
```

body：`_fetch` 使用 `os.environ["GITHUB_TOKEN"]` 取得 token，若環境變數未設定會拋出 `KeyError`，且該例外會被 `except: pass` 吞掉，但 Python 預設的例外處理會將 traceback 輸出到 stderr，其中可能包含 token 值（若 token 出現在錯誤訊息中）。

失敗情境：未設定 `GITHUB_TOKEN` 時，程式會印出包含 `KeyError: 'GITHUB_TOKEN'` 的 traceback，但不會洩漏 token 本身；然而若 token 值本身包含特殊字元導致其他例外，traceback 可能包含 token。

建議：使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`，若未設定則印出明確錯誤訊息並退出。

evidence：diff 第 20 行：直接使用 `os.environ["GITHUB_TOKEN"]`，未處理 KeyError。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A4:python:3:5 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序，可能回傳錯誤結果**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空列表（已處理），但若事件順序不是時間遞增（例如 GitHub API 可能依其他方式排序），計算出的 latency 可能為負值或錯誤。

失敗情境：若 timeline 事件順序為 `[{"created_at": "2023-01-02"}, {"created_at": "2023-01-01"}]`，則 latency 為負數。

建議：先依 `created_at` 排序，或明確使用最早和最晚的事件。

evidence：diff 第 34-35 行：直接取第一個和最後一個事件，未排序。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A4:python:4:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式回傳 `None`。呼叫端（如 `collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤上下文。

具體失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 在 `pr["user"]` 處拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

建議：讓例外向上傳播，或至少記錄錯誤並回傳一個明確的錯誤值，並在呼叫端檢查。

evidence：diff 第 25 行 `except: pass`，且呼叫端如第 31 行 `pr["user"]["login"]` 未檢查 `None`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-A4:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 seen=[] 導致跨呼叫狀態累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，因此多次呼叫會共用同一個列表，導致作者名單不斷累積。

具體失敗情境：第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`，而不是預期的 `['bob']`。

建議：將預設值改為 `None`，並在函式內初始化為空列表。

evidence：diff 第 29 行，`seen=[]` 為可變預設值，且函式內對 `seen` 進行 `append` 操作（第 31 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A4:python:5:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 的預設值為可變字典，且 int() 轉換可能拋出例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`threshold_from_env` 的參數 `default` 預設為 `{"days": 7}`，是可變字典，若函式內修改它會影響後續呼叫（目前未修改，但風險存在）。另外，`int(raw)` 若環境變數不是整數會拋出 `ValueError`，導致程式崩潰。建議改用不可變預設值並處理轉換錯誤。

evidence：diff 第 45 行：`def threshold_from_env(default={"days": 7}):`，且第 48 行 `int(raw)` 未捕捉例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## ph-A4:shell:1:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。雖然 branch 有格式驗證，但 repo 名稱完全未驗證。

**失敗情境**：若 `$ROOT` 下有一個名為 `x'; DROP TABLE runs;--` 的目錄，執行後會刪除 `runs` 資料表。

**建議**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對字串進行單引號跳脫（`${name//\'/\'\'}`）。

evidence：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A4:shell:3:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 查詢**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL 語句，導致資料毀損或執行未預期的資料庫操作。

**失敗情境**：假設 repo 目錄名稱為 `test'repo`，則 SQL 指令變成 `INSERT INTO runs VALUES('test'repo', 'main', 0, datetime('now'))`，造成語法錯誤；若精心構造名稱，可插入任意 SQL。

**建議修法**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或使用 `sqlite3` 的 `-cmd` 與 `.parameter` 機制。

evidence：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A4:shell:3:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。

**失敗情境**：若 `origin/$BRANCH` 不存在，`git rev-list` 回傳非零 exit code，`ahead` 為空，`[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入時 `$ahead` 為空字串，可能導致資料型別不符。

**建議修法**：檢查 `git rev-list` 的 exit code，失敗時設定 `ahead=0` 或終止處理。

evidence：diff 第 38 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A4:shell:3:7 ｜ `sandbox/repo_sync.sh:94` ｜ 候選：SH-C1

**使用全域變數傳遞參數，降低可讀性與可測試性**

existing_code:
```
sync_one "$target"
    run_hook "$d"
```

body：`sync_one` 與 `run_hook` 依賴全域變數 `$ROOT`、`$BRANCH`、`$DB`、`$LOG`，而非透過參數傳遞，這使得函式難以獨立測試與重用。

**建議修法**：將所需變數作為函式參數傳入，或使用 `local` 變數並在呼叫時明確指定。

evidence：diff 第 79-80 行：呼叫 `sync_one` 與 `run_hook` 時僅傳入部分參數，其餘依賴全域變數。

- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-A4:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或注入攻擊。攻擊者可透過建立惡意名稱的 repo 目錄或 branch 來執行任意 SQL 指令，例如刪除資料表或竄改資料。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-quote` 選項或手動跳脫單引號。

evidence：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`。變數 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串，未做任何跳脫。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A4:shell:4:7 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 解析目錄列表，無法處理包含空格或特殊字元的目錄名稱**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或 glob 字元，將導致迴圈分割錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：diff 第 79 行：使用 `ls` 輸出進行迴圈，未處理特殊字元。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-A4:probe:1:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，`prev` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是拋出錯誤。這會導致錯誤的 commit 範圍，甚至可能讓 `git log` 失敗。

建議：先檢查 `tags.index(tag) == 0`，若是第一個 tag，則記錄錯誤並返回非零退出碼，或改用 `git log tag` 來取得該 tag 的所有 commit。

evidence：diff 中 `main()` 函式在取得 `prev` 時直接使用 `tags.index(tag) - 1`，沒有處理 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A4:probe:2:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**只有一個符合條件的 tag 時，`prev` 會取到 `tags[-1]` 造成錯誤**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag) - 1` 會是 `-1`，因此 `prev` 會變成最後一個 tag（即 `tag` 本身），導致 `prev..tag` 是空範圍，`commits_between` 回傳空列表，程式印出「之間沒有新 commit」並回傳 0。

建議：檢查 `tags.index(tag) == 0` 時，記錄錯誤並回傳非零，或改用 `tags[tags.index(tag) - 1] if tags.index(tag) > 0 else None` 並處理 `None`。

evidence：diff 中 `prev` 的計算沒有處理 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A4:probe:2:3 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**`NOTES_MAX` 沒有下限，可能導致負數或零造成意外行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 將環境變數轉成整數，但沒有檢查是否為正數。若使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表或全部元素（負索引切片），導致公告內容不正確。

建議：在轉換後檢查 `value < 1` 時記錄警告並使用預設值。

evidence：diff 中 `max_items()` 只處理了 `ValueError`，沒有檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-A4:probe:2:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接將 `url` 傳給 `urllib.request.Request`，沒有檢查 scheme 是否為 `http` 或 `https`。若環境變數被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或傳送資料到非預期的位置。

建議：在 `main` 中驗證 `url` 的 scheme 為 `http` 或 `https`，否則回傳錯誤。

evidence：diff 中 `url` 直接來自環境變數，未經 scheme 驗證即用於 `urllib.request.Request`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-A4:probe:2:5 ｜ `sandbox/release_notes.py:96` ｜ 候選：PR-A2, PR-B7(unless)

**`post` 未處理 HTTP 錯誤狀態碼，可能誤報成功**

existing_code:
```
try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`post` 只檢查 `200 <= resp.status < 300`，但 `urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 404、500）時會拋出 `urllib.error.HTTPError`，而 `HTTPError` 是 `URLError` 的子類別，因此會被 `except urllib.error.URLError` 捕捉並記錄錯誤，但函式回傳 `False`，`main` 會回傳 1。這部分行為正確，但若 webhook 端回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能得到 2xx 或拋出例外。整體而言，錯誤處理尚可，但建議明確捕捉 `HTTPError` 以提供更精確的錯誤訊息。

evidence：diff 中 `post` 的例外處理只捕捉 `URLError`，未區分 `HTTPError`。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-A4:probe:3:2 ｜ `sandbox/release_notes.py:45` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 可設為負數或零，導致切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否大於 0。若設為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，意外排除最後 n 筆 commit；若設為 0，則會回傳空列表，但 `main` 中仍會嘗試取 `commits[0]` 而崩潰。建議在轉換後檢查 `value > 0`，否則回退到預設值。

evidence：diff 中 `max_items` 只處理 `ValueError`，未檢查數值範圍；`main` 中 `commits[: max_items()]` 直接使用該值。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-A4:probe:3:3 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，沒有檢查 URL 的 scheme。攻擊者若能控制環境變數（例如在 CI 中注入），可指定 `file:///etc/passwd` 或 `http://169.254.169.254/...` 等 URL，導致任意檔案讀取或內部網路掃描。建議限制 scheme 為 `https`（或至少 `http`/`https`），並考慮阻擋內網位址。

evidence：diff 中 `post` 函式直接使用傳入的 `url`，未做任何驗證；`main` 中 `url` 來自環境變數 `NOTES_WEBHOOK`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-A4:probe:4:2 ｜ `sandbox/release_notes.py:34` ｜ 候選：無

**`max_items` 未處理負數或零，可能導致空公告或錯誤**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設為負數，`commits[: max_items()]` 會變成 `commits[:-1]`（少最後一筆）；若設為 0，會得到空 list，導致 `latest = commits[0][0]` 拋出 IndexError。建議驗證數值為正整數，否則回退預設值。

evidence：diff 中 `max_items` 只處理 ValueError，未處理負數或零。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-A4:probe:5:2 ｜ `sandbox/release_notes.py:96` ｜ 候選：PR-A2, PR-B8, PR-B7(unless)

**post 未處理 HTTP 錯誤狀態碼**

existing_code:
```
except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`urllib.request.urlopen` 在 HTTP 回應狀態碼非 2xx 時會拋出 `urllib.error.HTTPError`，但目前的 `except` 只捕捉 `urllib.error.URLError`。`HTTPError` 是 `URLError` 的子類別，所以會被捕捉，但函式會回傳 `False`，導致呼叫端誤以為發送失敗。建議明確處理 `HTTPError`，並根據狀態碼決定是否重試或記錄更詳細的錯誤。

evidence：diff 中 `except` 捕捉 `URLError`，但 `HTTPError` 是其子類別，且函式回傳 `False` 表示失敗，但實際上可能只是回應狀態碼非 2xx。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-A4:python:2:5 ｜ `sandbox/pr_stats.py:21` ｜ 自動：PY-K-token → valid

**GITHUB_TOKEN 可能未設定，導致 KeyError**

existing_code:
```
req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
```

body：`_fetch` 直接使用 `os.environ["GITHUB_TOKEN"]`，如果環境變數未設定，會拋出 `KeyError`，且沒有提供任何有用的錯誤訊息。

失敗情境：使用者未設定 `GITHUB_TOKEN` 時，程式在第一次呼叫 `_fetch` 時崩潰，只顯示 `KeyError: 'GITHUB_TOKEN'`，無法得知需要設定 token。

建議：在程式啟動時檢查，或提供預設值與明確錯誤：
```python
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable is required")
```

evidence：diff 第 22 行：直接存取 `os.environ["GITHUB_TOKEN"]`，沒有檢查存在性。

## ph-A4:python:4:6 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 函式依賴可能不存在的鍵**

existing_code:
```
if pr["additions"] > 500:
```

body：`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 回傳的資料可能缺少這些鍵（例如 API 回應格式變更或部分 PR 資料不完整），導致 `KeyError`。

具體失敗情境：GitHub API 回傳的 PR 物件缺少 `additions` 欄位（例如某些事件類型），程式在 `classify` 中拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證資料結構。

evidence：diff 第 54 行，直接存取鍵，未檢查存在性。

## ph-A4:shell:1:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：`eval "$hook $repo"` 執行未受信任的 hook 路徑與 repo 名稱**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval` 執行 `$hook $repo`。`$hook` 是固定路徑，但 `$repo` 來自目錄名稱，未經驗證。若 repo 名稱包含 shell 特殊字元（例如 `$(rm -rf ~)`），會被執行。

**失敗情境**：若 `$ROOT` 下有名為 `$(touch /tmp/pwned)` 的目錄，執行此腳本會建立 `/tmp/pwned` 檔案。

**建議**：避免使用 `eval`，改用直接執行：`"$hook" "$repo"`。若 hook 需要 shell 解析，應明確限制 repo 名稱格式（例如只允許 `[A-Za-z0-9._-]+`）。

evidence：diff 第 52 行：`eval "$hook $repo"`

## ph-A4:shell:2:3 ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**路徑處理不當：cleanup_cache 使用未加引號的 glob，可能誤刪檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空格或特殊字元，或 `.cache` 目錄不存在，glob 可能展開成意外路徑。此外，若 `$ROOT` 為空或未定義，可能變成 `rm -rf /.cache/*`，造成系統檔案刪除。

建議先檢查目錄是否存在，並使用更安全的寫法：
```bash
if [ -d "$ROOT/.cache" ]; then
  find "$ROOT/.cache" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
fi
```

evidence：diff 第 53 行：`rm -rf "$ROOT"/.cache/*`

## ph-A4:shell:3:6 ｜ `sandbox/repo_sync.sh:68` ｜ 自動：SH-B2 → invalid

**summarize 中 total 計算可能因 grep 失敗而錯誤**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 `grep` 因檔案不存在而失敗，`total` 會被設為 0，但若檔案存在但為空，`grep -c .` 回傳 0 且 exit code 為 1，此時 `total` 會被設為 0，但實際上檔案存在且為空，後續 `if [ "$total" -gt 100 ]` 判斷正確，但 `echo` 顯示的筆數為 0，可能造成誤解。

**建議修法**：使用 `wc -l < "$LOG"` 或先檢查檔案是否存在。

evidence：diff 第 70 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

## ph-A4:shell:5:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入風險：`eval` 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 皆來自使用者輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元，將導致任意命令執行。例如，若 repo 名稱為 `foo; rm -rf ~`，則會執行 `eval "/path/.hooks/post-sync foo; rm -rf ~"`，造成嚴重後果。

建議避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 不包含特殊字元，或使用 `--` 分隔參數。

evidence：diff 第 55 行：`eval "$hook $repo"`，其中 `$hook` 與 `$repo` 未經驗證。

## ph-A4:probe:3:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，後續會因空列表而崩潰**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空列表。接著在 `main` 中 `commits[0][0]` 會拋出 `IndexError`，程式直接崩潰。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並回報錯誤。

evidence：diff 中 `commits_between` 的 `subprocess.run` 沒有 `check=True`，且回傳值未檢查；`main` 中 `latest = commits[0][0]` 直接對空列表取索引。
