# ph-B1 人工標記單（盲標：不含 confidence、severity）

自動 60 筆、人工 26 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-B1:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，因此多次呼叫會共用同一個列表，導致結果累積。

失敗情境：第一次呼叫 `collect_authors('repo', [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors('repo', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是預期的 `['carol']`。

建議：將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 29 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-B1:python:1:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 對空 timeline 的處理不正確**

existing_code:
```
events = pr.get("timeline", [])
    if not events:
        return 0
```

body：`review_latency` 在 `events` 為空時回傳 0，但這會與「真正的 latency 為 0」混淆。此外，`events` 來自 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位，因此 `events` 永遠是空列表，導致 latency 永遠為 0。

失敗情境：即使 PR 有 review 活動，只要 `_fetch` 沒有特別要求 timeline，`review_latency` 就會回傳 0，使指標失去意義。

建議：確認 API 回應是否包含 timeline，若無則需額外請求；若確實可能為空，應回傳 `None` 或拋出例外，而不是 0。

evidence：diff 第 35-37 行：`pr.get("timeline", [])` 預設空列表，且空列表時回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B1:python:1:5 ｜ `sandbox/pr_stats.py:72` ｜ 候選：無

**export_csv 未處理欄位中的逗號或換行，可能產生格式錯誤的 CSV**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 寫入 `author`、`latency`、`kind`，未對欄位值做 CSV 跳脫。若 `author` 包含逗號或換行（GitHub 使用者名稱可能包含逗號？），會破壞 CSV 結構。

失敗情境：若 `author` 為 `"Doe, John"`，輸出會變成 `Doe, John,123,normal`，導致解析錯誤。

建議：使用 `csv` 模組的 `writer` 來正確處理跳脫。

evidence：diff 第 72 行：直接以 f-string 寫入，未使用 csv 模組。

- 規則提示 PY-A6：open 沒用 with

## ph-B1:python:2:7 ｜ `sandbox/pr_stats.py:38` ｜ 候選：PY-B1

**review_latency 對空 events 回傳 0，可能誤導指標**

existing_code:
```
if not events:
        return 0
```

body：`review_latency` 在 `events` 為空時回傳 0，但 0 可能被解讀為「零延遲」，而實際上可能是資料缺失。建議回傳 None 或拋出例外，讓呼叫端處理。

evidence：diff 第 35-36 行：空 events 回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B1:python:3:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續 `pr["user"]["login"]` 會拋出 `TypeError`，且沒有上下文可除錯。

具體失敗情境：GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 執行 `pr["user"]` 時拋出 `TypeError: 'NoneType' object is not subscriptable`。

建議：至少記錄例外並重新拋出，或讓 `_fetch` 在失敗時拋出明確的例外，由呼叫端處理。

evidence：diff 第 25 行 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 30 行）和 `main`（第 75 行）被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B1:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若此函式被多次呼叫（例如在同一個行程中處理多個 repo），先前呼叫的結果會殘留，導致作者清單不正確。

具體失敗情境：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：將預設值改為 `None`，在函式內初始化為空 list。

evidence：diff 第 29 行，函式定義使用可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-B1:python:4:1 ｜ `sandbox/pr_stats.py:23` ｜ 候選：PY-A1, PY-K-status

**錯誤被完全吞掉，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 JSON、或 HTTP 錯誤狀態碼（如 404）發生時，_fetch 會回傳 None。呼叫端（collect_authors 和 main 中的迴圈）直接對回傳值進行索引（pr["user"]["login"]）或屬性存取，將導致 TypeError 或 AttributeError，且原始錯誤被隱藏，難以除錯。

建議：至少記錄例外（logging.exception），或重新拋出；若需回傳 None，呼叫端應檢查並處理。

evidence：diff 第 23-24 行：except: pass

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B1:python:4:6 ｜ `sandbox/pr_stats.py:42` ｜ 候選：PY-B1

**threshold_from_env 對無效環境變數拋出未處理的 ValueError**

existing_code:
```
if raw:
        return {"days": int(raw)}
```

body：threshold_from_env 將環境變數 PR_STALE_DAYS 轉為整數，若值不是有效整數（如 'abc'），int() 會拋出 ValueError，導致程式崩潰。建議捕捉例外並回退到預設值或提供明確錯誤訊息。

evidence：diff 第 42-43 行

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B1:python:5:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，且錯誤訊息不明確。

失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

建議：不要吞掉例外，讓錯誤向上傳播，或在 `_fetch` 內處理並拋出明確的例外；若需回傳 `None`，呼叫端必須檢查。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 66 行）被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B1:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A4

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留下來，造成結果不正確。

失敗情境：若在同一個程序內呼叫 `collect_authors` 兩次（例如測試或迴圈），第二次呼叫的 `seen` 會包含第一次的結果，導致作者清單重複。

建議：改用 `seen=None`，在函式內初始化為空 list。

evidence：diff 第 28 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 修改。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-B1:python:5:4 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序，可能拋出 KeyError 或 IndexError**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 `events` 可能為空（已檢查）或事件物件缺少 `created_at` 欄位（未檢查）。此外，GitHub API 的 timeline 事件不一定按時間排序，若未排序，計算出的 latency 可能為負值。

失敗情境：若某個 timeline 事件沒有 `created_at` 欄位（例如某些事件類型），會拋出 `KeyError`。

建議：先驗證事件結構，或使用 `events[0].get("created_at")` 並處理缺失；若需正確 latency，應先依時間排序。

evidence：diff 第 34-35 行：直接使用索引和鍵存取，未做防禦性檢查。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B1:python:5:6 ｜ `sandbox/pr_stats.py:48` ｜ 候選：無

**_to_epoch 使用 fromisoformat 可能無法解析 GitHub 的時間格式**

existing_code:
```
return int(datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
```

body：`_to_epoch` 使用 `datetime.datetime.fromisoformat` 解析時間字串，但 GitHub API 回傳的時間格式為 ISO 8601，例如 `2023-01-01T12:00:00Z`，Python 3.10 及以下版本的 `fromisoformat` 不支援 `Z` 後綴，會拋出 `ValueError`。

失敗情境：在 Python 3.9 環境中執行，遇到 `Z` 結尾的時間字串會崩潰。

建議：使用 `datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")` 或先替換 `Z` 為 `+00:00`（目前程式碼有做 `replace`，但 `fromisoformat` 在舊版仍可能不支援）。

evidence：diff 第 39 行：依賴 `fromisoformat` 的行為，但未考慮版本相容性。


## ph-B1:shell:2:7 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄列表可能導致問題**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會導致迴圈變數分割錯誤。建議使用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：diff 第 70 行：`for d in $(ls "$ROOT"); do`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-B1:shell:3:3 ｜ `sandbox/repo_sync.sh:33` ｜ 候選：SH-S4, SH-K-gitfail

**`cd` 失敗後未中止，後續 git 指令可能在錯誤目錄執行**

existing_code:
```
cd "$dir"
```

body：`sync_one` 中 `cd "$dir"` 若失敗（例如目錄不存在或權限不足），腳本不會停止，後續 `git fetch`、`git checkout` 等指令會在錯誤的目錄執行，可能導致非預期行為。建議在 `cd` 後檢查 `$?` 或使用 `set -e`，或改為 `cd "$dir" || return 1`。

evidence：第 31 行直接 `cd`，未檢查結果。

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-B1:shell:3:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 解析目錄列表，路徑含空白或特殊字元時可能出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出進行分詞，若 repo 目錄名稱包含空白、換行或 glob 字元，會導致迭代錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：第 68 行使用 `ls` 且未加引號，容易受特殊字元影響。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-B1:shell:4:3 ｜ `sandbox/repo_sync.sh:37` ｜ 候選：SH-B1(unless)

**git checkout 未加引號可能導致參數注入**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 未加引號，若 branch 名稱包含空格或特殊字元，可能被 shell 拆解成多個參數。雖然開頭有驗證 branch 格式，但驗證允許 `.`、`/`、`-` 等字元，仍可能造成意外行為。建議改為 `git checkout "$BRANCH"`。

evidence：第 33 行未加引號。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-B1:probe:2:2 ｜ `sandbox/release_notes.py:34` ｜ 候選：PR-B2(unless)

**load_config 未處理 JSON 以外的檔案讀取錯誤**

existing_code:
```
except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案存在但無法讀取（例如權限不足、I/O 錯誤），會拋出未處理的 `OSError` 導致程式崩潰。建議捕捉 `OSError` 並記錄警告後回傳空 dict，或讓錯誤向上傳播並在 main 中處理。

evidence：diff 中 `load_config` 的 except 子句僅涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`，未涵蓋其他可能的 `OSError`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-B1:probe:2:3 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

**post 未處理 HTTP 錯誤狀態碼，可能誤報成功**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 僅在 `urllib.error.URLError` 時回傳 False，但若伺服器回傳 4xx/5xx 狀態碼，`urlopen` 會拋出 `urllib.error.HTTPError`（為 `URLError` 子類別），因此會被捕捉並回傳 False。然而，若伺服器回傳 3xx 重定向，`urlopen` 預設會自動跟隨，最終可能得到 2xx 或拋出例外。但若伺服器回傳 204 No Content，`resp.status` 為 204，符合 `200 <= resp.status < 300`，回傳 True，但實際上可能未成功處理。建議明確檢查 `resp.status` 是否為 2xx，並考慮處理非 2xx 的 HTTP 狀態碼。

evidence：diff 中 `post` 函式僅依賴 `urlopen` 的例外處理，未明確處理 HTTP 狀態碼。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B1:probe:2:4 ｜ `sandbox/release_notes.py:39` ｜ 候選：PR-X1, PR-B3(unless)

**max_items 未限制 NOTES_MAX 的下限，可能導致切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為 0 或負數，`commits[: max_items()]` 會回傳空清單或錯誤切片，導致公告內容不完整或程式錯誤。建議加上下限檢查，例如 `max(1, int(raw))` 或明確拒絕非正整數。

evidence：diff 中 `max_items` 僅處理 ValueError，未檢查轉換後的數值是否為正整數。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-B1:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 且通過 `TAG_RE` 的 tag）。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 會先執行 `tags.index(tag)`，若 `tag` 不在列表中會拋出 `ValueError`，但若列表為空且 `tag` 不在其中，`tags.index(tag)` 同樣拋出 `ValueError`，這部分已有處理。然而，若 `tag` 是列表中的第一個元素，`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個元素，這可能不是預期的「前一個 tag」。建議在 `main` 中檢查 `tags.index(tag) == 0` 的情況，並明確處理沒有前一個 tag 的狀況。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B1:probe:4:2 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**`NOTES_MAX` 設為負數或零時會產生非預期結果**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只檢查了是否為整數，沒有檢查是否為正數。若使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別回傳空 list 或倒數第二個元素之前的全部 commit（Python 切片負索引行為）。這可能導致公告內容不完整或完全空白。

建議：在轉換後檢查 `value <= 0` 時記錄警告並回傳 `DEFAULT_MAX`。

evidence：diff 中 `max_items` 函式只處理 `ValueError`，未驗證數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-B1:probe:4:3 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**未驗證 webhook URL 的 scheme，可能造成 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接將 `url` 傳給 `urllib.request.Request`，沒有檢查 scheme 是否為 `https` 或 `http`。如果 `NOTES_WEBHOOK` 被設定為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或連線到非預期的資源。雖然環境變數通常由使用者控制，但若此工具被用於 CI/CD 且環境變數來自外部輸入，就可能被利用。

建議：在 `post` 前檢查 `urlparse(url).scheme in ('http', 'https')`，否則回傳錯誤。

evidence：diff 中 `post` 函式直接使用 `url` 建立 Request，無 scheme 檢查。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B1:probe:4:4 ｜ `sandbox/release_notes.py:32` ｜ 候選：PR-B2(unless)

**`load_config` 未處理權限錯誤，可能導致程式崩潰**

existing_code:
```
except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案存在但無讀取權限（`PermissionError`），程式會直接拋出 traceback。建議捕捉 `OSError` 並記錄警告後回傳空 dict，或讓錯誤訊息更友善。

evidence：diff 中 `load_config` 的 except 子句未包含 `PermissionError`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-B1:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**`list_tags` 回傳空列表時，`tags.index(tag) - 1` 會取到最後一個元素**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]`。如果 `tags` 是空列表（例如 repo 沒有任何符合 `v*` 的 tag），`tags.index(tag)` 會拋出 `ValueError`，但更隱晦的是如果 `tags` 非空但 `tag` 不在其中，`tags.index(tag)` 也會拋出 `ValueError`，這部分已有檢查。然而，如果 `tags` 只有一個元素且就是 `tag`，`tags.index(tag) - 1` 會是 `-1`，取到最後一個元素（即 `tag` 本身），導致 `prev` 等於 `tag`，`git log prev..tag` 會是空範圍。建議在取 `prev` 前檢查 `tags.index(tag) > 0`，否則回報錯誤。

evidence：diff 第 48 行：`prev = tags[tags.index(tag) - 1]`，未處理 `tags` 只有一個元素或 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B1:probe:5:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，沒有檢查 scheme 是否為 `https` 或 `http`。攻擊者若控制環境變數，可指定 `file://` 等 scheme 讀取本機檔案或觸發其他內部請求。建議驗證 URL 的 scheme 與 host。

evidence：diff 第 91 行：`url` 來自環境變數，未經 scheme 驗證即用於 `urllib.request.Request`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B1:probe:5:5 ｜ `sandbox/release_notes.py:96` ｜ 候選：PR-A2, PR-B7(unless)

**`post` 只捕捉 `URLError`，HTTP 錯誤狀態碼不會被記錄**

existing_code:
```
except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 404、500）時會拋出 `urllib.error.HTTPError`，它是 `URLError` 的子類別，所以會被捕捉並記錄。但若伺服器回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能得到 200 或拋出錯誤。若回傳 4xx/5xx，`HTTPError` 會被捕捉，但 `post` 回傳 `False`，呼叫端會回傳 1，但沒有記錄具體的 HTTP 狀態碼。建議在 `except` 中檢查 `e.code` 並記錄。

evidence：diff 第 95-97 行：捕捉 `URLError` 但未記錄 HTTP 狀態碼。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-B1:python:2:5 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**threshold_from_env 的 int 轉換未處理例外，可能導致程式崩潰**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 int，若該值不是合法整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式終止。建議使用 try/except 或先驗證輸入。

evidence：diff 第 45 行：`int(raw)` 無例外處理。

## ph-B1:python:4:4 ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

**檔案未使用 with 開啟，可能洩漏資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：export_csv 使用 open 開啟檔案，但未使用 with 或 try/finally 確保關閉。若寫入過程中發生例外（如磁碟滿、權限錯誤），檔案控制代碼不會被關閉，可能導致資源洩漏或資料不完整。

建議：使用 with open(path, 'w') as f: 並在區塊內寫入。

evidence：diff 第 59-63 行

## ph-B1:shell:1:3 ｜ `sandbox/repo_sync.sh:37` ｜ 自動：SH-K-gitfail → valid

**`git checkout` 與 `git merge` 失敗未中止，可能導致錯誤結果**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中 `git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導至 log，未檢查退出狀態。若 checkout 失敗（例如 branch 不存在），後續 merge 可能基於錯誤的 branch 執行，或 `ahead` 計算錯誤。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：第 34-35 行未檢查 git 指令的退出碼。

## ph-B1:shell:2:4 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時資料，導致錯誤的 ahead 計算或合併失敗。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：diff 第 30-32 行：`git fetch origin --prune 2>>"$LOG"` 等

## ph-B1:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入漏洞**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`$name` 與 `$BRANCH` 直接插入 SQL 字串，未經跳脫。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用 sqlite3 的參數綁定功能，或至少以 `sqlite3_escape` 函數跳脫輸入。

evidence：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

## ph-B1:shell:5:3 ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未設定或為空，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `.cache` 不存在，`rm` 會報錯但腳本仍繼續。建議先檢查 `$ROOT` 是否為空，並使用 `find` 或 `rm -rf -- "$ROOT/.cache"` 後再重建目錄。

evidence：第 58 行直接使用變數拼接路徑，且未檢查 `$ROOT` 是否為空。

## ph-B1:probe:3:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**子程序失敗時未檢查回傳碼，可能導致後續處理錯誤資料**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空列表，呼叫端會誤以為沒有 commit 而正常結束（回傳 0）。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

evidence：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `main` 中 `if not commits:` 會將空列表視為正常情況回傳 0。
