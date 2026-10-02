# v04 人工標記單（盲標：不含 confidence、severity）

自動 58 筆、人工 21 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v04:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空 list，這是可變預設值。每次呼叫若未提供 `seen`，會共用同一個 list 物件，導致先前呼叫的結果殘留。例如：
```python
collect_authors('repo', [1])  # 回傳 ['user1']
collect_authors('repo', [2])  # 回傳 ['user1', 'user2']，而不是 ['user2']
```
建議改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 29 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v04:python:1:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件有 created_at 欄位**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 GitHub API 的 timeline 事件可能因類型不同而缺少 `created_at`（例如某些事件只有 `submitted_at`）。若欄位缺失，會拋出 `KeyError`。

建議：
- 使用 `events[0].get("created_at")` 並檢查是否為 None。
- 或過濾出有 `created_at` 的事件。

evidence：diff 第 62-63 行：直接存取鍵值，未處理缺失。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v04:python:1:8 ｜ `sandbox/pr_stats.py:48` ｜ 候選：無

**_to_epoch 使用 fromisoformat 可能無法解析所有 ISO 8601 格式**

existing_code:
```
return int(datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
```

body：`_to_epoch` 使用 `datetime.datetime.fromisoformat`，但 Python 的 `fromisoformat` 在較舊版本（<3.11）不支援所有 ISO 8601 格式（例如帶有 `Z` 的字串需要先替換，這裡有做，但可能還有其他變體）。若時間戳格式不符，會拋出 `ValueError`。

建議：
- 考慮使用 `datetime.datetime.strptime` 或 `dateutil.parser` 來處理更多格式。
- 或確保 API 回傳格式固定。

evidence：diff 第 68 行：依賴 `fromisoformat` 的解析能力。


## v04:python:2:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 函式中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。這會導致呼叫端（如 `collect_authors` 和 `main` 中的 `pr["user"]["login"]`）在 `_fetch` 回傳 `None` 時拋出 `TypeError` 或 `KeyError`，且沒有明確的錯誤訊息。

建議：
- 至少記錄例外並重新拋出，或回傳一個明確的錯誤值。
- 使用 `raise ... from err` 保留原始追蹤資訊。
- 考慮使用 `urllib.error.HTTPError` 來處理特定的 HTTP 狀態碼。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v04:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫之間共用同一個 list。這可能導致非預期的行為，例如第二次呼叫時會包含第一次的結果。

建議：將預設值改為 `None`，並在函式內初始化為空 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 29 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v04:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**例外被吞掉，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx 狀態碼、或 JSON 解析失敗時，函式會回傳 None。呼叫端（collect_authors 和 main）直接使用回傳值，例如 pr["user"]["login"]，會導致 TypeError 或 KeyError，且沒有明確的錯誤訊息。

建議：
- 至少記錄例外（logging.exception）並重新拋出，或回傳一個明確的錯誤物件。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 在呼叫端處理 None 的情況。

evidence：diff 第 24 行：`except:` 後接 `pass`，且函式無回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v04:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3, PY-A4

**可變預設值 seen=[] 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：collect_authors 函式的參數 seen 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。雖然目前程式碼中只呼叫一次，但若未來重複呼叫，會累積先前結果，造成非預期行為。

建議：將預設值改為 None，並在函式內初始化為空串列。

evidence：diff 第 28 行：`seen=[]` 為可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v04:python:3:6 ｜ `sandbox/pr_stats.py:38` ｜ 候選：PY-B1

**review_latency 對空事件列表回傳 0，可能誤導**

existing_code:
```
if not events:
        return 0
```

body：review_latency 函式在 events 為空時回傳 0，這可能被解讀為「零延遲」，但實際上可能是資料缺失。建議回傳 None 或拋出例外，讓呼叫端處理。

evidence：diff 第 33-34 行：空列表回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v04:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3, PY-A4

**可變預設值 seen=[] 導致跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：collect_authors 函式的 seen 參數預設值為空串列，這在 Python 中只會建立一次，並在所有呼叫之間共用。如果呼叫者未傳入 seen，多次呼叫會累積先前呼叫的結果，導致 authors 清單包含重複或非預期的資料。

建議：將預設值改為 None，並在函式內初始化為空串列。

evidence：diff 第 28 行

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v04:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，會在函式定義時建立一次，並在所有呼叫之間共用。如果呼叫多次，前一次的結果會殘留在 `seen` 中，導致後續呼叫的結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 29 行：參數 `seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v04:shell:1:5 ｜ `sandbox/repo_sync.sh:33` ｜ 候選：SH-S4, SH-K-gitfail

**工作目錄假設：`sync_one` 依賴 `cd` 成功，但未檢查**

existing_code:
```
cd "$dir"
```

body：`sync_one` 使用 `cd "$dir"` 切換目錄，若目錄不存在或無權限，`cd` 失敗後續指令將在錯誤的目錄執行，可能操作錯誤的 repo。建議檢查 `cd` 的退出碼，失敗時回報錯誤並跳過該 repo。

evidence：diff 第 32 行，未檢查 `cd` 的結果。

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## v04:shell:1:6 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**潛在的變數未初始化：`ahead` 可能為空導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗，`ahead` 可能為空字串，後續的 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致 SQL 語法錯誤。建議在 git 指令失敗時設定 `ahead=0` 或中止處理。

evidence：diff 第 39 行，未處理 git 指令失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v04:shell:1:7 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 `ls` 解析目錄列表，可能因檔名包含換行或空白而錯誤**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白、換行或特殊字元，將被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

evidence：diff 第 84 行，使用 `ls` 的輸出進行 word splitting。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v04:shell:3:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**ls 輸出未加引號，路徑含空白時會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用命令替換，若 repo 目錄名稱包含空白或換行，迴圈會錯誤分割。建議改用 `find` 或 `for d in "$ROOT"/*` 並檢查是否為目錄。

evidence：diff 第 76 行：`for d in $(ls "$ROOT"); do`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v04:shell:3:5 ｜ `sandbox/repo_sync.sh:37` ｜ 候選：SH-B1(unless)

**git checkout 未加引號，branch 名稱含特殊字元可能出錯**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 未將 `$BRANCH` 用雙引號包住。雖然開頭有驗證格式，但若 branch 名稱包含空白（例如 `feature branch`），仍可能被 shell 分割。建議改為 `git checkout "$BRANCH"`。

evidence：diff 第 33 行：`git checkout $BRANCH 2>>"$LOG"`

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## v04:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 和 `$BRANCH` 插入 SQL 字串。如果 repo 目錄名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL。攻擊者可以建立惡意名稱的 repo 目錄，導致資料庫被竄改或資料外洩。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`。

evidence：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v04:shell:4:4 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**ls 輸出解析脆弱：檔名包含空白或換行會導致錯誤**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，但 `ls` 的輸出會受到檔名中的空白、換行等特殊字元影響而分割錯誤。例如，若 repo 目錄名稱為 `my repo`，會被拆成 `my` 和 `repo` 兩個項目。建議改用 glob：`for d in "$ROOT"/*/; do` 並去除尾隨斜線，或使用 `find` 搭配 `-print0` 和 `while read -d ''`。

evidence：diff 第 68 行：`for d in $(ls "$ROOT"); do`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v04:probe:3:2 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

**`load_config` 未驗證 JSON 頂層型別**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 直接回傳 `json.load` 的結果，但沒有檢查它是否為 dict。如果 `.release-notes.json` 的內容是陣列、字串或數字，`cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

建議在 `json.load` 後檢查 `isinstance(data, dict)`，若不是則拋出明確的錯誤訊息。

evidence：diff 中 `load_config` 函式直接回傳 `json.load(fh)` 的結果，沒有型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v04:probe:4:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`-1` 會取到最後一個元素，而不是報錯。這會導致錯誤的 `prev`，進而產生錯誤的 commit 範圍。應檢查 `tags.index(tag) == 0` 並處理此情況（例如提示沒有前一個 tag 或使用其他基準）。

evidence：diff 中該行直接使用 `-1` 索引，未處理邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v04:probe:4:3 ｜ `sandbox/release_notes.py:103` ｜ 候選：無

**設定檔載入可能拋出未處理的例外**

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

body：`load_config` 在檔案存在但內容不是合法 JSON 時會拋出 `SystemExit`，但若檔案權限不足或讀取時發生其他 I/O 錯誤，會拋出未捕捉的 `OSError`，導致程式直接崩潰。建議捕捉 `OSError` 並提供友善錯誤訊息。

evidence：diff 中 `load_config` 只處理了 `FileNotFoundError` 和 `JSONDecodeError`，未處理其他 `OSError`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑

## v04:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個符合格式的 tag 時，prev 會造成 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`tags[-1]` 會取到最後一個 tag，這通常不是預期的行為，且可能導致錯誤的 commit 範圍。建議檢查 `tags.index(tag) == 0` 的情況，並決定要如何處理（例如回報錯誤或使用其他基準）。

evidence：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1` 作為索引，未處理 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v04:python:2:5 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**threshold_from_env 未處理 int() 轉換失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，如果該值不是有效的整數（例如 "abc"），會拋出 `ValueError` 且沒有處理。

建議：使用 try/except 捕捉轉換錯誤，並提供預設值或明確的錯誤訊息。

evidence：diff 第 51 行：`int(raw)` 沒有例外處理。

## v04:python:4:5 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**環境變數轉換為整數未處理例外**

existing_code:
```
return {"days": int(raw)}
```

body：threshold_from_env 函式將環境變數 PR_STALE_DAYS 轉換為整數，但未處理 ValueError。若使用者設定非數字值（例如 "abc"），程式會崩潰。

建議：使用 try/except 捕捉轉換錯誤，並提供預設值或錯誤訊息。

evidence：diff 第 52 行

## v04:shell:1:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入風險：`eval` 執行未受信任的 hook 路徑與 repo 名稱**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 repo 目錄名稱，可能包含 shell 特殊字元（如 `;`, `$(...)`, 反引號等），導致任意命令執行。例如，若 repo 名稱為 `x; rm -rf ~`，則會執行 `rm -rf ~`。建議避免使用 `eval`，改用直接執行：`"$hook" "$repo"`，並確保 hook 路徑與參數正確引用。

evidence：diff 第 55 行使用 `eval` 執行包含變數的字串，其中 `$repo` 來自外部輸入。

## v04:shell:2:6 ｜ `sandbox/repo_sync.sh:68` ｜ 自動：SH-B2 → invalid

**summarize 中 total 計算錯誤**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 grep 失敗（例如檔案不存在），total 會被設為 0，但若 grep 成功但檔案為空，total 為 0 且 exit code 為 1，導致 total 被重設為 0，但實際上應為 0。此處邏輯正確但易混淆。更嚴重的問題是若 log 檔案不存在，grep 失敗，total=0，但後續 `tail -100 "$LOG"` 會失敗。建議先檢查檔案存在。

evidence：diff 第 68 行

## v04:shell:4:5 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**git 指令失敗未中止，可能導致後續操作在錯誤狀態下執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"

  # branch 已在開頭驗過格式，可以直接用
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中的 `git fetch`、`git checkout`、`git merge` 失敗時僅將錯誤寫入 log，但腳本繼續執行。例如，若 `git checkout` 失敗（例如 branch 不存在），後續的 `git merge` 和 `git rev-list` 可能在不正確的 branch 上執行，導致資料錯誤。建議在每個 git 指令後檢查退出碼，失敗時 return 或 exit，或使用 `set -e`（但需注意 `set -e` 對管線和條件式的影響）。

evidence：diff 第 31-35 行：git 指令沒有錯誤處理

## v04:shell:5:7 ｜ `sandbox/repo_sync.sh:41` ｜ 自動：SH-S3 → valid

**變數 `ahead` 可能未初始化或為空，導致數值比較錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因空字串而報錯，且 `sqlite3` 插入時 `$ahead` 為空可能導致 SQL 錯誤。

建議在取得 `ahead` 後檢查是否為數字，或設定預設值 0。

evidence：diff 第 34 行：未檢查 `git rev-list` 的退出碼或輸出是否為數字。

## v04:probe:3:3 ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**`max_items` 未處理負數或非整數值**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉成整數，但沒有檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，導致截斷錯誤。另外，若值為 `0`，會回傳空列表，可能不是預期行為。

建議加上檢查，確保值為正整數，否則使用預設值。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。
