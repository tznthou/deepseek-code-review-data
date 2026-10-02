# ph-A3 人工標記單（盲標：不含 confidence、severity）

自動 63 筆、人工 22 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-A3:python:1:2 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A4

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen=[]` 是可變預設值，會在多次呼叫間共用同一個 list。雖然目前程式只呼叫一次，但這是一個常見的陷阱，未來若重複呼叫會導致結果累積。建議改為 `seen=None`，在函式內初始化為空 list。

evidence：diff 第 27 行。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A3:python:2:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 使用可變預設值，且環境變數轉換可能失敗**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`def threshold_from_env(default={"days": 7})` 的預設參數是 dict，雖然函式內沒有修改它，但若未來修改可能導致跨呼叫污染。此外，`int(raw)` 沒有處理 `ValueError`，當環境變數 `PR_STALE_DAYS` 不是數字時會拋出例外。建議改用 `default=None` 並在函式內設定，同時捕捉轉換例外。

evidence：diff 第 44 行：可變預設值 dict，且第 46 行 `int(raw)` 未處理轉換失敗。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## ph-A3:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫 `collect_authors` 時，先前呼叫的結果會殘留在 `seen` 中，造成資料污染。

建議：改用 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設值，且函式內有 `seen.append(...)` 修改該 list。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A3:python:3:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且元素有 created_at，可能拋出例外**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但第一個或最後一個元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，`_to_epoch` 對時間格式有嚴格要求，若 API 回傳格式變更可能失敗。

建議：使用 `events[0].get("created_at")` 並處理缺失情況。

evidence：diff 第 55-56 行：直接存取 `created_at`，沒有檢查鍵是否存在。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A3:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫之間共用同一個 list。這可能導致非預期的行為：例如在同一個程序內多次呼叫 `collect_authors` 時，先前呼叫的作者會被保留下來。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：函式定義使用可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A3:python:4:5 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 存在且有 created_at，可能導致 KeyError**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 `events` 可能為空（已檢查）或元素缺少 `created_at` 鍵（未檢查）。如果 GitHub API 回傳的 timeline 事件缺少該欄位，會拋出 `KeyError`。

建議：使用 `.get("created_at")` 並處理缺失情況，或驗證事件結構。

evidence：diff 第 35-36 行：直接存取鍵，未檢查鍵是否存在。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A3:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫共用狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫之間共用同一個 list。如果呼叫者沒有傳入 `seen`，每次呼叫都會累積到同一個 list，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 27 行：參數 `seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-A3:python:5:4 ｜ `sandbox/pr_stats.py:72` ｜ 候選：無

**export_csv 未處理 CSV 特殊字元，可能產生格式錯誤或注入**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 寫入 CSV，未對欄位值進行轉義。如果 `author`、`latency` 或 `kind` 包含逗號、引號或換行符，會破壞 CSV 格式，甚至可能被用於 CSV 注入（例如以 `=`, `+`, `-`, `@` 開頭的值）。

建議：使用 `csv` 模組的 `csv.writer` 來正確處理轉義。

evidence：diff 第 53 行：直接寫入未轉義的值。

- 規則提示 PY-A6：open 沒用 with

## ph-A3:python:5:6 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 已排序，可能計算錯誤**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]` 的 `created_at` 來計算延遲，但 GitHub API 回傳的 timeline 事件不一定按時間排序。如果事件順序混亂，計算出的延遲可能為負值或不準確。

建議：先按 `created_at` 排序事件，或明確使用 `min` 和 `max`。

evidence：diff 第 34-35 行：直接使用第一個和最後一個事件，未排序。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A3:shell:2:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令使用字串拼接方式將 `$name` 與 `$BRANCH` 插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。

**失敗情境**：假設 `$ROOT` 下有一個目錄名為 `x'; DROP TABLE runs; --`，則執行的 SQL 會變成：
```sql
INSERT INTO runs VALUES('x'; DROP TABLE runs; --', 'main', 0, datetime('now'))
```
這會導致 `runs` 資料表被刪除。

**建議修法**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數進行單引號跳脫（`${name//\'/\'\'}`）。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A3:shell:2:4 ｜ `sandbox/repo_sync.sh:37` ｜ 候選：SH-K-gitfail, SH-B1(unless)

**變數未加引號：`git checkout $BRANCH` 可能因 branch 名稱含空格或特殊字元而失敗**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 未將 `$BRANCH` 以雙引號包覆。雖然開頭有驗證 branch 名稱格式，但允許的字元包含 `.`、`_`、`/`、`-`，這些字元在 shell 中通常安全，但若 branch 名稱包含空格（雖然驗證不允許）或 glob 字元（如 `*`），可能導致非預期行為。

**失敗情境**：若 branch 名稱包含 `*`（例如 `feature/*`），shell 會展開成目前目錄下的檔案名稱，導致 `git checkout` 收到錯誤參數。

**建議修法**：改為 `git checkout "$BRANCH"`。

evidence：diff 第 36 行：`git checkout $BRANCH 2>>"$LOG"`

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-A3:shell:2:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**`for d in $(ls "$ROOT")` 可能因檔名包含空格或換行而失敗**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：使用 `ls` 的輸出進行迴圈，若 repo 目錄名稱包含空格、換行或其他特殊字元，會被拆成多個項目，導致後續處理錯誤。

**失敗情境**：若 `$ROOT` 下有一個目錄名為 `my repo`，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致 `target` 路徑錯誤。

**建議修法**：使用 `find` 或 glob 搭配 null 分隔符，例如：
```bash
while IFS= read -r -d '' d; do
  ...
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
```

evidence：diff 第 70 行：`for d in $(ls "$ROOT"); do`

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-A3:shell:3:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 中的 `sqlite3` 指令直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL。雖然 branch 有格式驗證，但 repo 名稱完全未驗證。建議改用參數化查詢（sqlite3 支援 `?` 佔位符）或至少使用 `sqlite3` 的 `-cmd` 與 `printf` 進行跳脫。

evidence：diff 第 41 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 來自 `basename "$dir"`，未經驗證或跳脫。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A3:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號字串插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或注入攻擊。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 名稱來執行任意 SQL 指令，可能竄改或刪除資料庫內容。

**失敗情境**：
1. 建立名為 `x'; DROP TABLE runs;--` 的 repo 目錄，執行腳本後 `runs` 表將被刪除。
2. 傳入 branch 名稱 `main'; DELETE FROM runs;--`，同樣可造成資料遺失。

**建議修法**：
- 使用 `sqlite3` 的參數化查詢功能，例如：
  ```bash
  sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
  ```
- 或使用 `sqlite3` 的 `.parameter` 指令，或先以 `sqlite3` 的 `quote()` 函數處理輸入。

evidence：diff 第 44 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 直接拼接進 SQL 字串。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A3:shell:4:2 ｜ `sandbox/repo_sync.sh:56` ｜ 候選：SH-S2, SH-C1

**命令注入：`eval "$hook $repo"` 未安全處理參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval` 執行 hook 腳本，並將 repo 名稱作為參數傳入。若 repo 名稱包含 shell 特殊字元（例如 `; rm -rf ~`），將導致任意命令執行。攻擊者可建立惡意名稱的 repo 目錄，當腳本執行到該 repo 時觸發命令注入。

**失敗情境**：
1. 建立名為 `test; touch /tmp/pwned` 的 repo 目錄，執行腳本後 `/tmp/pwned` 檔案將被建立。
2. 更嚴重者，可注入 `rm -rf` 等破壞性指令。

**建議修法**：
- 避免使用 `eval`，改為直接執行：
  ```bash
  "$hook" "$repo"
  ```
- 若需傳遞多個參數，使用陣列或 `"$@"` 方式。

evidence：diff 第 54 行：`eval "$hook $repo"`，其中 `$repo` 未經跳脫直接放入 eval 字串。

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A3:probe:1:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個 tag 時，prev 取得會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是報錯。這可能導致錯誤的 commit 範圍。建議檢查 `tags.index(tag) == 0` 的情況，並給出明確的錯誤訊息。

evidence：diff 中該行直接使用 `tags.index(tag) - 1`，沒有處理 index 為 0 的邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A3:probe:2:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果 `tag` 是 `tags` 清單中的第一個元素（例如 repo 只有一個 tag），`tags.index(tag)` 回傳 0，`tags[0 - 1]` 會存取 `tags[-1]`，也就是最後一個元素，這通常不是預期的前一個版本，而且如果 `tags` 是空的（但前面已檢查 `tag in tags`，所以不會是空的），會拋出 IndexError。

建議：檢查 `tags.index(tag) == 0` 的情況，並決定如何處理（例如回報錯誤或使用其他基準）。

evidence：diff 中直接使用 `tags.index(tag) - 1` 作為索引，沒有處理 tag 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A3:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `tags` 列表中的第一個元素（例如 repo 只有一個 tag），`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個 tag，而不是拋出錯誤。這會導致 `prev` 指向錯誤的 tag，產生錯誤的 commit 範圍。建議在 `tags.index(tag) == 0` 時顯示錯誤訊息並回傳非零退出碼。

evidence：diff 中這一行直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A3:probe:3:3 ｜ `sandbox/release_notes.py:40` ｜ 候選：PR-X1, PR-B3(unless)

**`NOTES_MAX` 未處理負數或零，可能導致公告內容不完整**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 將 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表或錯誤切片，導致公告沒有內容或拋出例外。建議在轉換後檢查數值是否大於 0，否則使用預設值。

evidence：diff 中 `max_items()` 只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-A3:probe:4:3 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，沒有檢查 scheme。如果攻擊者能控制這個環境變數（例如透過 CI 設定），可以指定 `file:///etc/passwd` 或 `http://169.254.169.254/...` 等，導致讀取本機檔案或打內網服務。建議限制 scheme 為 `https`（或至少 `http` 和 `https`），並考慮阻擋內網 IP。

evidence：diff 中 `post` 直接使用 `url` 參數，沒有驗證 scheme；`url` 來自環境變數 `NOTES_WEBHOOK`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-A3:probe:4:4 ｜ `sandbox/release_notes.py:33` ｜ 候選：PR-B2(unless)

**load_config 只處理 FileNotFoundError 和 JSONDecodeError，其他例外會直接 crash**

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

body：`load_config` 開啟檔案時可能拋出 `PermissionError`、`IsADirectoryError` 等，這些沒有被捕捉，會讓程式直接 crash。雖然設定檔是選配的，但若檔案存在卻無法讀取，應該給出明確錯誤訊息。建議捕捉 `OSError` 並記錄錯誤後回傳空 dict 或退出。

evidence：diff 中 `load_config` 的 except 子句只涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-A3:probe:5:4 ｜ `sandbox/release_notes.py:36` ｜ 候選：無

**NOTES_MAX 未限制上限，可能導致記憶體耗盡**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 從環境變數讀取整數，但沒有檢查上限。如果使用者設定一個極大的值（例如 `NOTES_MAX=999999999`），`commits[: max_items()]` 會嘗試建立一個巨大的 list，可能耗盡記憶體。

建議：設定一個合理的上限（例如 1000），並在超過時記錄警告或直接截斷。

evidence：diff 中 `max_items` 函式沒有對回傳值做上限檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-A3:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**collect_authors 使用可變預設值，導致跨呼叫累積作者**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[])` 的預設參數 `seen` 是 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果呼叫者沒有傳入 `seen`，作者會被累積到同一個 list 中，造成結果錯誤。建議改為 `seen=None`，並在函式內初始化為空 list。

evidence：diff 第 28 行：可變預設值 `seen=[]`，且函式內對其進行 `append` 操作。

## ph-A3:python:3:6 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 直接存取 pr["additions"] 等鍵，若 API 回應缺少欄位會拋出 KeyError**

existing_code:
```
if pr["additions"] > 500:
        return "large"
    elif pr["changed_files"] > 20:
        return "wide"
    elif pr["title"].startswith("fix"):
        return "fix"
```

body：`classify` 假設 `pr` 字典一定包含 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限或版本不同而缺少這些欄位，導致 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

evidence：diff 第 45-50 行：直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，沒有防禦性檢查。

## ph-A3:python:5:5 ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

**export_csv 未使用 with 開啟檔案，可能導致資源洩漏**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`export_csv` 使用 `open` 和 `close`，但如果在寫入過程中發生例外，檔案可能不會被關閉。建議使用 `with open(path, "w") as f:` 來確保檔案正確關閉。

evidence：diff 第 55-58 行：手動開啟和關閉檔案，沒有使用 context manager。

## ph-A3:shell:1:6 ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**在迴圈內使用 local 宣告變數，可能導致非預期行為**

existing_code:
```
local target="$ROOT/$d"
```

body：`local target="$ROOT/$d"` 在 for 迴圈內使用 local，但 local 僅在函數內有效。此處位於 main 函數中，因此有效，但若未來重構可能造成混淆。建議改為一般賦值。

evidence：第 77 行在迴圈內使用 local。

## ph-A3:shell:3:5 ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

**使用 ls 解析目錄名稱，特殊字元可能導致錯誤**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 ls 的輸出進行 word splitting，若目錄名稱包含空格、換行或 glob 字元，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

evidence：diff 第 68 行：`for d in $(ls "$ROOT"); do`。

## ph-A3:shell:5:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入風險：eval 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$ROOT/.hooks/post-sync` 檔案名稱或 `$repo` 包含特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。

建議改用直接執行：`"$hook" "$repo"`，避免 eval。

evidence：第 61 行使用 eval，且參數來自檔案系統路徑與 repo 名稱，可能包含惡意內容。

## ph-A3:probe:2:3 ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**`max_items()` 未處理負數或過大的值**

existing_code:
```
return int(raw)
```

body：`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為負數或過大。如果設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit；如果設定為極大值，可能導致記憶體問題（雖然 commit 數量通常有限）。

建議：限制範圍，例如 `max(0, min(value, 1000))`。

evidence：diff 中 `max_items()` 直接回傳 `int(raw)`，沒有範圍檢查。
