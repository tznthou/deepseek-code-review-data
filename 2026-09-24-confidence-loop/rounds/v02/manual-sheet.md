# v02 人工標記單（盲標：不含 confidence、severity）

自動 64 筆、人工 24 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v02:python:1:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 是 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息，讓使用者難以除錯。

建議：
- 至少記錄例外（例如 `logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 考慮使用 `requests` 函式庫，它會自動拋出 HTTP 錯誤。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v02:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，會在函式定義時建立一次，並在所有呼叫之間共用。如果呼叫者沒有傳入 `seen`，每次呼叫都會將作者加到同一個 list 中，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v02:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設參數 seen=[] 導致跨呼叫狀態累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空串列，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者加到同一個串列中，造成結果不正確。

建議改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 25 行：`def collect_authors(repo, numbers, seen=[]):`，且函式內有 `seen.append(...)`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v02:python:3:5 ｜ `sandbox/pr_stats.py:21` ｜ 候選：PY-A1, PY-K-token

**GITHUB_TOKEN 可能因例外而外洩**

existing_code:
```
req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
```

body：`_fetch` 在建立請求時直接從環境變數讀取 token，若後續發生例外（例如網路錯誤），traceback 可能包含請求物件，進而洩漏 token。此外，若 token 無效，錯誤訊息可能包含 token。建議在錯誤處理中避免輸出請求內容，或使用更安全的方式傳遞憑證。

evidence：diff 第 20 行：直接將 token 加入 header，且後續例外處理不當。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v02:python:3:6 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但若 timeline 存在但為空（例如 `[]`），則會拋出 IndexError。此外，事件順序未保證按時間排序，可能導致負數延遲。建議檢查空 list 並排序事件。

evidence：diff 第 36-37 行：直接索引 events，未檢查空 list 或排序。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v02:python:4:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致靜默失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），呼叫端無法得知失敗，後續程式碼會繼續執行並可能因資料缺失而崩潰。例如：若 API 回傳 404，`json.loads` 會拋出例外，但被吞掉後 `_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或讓呼叫端處理。

evidence：diff 第 25 行：`except:` 後只有 `pass`，且 `_fetch` 被多處呼叫（`collect_authors`、`main`），其回傳值被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v02:python:4:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 的預設值為可變字典，且未處理轉換錯誤**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，是可變字典。雖然目前函式未修改它，但若未來修改會造成跨呼叫污染。此外，`int(raw)` 若環境變數不是數字會拋出 `ValueError`，導致程式崩潰。建議使用不可變預設值（如 `None`）並處理轉換例外。

evidence：diff 第 44 行：可變預設值，且 `int(raw)` 未包在 try/except 中。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## v02:python:4:6 ｜ `sandbox/pr_stats.py:21` ｜ 候選：PY-A1, PY-K-token

**Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError**

existing_code:
```
req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
```

body：`_fetch` 使用 `os.environ["GITHUB_TOKEN"]`，若環境變數未設定會拋出 `KeyError`，且此例外會被 `except: pass` 吞掉，導致靜默失敗。建議使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 None。

evidence：diff 第 22 行：直接索引環境變數，且位於 try 區塊外（但被外層 except 捕獲）。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v02:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A4

**可變預設值 seen=[] 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list，導致多次呼叫時作者列表會累積，造成結果不正確。例如第一次呼叫後 seen 包含 ['alice']，第二次呼叫會從 ['alice'] 開始，最終回傳包含重複作者的列表。建議改為 `seen=None`，在函式內初始化為空 list。

evidence：diff 第 28 行。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v02:python:5:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且包含 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 中若 `events` 為空列表，函式回傳 0，但若 events 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。建議使用 `events[0].get("created_at")` 並處理缺失情況。

evidence：diff 第 36-37 行。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v02:shell:1:5 ｜ `sandbox/repo_sync.sh:33` ｜ 候選：SH-S4, SH-K-gitfail

**`cd` 失敗時未中止，可能操作錯誤目錄**

existing_code:
```
cd "$dir"
```

body：`cd "$dir"` 若失敗（例如目錄不存在或權限不足），腳本仍會繼續執行後續的 `git` 指令，可能操作錯誤的 repo。建議在 `cd` 失敗時立即返回錯誤，例如 `cd "$dir" || return 1`。

evidence：第 31 行未檢查 `cd` 的返回值。

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## v02:shell:2:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 輸出進行迴圈，可能因檔名包含空白或換行而失敗**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式中的 `for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空白、換行或特殊字元，會導致迴圈分割錯誤。建議改用 `find` 或 glob 搭配 null 分隔符，例如 `while IFS= read -r -d '' d; do ... done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)`。

evidence：diff 第 69 行：`for d in $(ls "$ROOT"); do`。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v02:shell:3:6 ｜ `sandbox/repo_sync.sh:70` ｜ 候選：無

**日誌截斷邏輯可能遺失重要資訊**

existing_code:
```
if [ "$total" -gt 100 ]; then
    tail -100 "$LOG" > "$LOG.trimmed"
    mv "$LOG.trimmed" "$LOG"
  fi
```

body：`summarize` 函式在日誌行數超過 100 時，僅保留最後 100 行。這可能遺失較早的錯誤訊息，尤其是當多個 repo 同步失敗時。建議考慮將錯誤與一般日誌分開，或保留完整日誌並僅在輸出摘要時截斷。

evidence：diff 第 76-79 行：`if [ "$total" -gt 100 ]; then`、`tail -100 "$LOG" > "$LOG.trimmed"`、`mv "$LOG.trimmed" "$LOG"`

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v02:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 名稱未跳脫**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 名稱來觸發。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v02:shell:4:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 SQL 插入時 `$ahead` 為空會導致 SQL 語法錯誤。

建議在 rev-list 失敗時設定預設值（例如 0）或中止處理。

evidence：diff 第 39 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v02:shell:5:7 ｜ `sandbox/repo_sync.sh:90` ｜ 候選：SH-K-rootdir

**缺少對 repo 目錄是否為 Git 儲存庫的驗證**

existing_code:
```
if [ ! -d "$target/.git" ]; then
```

body：`if [ ! -d "$target/.git" ]` 僅檢查 `.git` 目錄是否存在，但未驗證其是否為有效的 Git 儲存庫。若 `.git` 損壞或非 Git 目錄，後續 git 指令可能失敗。建議使用 `git -C "$target" rev-parse --git-dir` 驗證。

evidence：diff 第 71 行：`if [ ! -d "$target/.git" ]; then`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v02:shell:5:8 ｜ `sandbox/repo_sync.sh:68` ｜ 候選：無

**日誌摘要計算可能不準確**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`summarize` 使用 `grep -c .` 計算行數，但若日誌最後一行沒有換行符，可能少算一行。建議使用 `wc -l` 或 `awk 'END{print NR}'`。

evidence：diff 第 62 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v02:probe:1:5 ｜ `sandbox/release_notes.py:66` ｜ 候選：無

**commit subject 可能包含換行字元，導致輸出格式錯亂**

existing_code:
```
sha, subject = line.split(" ", 1)
        commits.append((sha, subject))
```

body：`git log --format=%h %s` 的 subject 可能包含換行（例如 merge commit 或手動輸入），`group()` 直接將 subject 放入列表，`render()` 輸出時未跳脫，可能破壞 Markdown 格式或注入額外內容。建議對 subject 做 sanitize（例如取代換行）。

evidence：diff 中直接使用 `subject`，未做任何處理。

- 規則提示 PR-B4：沒有空白的行先 continue（實測）

## v02:probe:2:3 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 設為負數或零時，會產生空公告或錯誤**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了非整數的情況，但沒有檢查 `int(raw)` 是否為正數。如果 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表，`render` 會產生只有標題的公告；如果 `NOTES_MAX=-1`，切片會取到倒數第一個元素，行為怪異。建議加上 `if n <= 0: return DEFAULT_MAX` 之類的檢查。

evidence：diff 中 `max_items` 只處理 `ValueError`，沒有檢查轉換後的整數是否大於 0。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v02:probe:2:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `http` 或 `https`。如果攻擊者能控制 `NOTES_WEBHOOK` 環境變數（例如 CI 環境），可以指定 `file:///etc/passwd` 或 `gopher://` 等 scheme，造成資訊洩漏或 SSRF。建議在 `post` 開頭加上 `if not url.startswith(('http://', 'https://')): raise ValueError(...)`。

evidence：diff 中 `post` 函式直接使用 `url` 建立 Request，沒有檢查 scheme。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v02:probe:3:3 ｜ `sandbox/release_notes.py:111` ｜ 候選：無

**`max_items` 可能為負數或零，導致公告內容為空**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。如果設定為負數或 0，`commits[: max_items()]` 會是空列表，`render` 會產生只有標題的公告。建議在 `max_items` 中檢查數值必須大於 0，否則使用預設值。

evidence：diff 中 `max_items` 只處理了 `ValueError`，沒有檢查轉換後的數值是否為正數。

- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入

## v02:probe:3:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `https`。如果環境變數被設定為 `file://` 或 `http://`，可能導致讀取本地檔案或將資料傳送到非加密的端點。建議驗證 URL 的 scheme 必須是 `https`，並考慮使用 `urllib.parse.urlparse` 檢查。

evidence：diff 中 `url` 直接來自環境變數 `NOTES_WEBHOOK`，沒有進行 scheme 驗證。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v02:probe:4:4 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
```

body：`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `http` 或 `https`。如果環境變數被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或連線到非預期的資源。雖然環境變數通常由部署者控制，但這仍是一個潛在的安全風險。

建議：在 `main` 中驗證 `url` 的 scheme 為 `http` 或 `https`。

evidence：diff 第 93 行，`urlopen` 接受任意 scheme。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v02:probe:4:5 ｜ `sandbox/release_notes.py:74` ｜ 候選：無

**commit subject 的 prefix 解析可能誤分類**

existing_code:
```
prefix = subject.split(":", 1)[0]
```

body：`group` 使用 `subject.split(":", 1)[0]` 作為分類依據，但若 commit subject 本身包含冒號（例如 `fix: handle: edge case`），prefix 會是 `fix`，仍能正確分類；但若 subject 開頭不是 `feat:` 或 `fix:`，就會被歸為 `other`。這可能不是問題，但若團隊使用其他 prefix（如 `docs:`、`chore:`），這些 commit 會被歸為「其他」，可能不符合預期。

建議：確認團隊的 commit 慣例，或考慮更彈性的分類方式。

evidence：diff 第 61 行，只處理 `feat` 和 `fix`，其他都歸為 `other`。

- 規則提示 PR-A3：feat(api): 這種帶 scope 的前綴被分到「其他」（實測）
- 規則提示 PR-B5：kind 一定在 groups 裡（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v02:python:2:5 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 直接存取可能不存在的鍵**

existing_code:
```
if pr["additions"] > 500:
```

body：`classify` 函式直接使用 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`。GitHub API 的回應不一定包含這些欄位（例如某些事件或權限不足時），會拋出 `KeyError`。

建議使用 `.get()` 並提供預設值，或先驗證鍵是否存在。

evidence：diff 第 41 行：`if pr["additions"] > 500:`，且 `pr` 來自 `_fetch` 的回傳值，可能為 `None` 或缺少鍵。

## v02:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**可變預設值 seen=[] 導致跨呼叫狀態污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空列表，這是可變物件，會在多次呼叫間共享。若呼叫者未傳入 `seen`，每次呼叫都會將作者附加到同一個列表，導致結果累積。例如：第一次呼叫後 `seen` 包含 A，第二次呼叫（未傳入）會從 A 開始附加，回傳錯誤結果。建議改為 `seen=None` 並在函式內初始化。

evidence：diff 第 20 行：`seen=[]` 為可變預設值，且函式內有 `seen.append(...)` 修改該列表。

## v02:shell:1:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**`eval` 執行未受信任的 hook 路徑**

existing_code:
```
eval "$hook $repo"
```

body：`eval "$hook $repo"` 會執行 `$hook` 的內容。若 `$ROOT/.hooks/post-sync` 檔案被惡意修改（例如包含 `rm -rf /`），將造成嚴重後果。此外，`$repo` 未加引號，若 repo 名稱包含空格或特殊字元，可能導致命令注入。建議避免使用 `eval`，改為直接執行 `"$hook" "$repo"`，並確保 hook 檔案權限受控。

evidence：第 55 行使用 `eval` 執行未受信任的 hook 路徑。

## v02:shell:2:3 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 函式中的 `git fetch`、`git checkout`、`git merge` 指令僅將 stderr 重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續的 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：diff 第 31-33 行：三個 git 指令均未檢查退出碼。

## v02:shell:4:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：run_hook 使用 eval 執行未受信任的 hook 路徑**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 與 `$repo` 都來自使用者可控的輸入（`$ROOT` 與 repo 名稱），若其中包含 shell 特殊字元（例如 `; rm -rf ~`），可能導致任意命令執行。

建議避免使用 eval，改為直接執行並傳遞參數：
```bash
"$hook" "$repo"
```

evidence：diff 第 51 行：`eval "$hook $repo"`

## v02:shell:5:5 ｜ `sandbox/repo_sync.sh:41` ｜ 自動：SH-S3 → valid

**變數未初始化：ahead 可能為空導致數值比較錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)

  if [ "$ahead" -gt 0 ]; then
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，`ahead` 可能為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串導致語法錯誤。建議在指令失敗時設定預設值（如 `ahead=0`）或檢查退出碼。

evidence：diff 第 39-41 行：未處理 git rev-list 失敗的情況

## v02:probe:3:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成 commit 列表**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 處理。建議加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外。

evidence：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

## v02:probe:5:4 ｜ `sandbox/release_notes.py:50` ｜ 自動：PR-X3 → valid

**list_tags 使用 check=True 但未處理 CalledProcessError**

existing_code:
```
out = subprocess.run(
        ["git", "tag", "--list", "v*", "--sort=v:refname"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
```

body：`list_tags` 呼叫 `subprocess.run` 時設定了 `check=True`，但沒有捕捉 `subprocess.CalledProcessError`。如果 `git tag` 失敗，程式會直接 traceback 退出，使用者只看到一堆錯誤訊息。

建議：捕捉例外並印出友善的錯誤訊息，或讓上層處理。

evidence：diff 中 `list_tags` 的 `subprocess.run` 有 `check=True`，但函式沒有 try/except 處理可能的 `CalledProcessError`。
