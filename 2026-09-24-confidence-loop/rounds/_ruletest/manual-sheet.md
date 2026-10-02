# _ruletest 人工標記單（盲標：不含 confidence、severity）

自動 32 筆、人工 9 筆、抽查 4 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## _ruletest:python:1:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

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

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## _ruletest:python:2:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼**

existing_code:
```
except:
        pass
```

body：`_fetch` 函式使用裸 `except: pass` 吞掉所有例外，包括網路錯誤、JSON 解析錯誤等。此外，它未檢查 HTTP 回應狀態碼，若 API 回傳 404 或 401，`json.loads` 仍會嘗試解析錯誤頁面，可能拋出例外而被吞掉，導致函式回傳 `None`。後續程式碼（如 `pr["user"]["login"]`）會因 `pr` 為 `None` 而拋出 `TypeError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

evidence：diff 第 22 行：`except:` 與 `pass`，且未檢查 `resp.status`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## _ruletest:python:2:7 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

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

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## _ruletest:python:3:1 ｜ `sandbox/pr_stats.py:22` ｜ 候選：PY-A1, PY-K-status

**`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、JSON 解析錯誤），且未檢查 HTTP 狀態碼（例如 404、401）。這會導致呼叫端在 API 失敗時拿到 `None`，後續程式碼（如 `pr["user"]["login"]`）會拋出 `TypeError` 或 `KeyError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

evidence：diff 第 22 行：`except:` 後直接 `pass`，且未檢查 `resp.status`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## _ruletest:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**`collect_authors` 使用可變預設參數 `seen=[]`**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 預設為空列表，但列表是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致資料污染。建議改為 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 27 行：可變預設參數。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## _ruletest:python:3:6 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

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

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## _ruletest:shell:2:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以字串拼接方式插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可執行任意 SQL 指令。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 參數來利用此漏洞。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成 `INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))`，導致資料表被刪除。

**建議修法**：使用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或先對變數進行跳脫（如 `sqlite3` 的 `:memory:` 或使用 `printf '%q'`）。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經任何處理直接嵌入 SQL 字串。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## _ruletest:shell:3:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄名稱可能因特殊字元出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格、換行或萬用字元，將導致錯誤分割。建議改用 `for d in "$ROOT"/*/` 並搭配 `basename`，或使用 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：第 66 行使用 ls 輸出進行迴圈。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## _ruletest:shell:3:7 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**未驗證 $ROOT 是否為有效目錄**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式未檢查 `$ROOT` 是否存在且為目錄。若使用者提供不存在的路徑，`ls` 會失敗，但腳本仍會繼續執行並嘗試進入不存在的目錄。建議在開頭加上 `[ -d "$ROOT" ] || { echo "錯誤：$ROOT 不是目錄" >&2; exit 1; }`。

evidence：第 66 行之前未驗證 $ROOT。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## _ruletest:python:2:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 參數（來自命令列參數）與 `path`（來自內部變數，但可能受環境影響）。攻擊者可提供惡意的 `repo` 值（例如 `; rm -rf /`）來執行任意命令。建議改用參數列表形式並移除 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 76 行：`shell=True` 且 f-string 包含 `repo` 變數。

## _ruletest:shell:1:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 查詢**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱或 branch 名稱包含單引號，攻擊者可以注入任意 SQL 指令。例如，若 repo 名稱為 `x'; DROP TABLE runs; --`，則會執行 `DROP TABLE runs`。建議改用參數化查詢（sqlite3 支援 `?` 佔位符），或至少對輸入進行跳脫。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

## _ruletest:shell:2:3 ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**路徑處理不當：`cleanup_cache` 使用 `rm -rf` 搭配未驗證的 `$ROOT`**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 函式執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 包含空白或特殊字元，或使用者誤將 `$ROOT` 設為 `/`，可能導致災難性刪除。此外，`$ROOT` 未經驗證是否為預期目錄。

**失敗情境**：若 `$ROOT` 為 `/`，則會執行 `rm -rf //.cache/*`，可能刪除系統檔案。

**建議修法**：驗證 `$ROOT` 為絕對路徑且非根目錄，並使用更安全的刪除方式（如 `find "$ROOT/.cache" -mindepth 1 -delete`）。

evidence：diff 第 62 行：`rm -rf "$ROOT"/.cache/*`，`$ROOT` 未經驗證。

## _ruletest:shell:3:5 ｜ `sandbox/repo_sync.sh:41` ｜ 自動：SH-S3 → valid

**ahead 計算可能失敗，導致 SQL 插入空值**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若執行失敗（例如 origin/$BRANCH 不存在），`ahead` 將為空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查 `git rev-list` 的退出碼，失敗時設定預設值或跳過。

evidence：第 31 行未處理指令失敗的情況。
