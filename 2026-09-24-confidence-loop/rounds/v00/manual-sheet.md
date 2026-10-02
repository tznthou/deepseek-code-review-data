# v00 人工標記單（盲標：不含 confidence、severity）

自動 58 筆、人工 18 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v00:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**`collect_authors` 使用可變預設值 `seen=[]`，跨呼叫會累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen` 預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表物件。如果呼叫者未傳入 `seen`，多次呼叫會不斷累積作者，導致結果不正確。建議：將預設值改為 `None`，並在函式內初始化為空列表。

evidence：diff 第 28 行：函式簽名使用可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v00:python:3:6 ｜ `sandbox/pr_stats.py:63` ｜ 候選：無

**classify 使用 startswith("fix") 可能誤判標題**

existing_code:
```
elif pr["title"].startswith("fix"):
```

body：`classify` 以 `pr["title"].startswith("fix")` 判斷是否為 fix PR，但標題可能以 "fix" 開頭但非修復（例如 "fixed typo in docs"），或大小寫不同（"Fix"）。建議使用更精確的判斷，例如正規表示式或檢查標籤。

evidence：diff 第 44 行：`startswith("fix")` 過於寬鬆。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## v00:python:4:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，呼叫端無法得知失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致呼叫端拿到 `None` 或繼續執行，後續程式碼可能因為 `pr` 為 `None` 而拋出 `TypeError`，且錯誤被隱藏，難以除錯。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 讓呼叫端處理錯誤，而不是靜默失敗。

evidence：diff 第 24 行：`except:` 後直接 `pass`，且 `_fetch` 被 `collect_authors` 和 `main` 呼叫，其回傳值被直接使用（如 `pr["user"]["login"]`）。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v00:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 seen=[] 導致跨呼叫狀態累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會累積作者，且不會清空。若多次呼叫此函式，結果會包含先前呼叫的作者，造成資料污染。

建議：改為 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 28 行：`seen=[]` 為可變預設值，且函式內對其進行 `append` 操作。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v00:python:4:4 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且元素有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，若 `events` 只有一個元素，`first` 和 `last` 相同，回傳 0，可能無法反映真實延遲。

建議：檢查 `events` 是否為空，並確認每個事件都有 `created_at`，或使用更精確的計算方式。

evidence：diff 第 34-35 行：直接存取 `events[0]` 和 `events[-1]`，未檢查鍵是否存在。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v00:python:4:8 ｜ `sandbox/pr_stats.py:63` ｜ 候選：無

**classify 中 title.startswith("fix") 可能誤判**

existing_code:
```
elif pr["title"].startswith("fix"):
```

body：`classify` 使用 `pr["title"].startswith("fix")` 判斷是否為 fix，但大小寫敏感且可能誤判（例如 "fixed" 或 "Fix"）。建議使用正規表示式或忽略大小寫。

evidence：diff 第 53 行：`startswith("fix")` 未考慮大小寫變體。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## v00:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3, PY-A4

**可變預設值 seen=[] 導致跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：collect_authors 的參數 seen 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 seen，多次呼叫會累積先前結果，導致 authors 清單包含重複或非本次 PR 的作者。

建議：將預設值改為 None，並在函式內初始化為空串列。

evidence：diff 第 28 行顯示 seen=[]，且函式內使用 seen.append 修改該串列。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v00:python:5:5 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序，可能導致錯誤結果**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：review_latency 直接取 events[0] 和 events[-1] 的 created_at，但未檢查 events 是否為空（已檢查）或事件是否依時間排序。GitHub API 的 timeline 可能未排序，或事件缺少 created_at 欄位，導致計算錯誤或 KeyError。

建議：驗證事件結構，或明確排序後再取首尾。

evidence：diff 第 34-35 行直接索引 events，未檢查事件內容。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v00:shell:1:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄列表可能導致路徑處理錯誤**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式使用 `for d in $(ls "$ROOT")` 迭代目錄。若目錄名稱包含空格或特殊字元，將被錯誤分割。此外，`ls` 的輸出可能包含換行符號，導致迭代錯誤。

建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來安全處理。

evidence：diff 第 70 行：`for d in $(ls "$ROOT"); do`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v00:shell:1:6 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 變數可能為空，導致 SQL 插入失敗或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。

建議檢查 `git rev-list` 的退出碼，並在失敗時設定 `ahead=0` 或中止。

evidence：diff 第 36 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v00:probe:1:2 ｜ `sandbox/release_notes.py:39` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 設為負數或零時可能造成非預期行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
```

body：`max_items` 直接將環境變數轉成整數，沒有驗證範圍。若使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別回傳空列表或全部 commit（因為切片負數索引會從尾端計算），可能導致公告內容不正確。建議加上最小值檢查，例如 `max(1, int(raw))`。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的值是否合理。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v00:probe:2:2 ｜ `sandbox/release_notes.py:36` ｜ 候選：PR-X1, PR-B3(unless)

**`max_items` 未處理負數或零**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`int(raw)` 可以成功解析負數或零，但 `commits[: max_items()]` 在 `max_items()` 回傳負數時會得到空列表（因為切片從尾端倒數），回傳 0 時也會得到空列表，導致後續 `group` 收到空列表，最終產生沒有內容的公告。

建議：在 `max_items` 中檢查數值必須大於 0，否則回傳預設值或記錄警告。

evidence：diff 中 `max_items` 只處理了 `ValueError`，沒有檢查數值範圍。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v00:probe:2:3 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

**`post` 未處理非 2xx 狀態碼**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 4xx、5xx）時會拋出 `urllib.error.HTTPError`，但 `HTTPError` 是 `URLError` 的子類別，因此會被捕捉並記錄錯誤，但函式回傳 `False`。然而，如果伺服器回傳 3xx 且 `urlopen` 自動跟隨重定向，最終狀態碼可能不是 2xx，但函式仍會回傳 `True`。

建議：明確檢查 `resp.status` 是否在 200-299 範圍，否則記錄錯誤並回傳 `False`。

evidence：diff 中 `post` 函式只檢查了狀態碼範圍，但未處理重定向後的非 2xx 情況。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v00:probe:2:4 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

**`load_config` 未驗證 JSON 型別**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`json.load` 可能回傳任何 JSON 型別（例如 list、string、number），但後續程式碼假設它是 dict（例如 `cfg.get('title', ...)`）。如果設定檔內容是 `[]` 或 `"abc"`，會拋出 `AttributeError`。

建議：在 `load_config` 中檢查 `isinstance(data, dict)`，否則拋出錯誤或回傳空 dict。

evidence：diff 中 `load_config` 直接回傳 `json.load` 的結果，沒有型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v00:probe:4:2 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 為負數時會意外截斷 commit 列表**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為負數。在 `main` 中，`commits[: max_items()]` 若 `max_items()` 回傳負數，Python 切片會從尾端倒數，導致只取最後幾個 commit，而不是全部或前 N 個。例如 `NOTES_MAX=-1` 會讓公告只包含最後一個 commit。建議在轉換後檢查是否為正整數，若不是則回傳預設值或記錄警告。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的整數是否為負數。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v00:probe:4:3 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

**webhook 回應非 2xx 時未記錄回應內容**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 函式在 `urlopen` 成功取得回應後，只檢查 status code 是否在 200-299 之間，若不是則回傳 False，但沒有記錄回應的 status code 或 body。這會讓除錯變得困難，因為無法知道 webhook 端拒絕的具體原因（例如 400 或 403）。建議在非 2xx 時記錄 `resp.status` 和 `resp.read()` 的內容（注意不要洩漏敏感資訊）。

evidence：diff 中 `post` 函式在回應非 2xx 時直接回傳 False，沒有記錄任何資訊。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v00:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 是第一個 tag 時會 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 函式中，`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 列表的第一個元素時會嘗試存取 `tags[-1]`，這會回傳最後一個 tag，而不是正確的前一個 tag（實際上沒有前一個）。這會導致錯誤的 commit 範圍，甚至可能產生空列表或錯誤的 release notes。建議檢查 `tags.index(tag) == 0` 的情況，並回傳錯誤或使用不同的邏輯。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未處理 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v00:probe:5:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，存在 SSRF 風險**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 函式直接使用 `urllib.request.urlopen` 發送請求，未檢查 URL 的 scheme。如果 `NOTES_WEBHOOK` 被設定為 `file://` 或 `ftp://` 等非 HTTP(S) 協定，可能導致本地檔案讀取或內部網路掃描。建議驗證 URL 必須以 `https://` 開頭（或至少限制為 `http://` 和 `https://`）。

evidence：diff 中 `post` 函式直接使用 `url` 參數建立請求，未進行任何 scheme 檢查。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v00:python:2:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（使用者可控）。攻擊者可注入額外命令，例如 `repo` 設為 `foo; rm -rf /`，導致任意命令執行。建議：改用參數列表形式（`subprocess.run(["tar", "czf", f"{path}.tgz", path])`），並避免使用 `shell=True`；若必須使用 shell，應對輸入進行嚴格驗證或轉義。

evidence：diff 第 74 行：`subprocess.run` 的指令字串由 f-string 組成，包含外部輸入 `repo` 和 `path`，且 `shell=True`。

## v00:python:4:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**shell=True 且指令包含外部輸入，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo`（來自命令列參數）與 `path`（由 repo 衍生）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`。

建議：
- 避免 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若需使用 shell，務必驗證輸入或使用 `shlex.quote`。

evidence：diff 第 68 行：`repo` 來自 `sys.argv[1]`，未經驗證直接嵌入 shell 指令。

## v00:shell:1:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如，若 repo 名稱為 `x'; DROP TABLE runs;--`，則會執行惡意 SQL。

建議使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## v00:shell:2:4 ｜ `sandbox/repo_sync.sh:37` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git checkout 失敗仍繼續執行**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 失敗時（例如 branch 不存在），腳本仍會繼續執行 `git merge` 與後續步驟，可能導致錯誤的同步結果或資料庫寫入不正確的資料。

建議在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo：
```bash
git checkout "$BRANCH" 2>>"$LOG" || { echo "checkout failed for $name" >> "$LOG"; return 1; }
```

evidence：diff 第 32 行：`git checkout $BRANCH 2>>"$LOG"`

## v00:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串，攻擊者可透過特製的 repo 目錄名稱或 branch 名稱注入任意 SQL，例如建立名為 `x'); DROP TABLE runs;--` 的目錄。建議改用參數化查詢或使用 `sqlite3` 的參數綁定功能，或至少對輸入進行跳脫。

evidence：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## v00:shell:5:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。雖然 `$BRANCH` 有格式驗證，但 `$name` 來自目錄名稱，攻擊者可以建立包含單引號的目錄（例如 `'; DROP TABLE runs; --`），導致 SQL 注入。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

evidence：diff 第 49 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## v00:probe:4:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 執行失敗時未檢查，可能產生空公告**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有傳入 `check=True`，也沒有檢查 `proc.returncode`。如果 `repo` 路徑不是有效的 git 儲存庫，或 `git log` 因其他原因失敗，`proc.stdout` 會是空字串，函式回傳空 list。後續 `main` 會因為 `commits` 為空而直接回傳 0，不會貼出任何東西，但也不會回報錯誤。更糟的是，如果 `git log` 部分失敗但仍有輸出（例如 rev 不存在），程式可能貼出不完整的公告。建議加上 `check=True` 或明確檢查 `proc.returncode`，並在失敗時記錄錯誤並回傳非零 exit code。

evidence：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `subprocess.run` 未設 `check=True`。
