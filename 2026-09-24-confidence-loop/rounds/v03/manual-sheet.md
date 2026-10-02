# v03 人工標記單（盲標：不含 confidence、severity）

自動 69 筆、人工 15 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v03:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 `seen=[]` 導致跨呼叫狀態污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen` 預設為空列表，這是一個可變物件。在 Python 中，預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表。如果呼叫者沒有傳入 `seen`，則每次呼叫都會將作者名稱累加到同一個列表中，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 27 行：參數 `seen=[]` 使用可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v03:python:2:6 ｜ `sandbox/pr_stats.py:72` ｜ 候選：無

**CSV 輸出未跳脫，可能導致格式錯誤或注入**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 將 `author`、`latency`、`kind` 寫入 CSV 檔案。如果 `author` 包含逗號、換行或引號，會破壞 CSV 格式。此外，如果這些值來自外部（例如 GitHub 使用者名稱），可能包含惡意內容，在後續處理（如用試算表開啟）時造成風險。

建議：使用 `csv` 模組的 `writer` 來正確處理跳脫。

evidence：diff 第 63 行：直接字串拼接，未使用 csv 模組。

- 規則提示 PY-A6：open 沒用 with

## v03:python:2:7 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 依賴不存在的 timeline 欄位，可能回傳 0**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 函式使用 `pr.get("timeline", [])` 取得事件列表。但 GitHub API 的 Pull Request 物件通常不包含 `timeline` 欄位（需要另外請求 timeline 端點）。因此 `events` 會是空列表，函式回傳 0，導致延遲計算不正確。

建議：確認 API 回應結構，或另外請求 timeline 資料。

evidence：diff 第 33 行：`pr.get("timeline", [])` 可能永遠為空。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v03:python:4:7 ｜ `sandbox/pr_stats.py:32` ｜ 候選：PY-A3, PY-A4

**collect_authors 未處理 _fetch 回傳 None 或缺少 user 鍵的情況**

existing_code:
```
seen.append(pr["user"]["login"])
```

body：`collect_authors` 中 `pr["user"]["login"]` 若 `_fetch` 回傳 `None` 或 `pr` 缺少 `user` 鍵，會拋出 `TypeError` 或 `KeyError`。這與 `_fetch` 的錯誤處理有關，但即使 `_fetch` 正常，API 回應也可能缺少 `user` 欄位。

建議：在使用前檢查 `pr` 是否為 None 以及 `user` 鍵是否存在。

evidence：diff 第 31 行：直接存取巢狀鍵。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v03:python:5:5 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且元素有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 中，如果 `events` 為空，函式回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，則會拋出 `KeyError`。此外，`events` 的順序可能不是按時間排序，直接取第一個和最後一個可能不準確。

建議：驗證每個事件的 `created_at` 存在，並考慮排序。

evidence：diff 第 36-37 行：直接索引 events 並存取 created_at。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v03:shell:1:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 解析目錄列表，檔名含空格或換行時會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或特殊字元，將被錯誤分割。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，迴圈會將其視為兩個項目 `my` 和 `repo`，導致路徑錯誤。

**建議修法**：使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 迴圈。

evidence：diff 第 70 行

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v03:shell:2:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能失敗，導致 SQL 插入空值或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而中止腳本（set -e 未啟用，但可能產生錯誤訊息），且 SQL 插入時 `$ahead` 為空會導致型別錯誤。建議檢查指令退出碼並設定預設值（如 0）。

evidence：diff 第 38 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v03:shell:4:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄列表，路徑含空白或換行會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 依賴 ls 的輸出以空白分隔，若 repo 目錄名稱包含空白、換行或特殊字元，迴圈會錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：第 70 行使用 ls 輸出進行迴圈，未處理特殊字元。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v03:shell:4:7 ｜ `sandbox/repo_sync.sh:95` ｜ 候選：無

**run_hook 的參數傳遞可能不正確**

existing_code:
```
run_hook "$d"
```

body：`run_hook "$d"` 傳入的是 repo 的 basename，但 hook 可能需要完整路徑。此外，`run_hook` 內部的 `$repo` 參數未加引號，若名稱含空白會出錯。建議傳入完整路徑並在 hook 執行時正確引用。

evidence：第 78 行傳入 basename，且 run_hook 內未正確引用。

- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v03:probe:1:2 ｜ `sandbox/release_notes.py:39` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 為負數或非整數時行為不一致**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了 `ValueError`，但 `int(raw)` 也可能拋出 `TypeError`（不太可能，因為 raw 是字串）。另外，如果 `NOTES_MAX` 是負數，`commits[: max_items()]` 會回傳除了最後幾個元素以外的所有 commit，這可能不是預期行為。建議加上範圍檢查，例如 `max(0, value)` 或明確拒絕負數。

evidence：diff 中 `max_items` 函式沒有處理負數或非整數輸入。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v03:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**找不到符合條件的 tag 時會因 IndexError 崩潰**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 且格式正確的 tag）。在 `main` 中，`tags.index(tag)` 會拋出 `ValueError`，但即使 tag 存在於列表中，若它是第一個元素，`tags[tags.index(tag) - 1]` 會取到 `tags[-1]`（最後一個元素），而不是前一個 tag。建議在 `list_tags` 後檢查列表是否為空，並明確處理 tag 是第一個元素的情況。

evidence：diff 中 `prev = tags[tags.index(tag) - 1]` 沒有考慮 `tags` 為空或 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v03:probe:3:3 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 為負數或非整數時處理不完整**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了 `ValueError`，但 `int(raw)` 也可能拋出 `TypeError`（如果 `raw` 是 `None` 以外的非字串型別，但環境變數一定是字串，所以實際上不會）。另外，如果 `NOTES_MAX` 是負數，`commits[: max_items()]` 會取到空列表，導致公告沒有內容。建議加上範圍檢查，例如 `max(0, int(raw))` 或明確拒絕負數。

evidence：diff 中 `max_items` 沒有處理負數或非整數輸入，且 `commits[: max_items()]` 可能因負數而得到空列表。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v03:probe:4:2 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 設為負數或零時會產生空公告或漏掉全部 commit**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否大於 0。若使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會變成空列表或全部被截斷，導致公告內容空白或遺漏。建議在轉換後檢查數值，若小於 1 則記錄警告並使用預設值。

evidence：diff 中 `max_items()` 沒有對轉換後的整數做範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v03:probe:4:3 ｜ `sandbox/release_notes.py:96` ｜ 候選：PR-A2, PR-B7(unless)

**post() 未處理 HTTP 錯誤狀態碼**

existing_code:
```
except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`post()` 只捕捉 `urllib.error.URLError`，但 `urlopen` 在收到 4xx/5xx 回應時會拋出 `urllib.error.HTTPError`（它是 `URLError` 的子類別，所以會被捕捉），然而程式碼在 `except` 區塊中記錄錯誤並回傳 `False`，這部分正確。但若伺服器回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能回傳 200，這部分沒問題。真正的問題是：如果伺服器回傳 204 No Content，`resp.status` 是 204，條件 `200 <= resp.status < 300` 成立，回傳 `True`，但實際上 webhook 可能沒有處理。不過這屬於邊緣情況，影響不大。建議明確處理 `HTTPError` 並記錄狀態碼，或至少確認非 2xx 都視為失敗。

evidence：diff 中 `post()` 的例外處理只捕捉 `URLError`，但 `HTTPError` 是子類別，會被捕捉，但沒有特別記錄狀態碼。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v03:probe:5:2 ｜ `sandbox/release_notes.py:34` ｜ 候選：無

**NOTES_MAX 設為負數或零時會產生空公告或錯誤**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否為正數。若設定為 0 或負數，`commits[: max_items()]` 會變成空 list 或從尾端切片，導致公告內容為空或不完整。建議加上 `if value < 1` 的檢查，並回退到預設值。

evidence：diff 中 `max_items` 函式只處理 `ValueError`，未檢查轉換後的值是否大於 0。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v03:python:2:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**shell=True 搭配外部輸入，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 並設定 `shell=True`，且指令字串中包含 `repo` 和 `path` 變數。這些變數來自命令列參數（`repo`）和內部產生的路徑（`path`），但 `repo` 完全由使用者控制。攻擊者可以提供惡意的 `repo` 值，例如 `"; rm -rf / #"`，導致任意指令執行。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 如果必須使用 shell，請對所有外部輸入進行嚴格的驗證和轉義。

evidence：diff 第 67 行：`shell=True` 且 f-string 包含外部輸入 `repo`。

## v03:python:3:5 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**環境變數轉換為整數未處理例外**

existing_code:
```
return {"days": int(raw)}
```

body：threshold_from_env 中 int(raw) 可能拋出 ValueError，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

evidence：diff 第 44 行顯示 int(raw) 未包在 try 中。

## v03:python:5:1 ｜ `sandbox/pr_stats.py:24` ｜ 自動：PY-A1 → valid

**_fetch 吞掉所有例外，導致靜默失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得呼叫端無法得知失敗，後續程式碼可能因 `pr` 為 `None` 或缺少鍵而崩潰，或產生錯誤的統計結果。

建議：至少記錄錯誤並重新拋出，或回傳一個明確的錯誤值，讓呼叫端處理。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

## v03:shell:1:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經參數化直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `'; DROP TABLE runs; --`），將導致 SQL 注入，可能破壞資料庫或執行任意 SQL。

**失敗情境**：假設 `$ROOT` 下有一個名為 `evil'; DROP TABLE runs; --` 的目錄，執行腳本後 `runs` 表將被刪除。

**建議修法**：使用 `sqlite3` 的參數綁定功能，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行單引號轉義（但參數綁定更安全）。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## v03:shell:2:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：eval 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`eval "$hook $repo"` 將 hook 路徑與 repo 名稱直接拼接後執行，若 repo 名稱包含 shell 特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。例如 repo 名稱為 `x; rm -rf ~` 時，會執行惡意命令。建議避免使用 eval，改用直接執行並傳遞參數：`"$hook" "$repo"`。

evidence：diff 第 53 行：`eval "$hook $repo"`

## v03:shell:3:4 ｜ `sandbox/repo_sync.sh:41` ｜ 自動：SH-S3 → valid

**ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議檢查 rev-list 的 exit code 並處理失敗情況。

evidence：第 33 行未檢查 rev-list 的 exit code。

## v03:shell:4:5 ｜ `sandbox/repo_sync.sh:41` ｜ 自動：SH-S3 → valid

**ahead 計算可能因 rev-list 失敗而為空**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQLite 插入時 `$ahead` 為空可能導致錯誤。建議檢查 rev-list 的 exit code，失敗時設定預設值或跳過。

evidence：第 36 行未檢查 rev-list 的執行結果。

## v03:probe:1:3 ｜ `sandbox/release_notes.py:91` ｜ 自動：PR-B11 → invalid

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 函式直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，沒有驗證 scheme 是否為 http/https。如果攻擊者能控制環境變數（例如在 CI 中注入），可能導致請求發送到內部服務。但這需要攻擊者已有環境變數控制權，風險較低。建議加上 scheme 檢查。

evidence：diff 中 `post` 函式未對 URL 進行驗證。
