# v01 人工標記單（盲標：不含 confidence、severity）

自動 67 筆、人工 24 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v01:python:1:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，呼叫端無法得知失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致呼叫端拿到 `None` 或未定義的 `pr`，後續程式碼會因 `pr["user"]` 拋出 `TypeError` 或 `KeyError`。例如：GitHub API 回傳 404 時，`urlopen` 會拋出 `HTTPError`，但被 `pass` 吞掉，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 就會崩潰。建議：至少記錄錯誤並重新拋出，或回傳明確的錯誤值，讓呼叫端能處理。

evidence：diff 第 24 行顯示 `except:` 後只有 `pass`，且 `_fetch` 的呼叫端（如 `collect_authors` 第 28 行）直接使用回傳值，沒有檢查是否為 `None`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v01:python:2:1 ｜ `sandbox/pr_stats.py:22` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式可能回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，且沒有提供任何錯誤訊息。

具體失敗情境：當 GitHub API 回傳 404（例如 PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]["login"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰且沒有 log。

建議：在 `_fetch` 中不要吞掉例外，或至少記錄錯誤並重新拋出；或者讓呼叫端檢查回傳值是否為 `None`。

evidence：diff 第 22-23 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 27 行）和 `main`（第 75 行）被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v01:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 `seen=[]` 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen` 預設為空列表，這是一個可變預設值。每次呼叫時若未傳入 `seen`，會共用同一個列表物件，導致多次呼叫的結果累積。

具體情境：第一次呼叫 `collect_authors(repo, [1])` 回傳 `['user1']`；第二次呼叫 `collect_authors(repo, [2])` 會回傳 `['user1', 'user2']`，而不是預期的 `['user2']`。

建議：將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 26 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行了 `append` 操作（第 28 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v01:python:2:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 假設 timeline 存在且非空，但 API 回應可能不含該欄位**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 直接使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位（需要另外請求 timeline API）。因此 `events` 會是空列表，函式回傳 0，導致延遲指標失真。

具體情境：`_fetch` 回傳的 PR JSON 沒有 `timeline` 鍵，`events` 為空，函式回傳 0，所有 PR 的延遲都顯示為 0。

建議：確認 API 回應結構，或另外請求 timeline 資料；若無法取得，應回傳 `None` 或拋出明確錯誤。

evidence：diff 第 31 行：`pr.get("timeline", [])` 預設為空列表，但 GitHub PR API 回應中沒有 `timeline` 欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v01:python:2:9 ｜ `sandbox/pr_stats.py:75` ｜ 候選：無

**main 中重複呼叫 _fetch，且未檢查回傳值**

existing_code:
```
pr = _fetch(f"/repos/{repo}/pulls/{n}")
```

body：`main` 在迴圈中對每個 PR 呼叫 `_fetch`，但 `_fetch` 可能回傳 `None`（因為吞掉例外），導致後續 `pr["user"]["login"]` 拋出 `TypeError`。此外，`collect_authors` 已經呼叫過一次 `_fetch`，這裡又重複呼叫，造成不必要的 API 請求。

具體情境：某個 PR 的 API 請求失敗，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]["login"]` 拋出 `TypeError`。

建議：在 `_fetch` 中處理錯誤並拋出例外，或在 `main` 中檢查回傳值；同時考慮重用 `collect_authors` 的結果，避免重複請求。

evidence：diff 第 75 行：`_fetch` 的回傳值未檢查，且 `_fetch` 可能回傳 `None`。

- 規則提示 PY-A6：open 沒用 with
- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## v01:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰或產生錯誤結果**

existing_code:
```
try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，導致程式崩潰。此外，若 API 回傳錯誤（如 404），程式不會有明確的錯誤訊息，使用者難以除錯。

建議：
- 移除 `try/except`，讓例外自然傳播，或至少記錄錯誤並重新拋出。
- 若需處理特定例外（如 `urllib.error.HTTPError`），應針對性捕捉並提供有意義的錯誤訊息。

evidence：diff 第 24-28 行顯示 `_fetch` 的 `except: pass`，且呼叫端（第 31、59 行）直接使用回傳值，未檢查是否為 `None`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v01:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若呼叫多次，前一次的結果會殘留，導致後續呼叫的結果包含先前 PR 的作者，造成資料污染。

建議：
- 將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 31 行顯示可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v01:python:3:4 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序，可能導致錯誤延遲計算**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理）或事件未按時間排序。若事件順序混亂，計算出的延遲可能為負值或錯誤。此外，若 `created_at` 欄位缺失或格式不符，`_to_epoch` 會拋出例外。

建議：
- 確認 API 回傳的 timeline 是否保證有序，否則應先排序。
- 對 `created_at` 的解析加入錯誤處理。

evidence：diff 第 42-43 行直接使用索引存取，未檢查事件順序或欄位存在性。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v01:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A4

**可變預設值參數 seen=[] 可能導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。如果函式被多次呼叫（例如在測試或迴圈中），結果會累積，導致非預期行為。建議改為 `seen=None` 並在函式內初始化。

evidence：diff 第 27 行顯示 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v01:python:4:7 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 假設 timeline 存在且非空，可能導致錯誤**

existing_code:
```
events = pr.get("timeline", [])
    if not events:
        return 0
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位，因此 `events` 會是空列表，函式回傳 0。這可能不是預期行為，建議確認 API 回應結構或改用其他端點取得時間線。

evidence：diff 第 34-36 行顯示對 `timeline` 的處理。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v01:python:5:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
    raw = os.environ.get("PR_STALE_DAYS", "")
    if raw:
        return {"days": int(raw)}
```

body：`threshold_from_env` 的預設參數 `default={"days": 7}` 是可變 dict，雖然函式內沒有修改它，但若未來修改可能造成跨呼叫污染。此外，`int(raw)` 若環境變數不是整數會拋出 `ValueError`，導致程式崩潰。建議：改用不可變預設值（如 `None`）並處理轉換例外。

evidence：diff 第 45-48 行顯示可變預設值和未處理的 `int()` 轉換。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## v01:shell:1:3 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 解析目錄名稱，無法處理包含空白或換行的路徑**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白和換行分割，因此如果 repo 目錄名稱包含空白（例如 `my repo`），會被拆成多個 token，導致 `$target` 路徑錯誤，腳本無法正確處理該 repo。

**失敗情境**：在 `$ROOT` 下建立名為 `my repo` 的目錄（含 `.git`），執行腳本時，迴圈會嘗試處理 `my` 和 `repo` 兩個不存在的路徑，該 repo 不會被同步。

**建議修法**：使用 `find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0` 搭配 `while IFS= read -r -d '' dir` 迴圈，或使用 `shopt -s nullglob` 與 glob 展開。

evidence：diff 第 73 行：`for d in $(ls "$ROOT"); do`，這是常見的錯誤用法，無法處理特殊字元。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v01:shell:3:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**迴圈使用 ls 輸出解析，檔名含空格或換行會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 依賴 ls 的輸出，若目錄名稱包含空格、換行或特殊字元，迴圈會錯誤分割。建議使用 `find` 或 glob 搭配 null 分隔符，或使用 `for d in "$ROOT"/*/` 並檢查是否為目錄。

evidence：diff 第 74 行：使用命令替換解析 ls 輸出。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v01:shell:3:7 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-S3

**SQL 插入未使用參數化，且未處理 ahead 為空**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：即使輸入合法，若 `ahead` 為空（如 git 指令失敗），SQL 語句會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致語法錯誤。建議使用參數化查詢並確保 ahead 有預設值。

evidence：diff 第 47 行：ahead 可能為空。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v01:shell:5:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**路徑處理不當：使用 ls 解析目錄，檔名包含空白或換行會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若目錄名稱包含空白或換行，將無法正確處理。建議改用 glob 或 `find` 搭配 `-print0` 和 `while read -d ''`。

evidence：第 72 行使用 `$(ls ...)`，未考慮特殊檔名。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v01:shell:5:6 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 變數可能為空，導致 SQL 插入 NULL 或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ...)` 若 git 指令失敗（例如 branch 不存在），`ahead` 可能為空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因 `-gt` 需要整數而報錯，且 SQL 插入時可能產生 `INSERT INTO runs VALUES(..., , ...)` 的語法錯誤。建議在 git 指令失敗時設定預設值（如 0）或中止。

evidence：第 38 行未檢查 git rev-list 的退出碼，且未處理空值。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v01:probe:1:4 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 列表為空時索引錯誤**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 的 tag）。在 `main` 中，`tags.index(tag)` 會拋出 `ValueError`，但若 `tag` 不在列表中，程式會先檢查 `if tag not in tags` 並回傳錯誤，因此不會執行到 `tags.index(tag)`。然而，若 `tags` 為空且 `tag` 不在其中，`if tag not in tags` 為真，程式會回傳 2，不會有問題。但若 `tags` 為空且 `tag` 恰好為空字串（不可能，因為前面已驗證格式），所以此情境不會發生。因此此問題可能不存在，但建議仍檢查 `tags` 是否為空，避免未來修改時引入錯誤。

evidence：diff 中 `main` 函式在 `tag not in tags` 檢查後直接使用 `tags.index(tag)`，但未檢查 `tags` 是否為空。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v01:probe:2:2 ｜ `sandbox/release_notes.py:74` ｜ 候選：無

**`group` 函式對 commit subject 的解析可能誤分類**

existing_code:
```
prefix = subject.split(":", 1)[0]
        kind = prefix if prefix in groups else "other"
```

body：`group` 函式以 `subject.split(":", 1)[0]` 作為分類依據，但若 commit subject 不含冒號，`prefix` 會是整個 subject，可能不屬於任何已知分類而被歸為 `other`。這可能導致分類不準確，但影響有限。建議先檢查是否包含冒號，或使用更嚴謹的解析方式。

evidence：diff 中 `group` 函式的解析邏輯未處理無冒號的情況。

- 規則提示 PR-A3：feat(api): 這種帶 scope 的前綴被分到「其他」（實測）
- 規則提示 PR-B5：kind 一定在 groups 裡（實測）

## v01:probe:3:2 ｜ `sandbox/release_notes.py:33` ｜ 候選：無

**`max_items` 未處理負數或零**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有驗證其值是否為正數。如果設定為負數或零，`commits[: max_items()]` 會產生空 list 或意外的切片結果（例如 `commits[:-1]` 會排除最後一個 commit），導致 release notes 內容不正確。

建議：在轉換後檢查數值是否大於 0，否則使用預設值或記錄警告。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的整數是否為正數。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v01:probe:3:3 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

**`load_config` 未驗證 JSON 內容型別**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 直接回傳 `json.load` 的結果，沒有檢查其型別是否為 dict。如果設定檔內容是 list、字串或數字，後續 `cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

建議：在回傳前檢查 `isinstance(data, dict)`，否則拋出錯誤或回傳空 dict。

evidence：diff 中 `load_config` 函式直接回傳 `json.load` 的結果，沒有型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v01:probe:4:2 ｜ `sandbox/release_notes.py:31` ｜ 候選：無

**NOTES_MAX 未驗證範圍，負數或零可能造成非預期行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數，`commits[: max_items()]` 會回傳空列表，導致輸出空白；若設定為 0，同樣回傳空列表。建議在轉換後檢查 `value > 0`，否則回傳預設值或記錄警告。

evidence：diff 中 `max_items` 僅處理 `ValueError`，未檢查轉換後的值是否為正整數。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v01:probe:4:4 ｜ `sandbox/release_notes.py:74` ｜ 候選：無

**commit subject 解析可能因格式不符而誤分類**

existing_code:
```
prefix = subject.split(":", 1)[0]
        kind = prefix if prefix in groups else "other"
```

body：`group` 函式以 `subject.split(":", 1)[0]` 作為分類依據，若 commit subject 不含冒號，則整個 subject 會被當成 prefix，並歸入 `other`。這可能導致大量 commit 被錯誤分類，影響 release notes 的可讀性。建議僅在 prefix 符合已知標籤時才使用，否則一律歸入 `other`。

evidence：diff 中 `group` 函式未檢查 prefix 是否為有效標籤，直接使用 `subject.split(":", 1)[0]`。

- 規則提示 PR-A3：feat(api): 這種帶 scope 的前綴被分到「其他」（實測）
- 規則提示 PR-B5：kind 一定在 groups 裡（實測）

## v01:probe:5:2 ｜ `sandbox/release_notes.py:31` ｜ 候選：無

**NOTES_MAX 未處理負數或零，可能導致輸出異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 從環境變數讀取整數，但沒有驗證範圍。如果設定為負數或零，`commits[: max_items()]` 會產生空列表或錯誤的切片，導致 release notes 內容不完整或程式出錯。

建議：檢查數值是否為正整數，否則使用預設值或回報錯誤。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v01:probe:5:4 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

**webhook 回應狀態碼判斷可能不正確**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 函式檢查 `200 <= resp.status < 300` 來判斷成功，但有些 webhook 服務可能回傳 204 No Content 或其他 2xx 狀態碼，這部分沒問題。然而，如果服務回傳 3xx 重定向，`urllib` 會自動跟隨，最終狀態碼可能是 2xx，但這可能不是預期的行為。另外，如果服務回傳 4xx 或 5xx，函式會回傳 False，但沒有記錄回應內容，不利於除錯。

建議：考慮記錄回應狀態碼和內容，以便診斷問題。

evidence：diff 中 `post` 函式只回傳布林值，沒有記錄失敗時的詳細資訊。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v01:python:2:6 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 直接存取 pr["additions"] 等鍵，未處理缺失**

existing_code:
```
if pr["additions"] > 500:
```

body：`classify` 直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，若 API 回應缺少這些鍵（例如權限不足或 API 變更），會拋出 `KeyError`。

具體情境：GitHub API 回應中缺少 `additions` 欄位（例如某些事件類型），`classify` 拋出 `KeyError`，程式崩潰。

建議：使用 `.get()` 並提供預設值，或先驗證回應結構。

evidence：diff 第 44 行：直接使用 `pr["additions"]`，未檢查鍵是否存在。

## v01:python:3:8 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 假設 pr 包含 additions 和 changed_files 欄位，可能因 API 回應缺失而崩潰**

existing_code:
```
if pr["additions"] > 500:
        return "large"
    elif pr["changed_files"] > 20:
```

body：`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，若 API 回應中缺少這些欄位（例如權限不足或 API 版本變更），會拋出 `KeyError`。

建議：
- 使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)` 提供預設值。

evidence：diff 第 59-60 行直接使用鍵值存取。

## v01:python:5:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`。建議：改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 62 行顯示 `shell=True` 且指令字串由外部輸入拼接。

## v01:shell:1:5 ｜ `sandbox/repo_sync.sh:13` ｜ 自動：SH-S6 → valid

**多個 repo 共用同一個 log 檔，可能造成內容交錯**

existing_code:
```
LOG=/tmp/repo_sync.log
```

body：所有 repo 的同步過程都將輸出附加到同一個 `$LOG` 檔（`/tmp/repo_sync.log`），且 `sync_one` 中的 `git` 指令使用 `2>>"$LOG"` 並行寫入。如果多個 repo 同時執行（雖然目前是循序），或 log 檔被其他程序寫入，內容可能交錯，影響後續的 `summarize` 與除錯。

**建議修法**：為每個 repo 使用獨立的 log 檔，或在寫入時加上鎖定機制。

evidence：diff 第 15 行：`LOG=/tmp/repo_sync.log`，且多處使用 `2>>"$LOG"` 寫入。

## v01:shell:3:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：hook 使用 eval 執行未受信任的參數**

existing_code:
```
eval "$hook $repo"
```

body：`eval "$hook $repo"` 將 `$repo` 直接拼入命令字串，若 repo 名稱包含 shell 特殊字元（如 `; rm -rf /`），將導致任意命令執行。即使 hook 路徑固定，`$repo` 來自目錄名稱，可能受攻擊者控制。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

evidence：diff 第 55 行：`eval "$hook $repo"`，其中 `$repo` 未經驗證。

## v01:shell:4:4 ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

**使用 ls 解析目錄列表，檔名含空格或換行會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 依賴 ls 的輸出，若目錄名稱包含空格、換行或特殊字元，迴圈會錯誤分割。建議改用 glob：`for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

evidence：diff 第 76 行，未使用安全的方式迭代目錄。

## v01:shell:5:5 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將 stderr 寫入 log，未檢查退出碼。若 fetch 失敗，後續的 merge 可能基於過時的遠端分支，導致錯誤的 ahead 計數。建議在每個 git 指令後檢查 `$?`，失敗時中止該 repo 的處理。

evidence：第 34-36 行未檢查 git 指令的退出碼。

## v01:probe:4:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查，可能導致後續處理錯誤資料**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損壞、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空或包含錯誤訊息，函式仍會回傳空列表或解析出錯誤的 commit。後續 `main` 會將空列表視為「沒有新 commit」而回傳 0，或將錯誤訊息當成 commit 處理。建議加上 `check=True` 或檢查 `returncode`，並在失敗時拋出例外或回傳明確錯誤。

evidence：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且未設定 `check=True`。
