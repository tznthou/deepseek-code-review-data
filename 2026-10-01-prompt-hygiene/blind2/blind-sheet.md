# 盲標單（不含 confidence、severity、輪次）

人工 98 筆、抽查 29 筆。結果寫進 blind-labels.csv（code,item,label,reason）。
label 只能是 valid／invalid／disputed；item 寫 expected-rules 的 id，對不到就寫 NONE。

# 需要人工判定

## M001 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M002 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M003 ｜ 標的 probe ｜ `sandbox/release_notes.py:31` ｜ 人工

**`load_config` 未處理 JSON 型別錯誤**

existing_code:
```
return json.load(fh)
```

body：`load_config` 假設 JSON 檔案內容是 dict，但若檔案內容是 list 或字串，`json.load` 會成功回傳非 dict 型別，後續 `cfg.get` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，若不是則回報錯誤。

evidence：diff 中 `load_config` 直接回傳 `json.load(fh)` 的結果，未驗證型別。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M004 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 events 非空且每個事件都有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但事件物件可能缺少 `created_at` 鍵，或 `events` 為空（已處理），但若 `events` 為空則回傳 0，可能掩蓋真實延遲。此外，若 `created_at` 格式不正確，`_to_epoch` 會拋出例外。

建議：檢查鍵是否存在，並處理時間解析錯誤。

evidence：diff 第 36-37 行：直接索引事件列表。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M005 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M006 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時作者名單不斷累積，而不是每次重新開始。

建議：改用 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 30 行：參數預設值為 `[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M007 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未檢查 scheme 是否為 http/https。若攻擊者能控制環境變數，可指定 `file://` 或 `gopher://` 等 scheme，造成 SSRF 或資訊洩漏。建議驗證 URL 的 scheme 必須是 http 或 https。

evidence：diff 中 `post` 未對 `url` 做任何驗證。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M008 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M009 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 依賴 timeline 欄位，但 GitHub API 預設不回傳，導致延遲永遠為 0**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub Pull Request API 的回應中並無 `timeline` 欄位（需另外請求 timeline 端點）。因此 `events` 永遠是空列表，函式回傳 0，指標失去意義。

**失敗情境**：所有 PR 的 latency 都顯示為 0，無法反映實際審查時間。

**建議**：若要取得 timeline，需額外呼叫 `/repos/{repo}/issues/{n}/timeline` 或使用 GraphQL；或改用其他可用欄位（如 `created_at` 與 `closed_at`）。

evidence：diff 第 43 行：`pr.get("timeline", [])`，但 `_fetch` 只請求 `/repos/{repo}/pulls/{n}`，該端點回應不含 `timeline`。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M010 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**`prev` 取得方式在 tag 為第一個版本時會拋出 `IndexError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 中的第一個元素。若使用者指定的是最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致 `git log` 範圍錯誤，可能產生不正確的 commit 列表或空列表。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個 tag。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 取得前一個 tag，未處理 index 為 0 的邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M011 ｜ 標的 probe ｜ `sandbox/release_notes.py:33` ｜ 人工

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

## M012 ｜ 標的 python ｜ `sandbox/pr_stats.py:31` ｜ 人工

**`_fetch` 回傳 `None` 時未處理，導致後續程式碼崩潰**

existing_code:
```
pr = _fetch(f"/repos/{repo}/pulls/{n}")
        seen.append(pr["user"]["login"])
```

body：`_fetch` 在例外時回傳 `None`，但 `collect_authors` 與 `main` 中直接使用 `pr["user"]["login"]` 等鍵值存取。若 API 失敗，程式將拋出 `TypeError` 或 `KeyError`，且無任何錯誤訊息。建議在呼叫處檢查回傳值是否為 `None` 或改用例外傳播。

evidence：diff 第 31-32 行顯示 `_fetch` 回傳值直接以 `pr["user"]` 存取，未檢查 `None`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M013 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 timeline 事件存在且有序**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]`，但沒有檢查 `events` 是否為空（雖然有 `if not events` 的檢查，但若 `events` 為 `None` 會拋出 `TypeError`）。此外，它假設事件按時間排序，但 GitHub API 的回傳順序可能不保證。建議明確處理 `None` 情況，並考慮對事件按時間排序後再計算。

evidence：diff 第 40-41 行：直接索引 events，未處理 None 或順序問題。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M014 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

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

## M015 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M016 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 人工

**`max_items` 未處理負數或非整數輸入**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將 `NOTES_MAX` 轉為整數，但未檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，導致最後一個 commit 被排除。此外，若輸入為浮點數字串（如 `"3.5"`），`int()` 會拋出 `ValueError`，目前有處理，但負數未處理。建議加上 `if value < 0: return DEFAULT_MAX` 或類似檢查。

evidence：diff 中 `max_items` 函式只處理 `ValueError`，未檢查負數。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M017 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 人工

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

## M018 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 人工

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

## M019 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 人工

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

## M020 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 人工

**`max_items()` 未處理負數或零，可能導致非預期行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 將環境變數 `NOTES_MAX` 轉為整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別取得空列表或全部 commit（因為 `commits[:-1]` 會排除最後一個，`commits[:0]` 會是空列表），與預期的「限制數量」不符。建議在轉換後檢查數值是否大於 0，否則回傳預設值或拋出錯誤。

evidence：diff 第 39-43 行，`int(raw)` 成功後直接回傳，未驗證數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M021 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

**SQL 注入漏洞：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆插入 SQL 語句，但未對單引號進行跳脫。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將導致 SQL 語法錯誤或 SQL 注入。攻擊者可透過建立惡意名稱的 repo 目錄或傳入特製 branch 參數，執行任意 SQL 指令，例如刪除資料表或竄改資料。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `printf` 進行跳脫。

evidence：diff 第 43 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`，其中 `$name` 與 `$BRANCH` 未經跳脫。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M022 ｜ 標的 python ｜ `sandbox/pr_stats.py:51` ｜ 人工

**`threshold_from_env` 的 `default` 參數為可變預設值，且未處理轉換失敗**

existing_code:
```
def threshold_from_env(default={"days": 7}):
    raw = os.environ.get("PR_STALE_DAYS", "")
    if raw:
        return {"days": int(raw)}
```

body：`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，是可變字典。雖然函式內未修改 `default`，但若未來修改可能引入共用狀態問題。此外，`int(raw)` 轉換環境變數時若值不是整數會拋出 `ValueError`，導致程式崩潰。

建議：改用 `default=None` 並在函式內設定預設值，並捕捉 `ValueError` 或提供明確錯誤訊息。

evidence：diff 第 48-51 行：可變預設值與未處理的 `int()` 轉換。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## M023 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

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

## M024 ｜ 標的 probe ｜ `sandbox/release_notes.py:45` ｜ 人工

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

## M025 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M026 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 人工

**`archive` 未檢查 `subprocess.run` 回傳值**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run` 預設不拋出例外，若 `tar` 或 `gh` 指令失敗（例如路徑不存在、權限不足），程式仍會繼續執行並回報成功。建議檢查 `returncode` 或使用 `check=True`。

evidence：diff 第 64 行顯示 `subprocess.run` 未檢查回傳值。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## M027 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M028 ｜ 標的 probe ｜ `sandbox/release_notes.py:37` ｜ 人工

**NOTES_MAX 負數或非整數處理不完整**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理 `ValueError`，但若 `NOTES_MAX` 設為負數，`int(raw)` 會成功，回傳負數，導致 `commits[: max_items()]` 切片行為異常（可能回傳空列表）。建議檢查數值是否為正整數，否則回退預設值。

evidence：diff 中 `max_items` 函式未檢查轉換後的數值是否為正整數。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M029 ｜ 標的 probe ｜ `sandbox/release_notes.py:30` ｜ 人工

**load_config 未驗證 JSON 型別，可能導致後續錯誤**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 回傳 `json.load` 的結果，但未檢查是否為 dict。若 `.release-notes.json` 內容是 list 或字串，`cfg.get` 會拋出 AttributeError。

建議：檢查 `isinstance(data, dict)`，否則回傳空 dict 或拋出明確錯誤。

evidence：diff 中 `load_config` 直接回傳 `json.load` 結果，未驗證型別。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M030 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

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

## M031 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 計算可能失敗，導致 SQL 插入空值**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如分支不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致 SQL 錯誤。建議檢查 `ahead` 是否為數字，失敗時設定為 0 或中止。

evidence：diff 第 36 行，未處理指令失敗。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M032 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M033 ｜ 標的 probe ｜ `sandbox/release_notes.py:34` ｜ 人工

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

## M034 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

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

## M035 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M036 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 計算可能失敗且未處理**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（如 branch 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而終止腳本。建議檢查 `ahead` 是否為數字，失敗時設為 0 或跳過。

evidence：diff 第 36 行，未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M037 ｜ 標的 python ｜ `sandbox/pr_stats.py:51` ｜ 人工

**threshold_from_env 使用可變預設值，且環境變數轉換可能失敗**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`def threshold_from_env(default={"days": 7})` 的預設參數是 dict，雖然函式內沒有修改它，但若未來修改可能導致跨呼叫污染。此外，`int(raw)` 沒有處理 `ValueError`，當環境變數 `PR_STALE_DAYS` 不是數字時會拋出例外。建議改用 `default=None` 並在函式內設定，同時捕捉轉換例外。

evidence：diff 第 44 行：可變預設值 dict，且第 46 行 `int(raw)` 未處理轉換失敗。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## M038 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M039 ｜ 標的 probe ｜ `sandbox/release_notes.py:94` ｜ 人工

**webhook 回應僅檢查狀態碼，未驗證回應內容，可能誤判成功**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 函式只檢查 HTTP 狀態碼是否在 200-299，但有些 webhook 服務（如 Slack）在請求格式錯誤時仍回傳 200，但回應內容包含錯誤訊息。這會導致程式誤以為發布成功，實際上頻道沒有收到訊息。建議檢查回應內容，例如 Slack 回傳的 `ok` 欄位。

evidence：diff 中 `post` 函式僅回傳狀態碼檢查結果，未讀取或驗證回應內容。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M040 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:94` ｜ 人工

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

## M041 ｜ 標的 probe ｜ `sandbox/release_notes.py:40` ｜ 人工

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

## M042 ｜ 標的 probe ｜ `sandbox/release_notes.py:39` ｜ 人工

**`max_items` 未處理負數或零值，可能導致切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未檢查是否為正數。若設定為負數，`commits[: max_items()]` 會回傳空 list（因為負索引切片會從尾端取，但這裡是負數會導致空結果），若為 0 則回傳空 list，可能造成公告內容空白。建議加上下限檢查，例如 `max(1, int(raw))` 或明確拒絕非正整數。

evidence：diff 中 `max_items` 函式僅處理 `ValueError`，未檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M043 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M044 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M045 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M046 ｜ 標的 python ｜ `sandbox/pr_stats.py:26` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 與 `main`）直接使用回傳值當作 dict 存取，例如 `pr["user"]["login"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：
- 至少記錄錯誤（`logging.exception`）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼（`resp.status`）並處理非 200 的情況。
- 避免使用裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError` 等）。

evidence：diff 第 26 行：`except:` 後只有 `pass`，且函式無回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M047 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M048 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

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

## M049 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 events 非空且元素有 created_at，可能拋出例外**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但第一個元素缺少 `created_at` 鍵，則會拋出 `KeyError`。此外，`pr.get("timeline", [])` 可能回傳 `None`（若 API 回傳 `timeline: null`），此時 `if not events` 會通過（`None` 為 falsy），但後續 `events[0]` 會拋出 `TypeError`。

建議：
- 檢查 `events` 是否為 list 且非空，並確認每個元素都有 `created_at`。
- 使用 `events[0].get("created_at")` 並處理缺失值。

evidence：diff 第 44-45 行：直接索引 events 並存取鍵。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M050 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 timeline 事件有 created_at 欄位**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但某些事件類型可能沒有 `created_at` 欄位，導致 `KeyError`。

失敗情境：若 timeline 中包含沒有 `created_at` 的事件（例如某些內部事件），程式會拋出例外。

建議：使用 `event.get("created_at")` 並過濾無效事件。

evidence：diff 第 34-35 行，直接存取鍵值。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M051 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M052 ｜ 標的 python ｜ `sandbox/pr_stats.py:72` ｜ 人工

**export_csv 未處理 CSV 特殊字元，可能產生格式錯誤或注入**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 寫入 CSV，未對欄位值進行轉義。如果 `author`、`latency` 或 `kind` 包含逗號、引號或換行符，會破壞 CSV 格式，甚至可能被用於 CSV 注入（例如以 `=`, `+`, `-`, `@` 開頭的值）。

建議：使用 `csv` 模組的 `csv.writer` 來正確處理轉義。

evidence：diff 第 53 行：直接寫入未轉義的值。

- 規則提示 PY-A6：open 沒用 with

## M053 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

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

## M054 ｜ 標的 probe ｜ `sandbox/release_notes.py:32` ｜ 人工

**`load_config` 只處理 `FileNotFoundError` 和 `JSONDecodeError`，其他例外會直接中斷程式**

existing_code:
```
except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 在讀取設定檔時，如果檔案存在但權限不足（`PermissionError`）或編碼錯誤（`UnicodeDecodeError`），這些例外不會被捕捉，程式會直接 crash。雖然設定檔是選配的，但這類錯誤應該被視為可預期的失敗，建議捕捉 `OSError` 並記錄警告後回傳空 dict，或至少讓錯誤訊息更友善。

evidence：diff 第 34-37 行，只捕捉了兩種例外，其他 `OSError` 子類別（如 `PermissionError`）會直接傳播。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M055 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:75` ｜ 人工

**summarize 函式在日誌為空時仍輸出訊息**

existing_code:
```
echo "本次同步共 $total 筆紀錄，詳見 $LOG"
```

body：`summarize` 函式中，若 `$LOG` 檔案不存在或為空，`total` 為 0，但仍會輸出「本次同步共 0 筆紀錄，詳見 $LOG」。這可能造成誤導。

建議在 `total` 為 0 時輸出不同訊息或省略。

evidence：diff 第 68 行：未處理 `total` 為 0 的情況。

- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M056 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M057 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設參數，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen=[]` 是可變預設參數，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留下來，造成結果不正確。

**失敗情境**：第一次呼叫 `collect_authors('repo', [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors('repo', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

**建議**：改用 `None` 作為預設值，在函式內建立新 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設參數。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M058 ｜ 標的 probe ｜ `sandbox/release_notes.py:38` ｜ 人工

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

## M059 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M060 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 使用不存在的 timeline 欄位，可能拋出 KeyError**

existing_code:
```
events = pr.get("timeline", [])
```

body：`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中並無此欄位（需另外請求 timeline 端點）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。若未來 API 變更或誤用，可能導致 `KeyError`。

建議：確認正確的資料來源，或移除該函式。

evidence：diff 第 31 行：`pr.get("timeline", [])` 中的 `timeline` 並非標準 PR 物件欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M061 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳列表中的第一個元素（例如 repo 只有一個 tag，或該 tag 是最早的版本），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式直接崩潰。建議在取 `prev` 前檢查 `tags.index(tag) == 0`，並給出明確錯誤訊息或改用其他方式處理（例如從 repo 初始 commit 開始）。

evidence：diff 第 94 行，直接對 `tags.index(tag) - 1` 取值，未處理 index 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M062 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**tag 是第一個版本時會 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 的第一個元素。如果使用者指定了最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致錯誤的比較範圍。建議檢查 `tags.index(tag) == 0` 並處理此情況。

evidence：diff 中該行直接使用 `-1` 索引，未處理 `tag` 為第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M063 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式可能回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接使用 `pr["user"]["login"]` 等鍵值，若 `pr` 為 `None` 會拋出 `TypeError`，程式直接崩潰。

失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，下一行 `pr["user"]` 就會拋出例外。

建議：在 `_fetch` 中記錄錯誤並重新拋出，或讓呼叫端檢查回傳值。

evidence：diff 第 25 行 `except: pass`，且後續 `collect_authors` 第 30 行 `seen.append(pr["user"]["login"])` 未檢查 `pr` 是否為 `None`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M064 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個符合 `v*` 的 tag），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式會直接 crash。建議在取 `prev` 前檢查 index 是否大於 0，若為 0 則提示使用者這是第一個版本，或改用其他方式取得起始點。

evidence：diff 第 104 行，直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為負數。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M065 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。這使得呼叫端無法得知失敗，後續程式碼（如 `pr["user"]["login"]`）在 `pr` 為 `None` 或缺少鍵時會拋出未處理的例外，造成程式崩潰。

建議：
- 至少記錄錯誤並重新拋出，或回傳一個明確的錯誤值。
- 使用 `raise` 保留原始例外，或改用 `except Exception as e: raise RuntimeError(...) from e`。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。

evidence：diff 第 25-26 行：`except:` 後直接 `pass`，沒有記錄或重新拋出。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M066 ｜ 標的 python ｜ `sandbox/pr_stats.py:21` ｜ 人工

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

## M067 ｜ 標的 python ｜ `sandbox/pr_stats.py:51` ｜ 人工

**threshold_from_env 的預設值為可變字典，且 int() 轉換可能拋出例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`threshold_from_env` 的參數 `default` 預設為 `{"days": 7}`，是可變字典，若函式內修改它會影響後續呼叫（目前未修改，但風險存在）。另外，`int(raw)` 若環境變數不是整數會拋出 `ValueError`，導致程式崩潰。建議改用不可變預設值並處理轉換錯誤。

evidence：diff 第 45 行：`def threshold_from_env(default={"days": 7}):`，且第 48 行 `int(raw)` 未捕捉例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## M068 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[])` 的預設值 `[]` 在函式定義時建立一次，之後每次呼叫都會沿用同一個 list。若函式被多次呼叫（例如測試或迴圈中），`seen` 會不斷累積，導致結果包含前次呼叫的作者。建議改為 `seen=None`，在函式內初始化。

evidence：diff 第 30 行：可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M069 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 events 非空且元素有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 欄位，會拋出 `KeyError`。此外，若 `events` 只有一個元素，`first` 和 `last` 相同，回傳 0，可能無法反映實際延遲。

建議：檢查每個事件是否有 `created_at`，或使用 `events[0].get("created_at")` 並處理缺失。

evidence：diff 第 36-37 行：直接存取鍵值，無防護。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M070 ｜ 標的 python ｜ `sandbox/pr_stats.py:26` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 或 `pr["additions"]` 會拋出 `TypeError`，導致程式崩潰。

建議：
- 至少記錄錯誤（logging）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼（例如 `resp.status != 200` 時拋出例外）。
- 避免使用裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError` 等）。

evidence：diff 第 26 行：`except:` 後直接 `pass`，且函式無回傳值，呼叫端未檢查。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M071 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M072 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

**`post` 未驗證 URL scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查 scheme 是否為 `https`。如果攻擊者能控制環境變數（例如在 CI 中注入），可能導致請求發送到內部服務（如 `http://169.254.169.254/...`）。建議驗證 URL 的 scheme 和 host，或至少限制為 `https`。

evidence：diff 中 `post` 函式直接使用 `url` 參數，未做任何驗證。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M073 ｜ 標的 python ｜ `sandbox/pr_stats.py:63` ｜ 人工

**classify 使用 title.startswith('fix') 可能誤分類（如 'fixed'、'fixer'）**

existing_code:
```
elif pr["title"].startswith("fix"):
```

body：`classify` 判斷 `pr["title"].startswith("fix")`，這會將標題開頭為 'fixed'、'fixer'、'fixing' 等字詞的 PR 也歸類為 'fix'，可能不是預期行為。

**失敗情境**：標題為 "Fixed typo in README" 的 PR 會被分類為 'fix'，但若預期只有 'fix' 開頭才算，則結果不正確。

**建議**：使用更精確的判斷，例如 `pr["title"].lower().startswith("fix ")` 或正則表達式。

evidence：diff 第 70 行：`startswith("fix")` 未考慮單詞邊界。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## M074 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

**使用 ls 解析目錄列表，路徑含空白或換行時會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 依賴 ls 的輸出以空白分隔，若 repo 目錄名稱包含空白或換行，將被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0` 與 `while read -d ''`。

evidence：diff 第 72 行，使用 ls 輸出進行迴圈，未處理特殊字元。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## M075 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

**_fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致回傳 `None`。呼叫端（`collect_authors` 與 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，會拋出 `TypeError` 或 `AttributeError`。例如：GitHub API 回 404（PR 不存在）時，`urlopen` 會拋出 `HTTPError`，被吞掉後 `pr` 為 `None`，下一行 `pr["user"]` 就崩潰。建議：至少記錄錯誤並重新拋出，或讓呼叫端檢查 `None`。

evidence：diff 第 25-26 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值被 `collect_authors` 和 `main` 直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M076 ｜ 標的 python ｜ `sandbox/pr_stats.py:63` ｜ 人工

**classify 使用 startswith("fix") 判斷，可能誤分類**

existing_code:
```
elif pr["title"].startswith("fix"):
```

body：`pr["title"].startswith("fix")` 會將標題開頭為 `fix` 但實際不是修復的 PR（例如 `fixation`）歸類為 `fix`。建議使用更精確的判斷，例如正規表示式或檢查完整單字。

evidence：diff 第 53 行：`startswith("fix")` 過於寬鬆。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## M077 ｜ 標的 probe ｜ `sandbox/release_notes.py:96` ｜ 人工

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

## M078 ｜ 標的 python ｜ `sandbox/pr_stats.py:22` ｜ 人工

**`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會捕捉所有例外（包含 `KeyboardInterrupt`、`SystemExit`），且未檢查 `resp.status`。若 API 回傳 404、500 或網路錯誤，函式回傳 `None`，後續 `pr["user"]` 等操作將拋出 `TypeError` 或 `KeyError`，且無任何錯誤訊息。建議至少記錄錯誤並重新拋出，或回傳明確的錯誤物件，並檢查回應狀態碼。

evidence：diff 第 22-24 行顯示 `_fetch` 的 `try` 區塊內呼叫 `urlopen`，但 `except` 子句僅 `pass`，且未檢查 `resp.status`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M079 ｜ 標的 probe ｜ `sandbox/release_notes.py:94` ｜ 人工

**HTTP 狀態碼未檢查，可能誤報成功**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 函式僅檢查 `resp.status` 是否在 200-299 之間，但 `urllib.request.urlopen` 對 4xx/5xx 回應會拋出 `HTTPError`，該例外是 `URLError` 的子類別，會被捕捉並記錄錯誤，但函式回傳 `False`。然而，若伺服器回傳 3xx 且未自動跟隨重定向，`urlopen` 可能拋出 `HTTPError`，同樣被捕捉。但若伺服器回傳 2xx 以外的狀態碼且未拋出例外（例如某些自訂 handler），則可能回傳 `True`。建議明確檢查 `resp.status` 並處理非 2xx 情況。

evidence：diff 中 `post` 函式依賴 `urlopen` 的例外行為，未明確處理所有非 2xx 狀態。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M080 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤訊息。

**失敗情境**：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

**建議**：移除 `try/except`，讓例外自然傳播；或至少記錄錯誤並重新拋出，例如：
```python
except Exception as e:
    print(f"Failed to fetch {path}: {e}", file=sys.stderr)
    raise
```

evidence：diff 第 24-25 行：`except:` 後直接 `pass`，且函式沒有回傳任何值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M081 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 人工

**`max_items` 未限制上限，可能導致 payload 過大**

existing_code:
```
return int(raw)
```

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未設定上限。若使用者設定極大值（例如 1000000），`commits[: max_items()]` 會將大量 commit 納入訊息，可能超過 webhook 的 payload 限制或造成記憶體壓力。建議設定合理上限（例如 1000）並在超過時警告。

evidence：diff 中 `max_items` 函式直接回傳 `int(raw)`，未檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M082 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

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

## M083 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**`review_latency` 假設 `events` 非空且元素有 `created_at`，可能拋出例外**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，`events` 可能不是串列（例如 API 回傳 `None`），`events[0]` 會拋出 `TypeError`。

建議：檢查 `events` 型別與元素結構，或使用 `events[0].get("created_at")`。

evidence：diff 第 40-41 行：直接索引與鍵存取。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M084 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M085 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `tags` 列表中的第一個元素（例如 repo 只有一個 tag），`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個 tag，而不是拋出錯誤。這會導致 `prev` 指向錯誤的 tag，產生錯誤的 commit 範圍。建議在 `tags.index(tag) == 0` 時顯示錯誤訊息並回傳非零退出碼。

evidence：diff 中這一行直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M086 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M087 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若函式被多次呼叫（例如在同一個程序內處理多個 repo），`seen` 會不斷累積先前呼叫的作者，導致結果錯誤。

**失敗情境**：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

**建議**：改用 `None` 作為預設值，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 29 行：函式定義使用可變預設值 `seen=[]`，且函式內對 `seen` 進行 `append` 修改。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M088 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M089 ｜ 標的 probe ｜ `sandbox/release_notes.py:96` ｜ 人工

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

## M090 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個 tag 時，prev 取得會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是報錯。這可能導致錯誤的 commit 範圍。建議檢查 `tags.index(tag) == 0` 的情況，並給出明確的錯誤訊息。

evidence：diff 中該行直接使用 `tags.index(tag) - 1`，沒有處理 index 為 0 的邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M091 ｜ 標的 python ｜ `sandbox/pr_stats.py:22` ｜ 人工

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

## M092 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次。每次呼叫若未傳入 `seen`，都會共用同一個 list，導致多次呼叫時作者名單不斷累積，且可能包含前一次呼叫的結果。

建議：改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 31 行：參數預設值為 `[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M093 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**變數 ahead 可能未定義或為空，導致 SQL 插入失敗或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。建議在計算後檢查 `ahead` 是否為數字，失敗時設為 0 或中止。

evidence：第 31 行未處理 git 指令失敗時 ahead 為空的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M094 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M095 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M096 ｜ 標的 probe ｜ `sandbox/release_notes.py:96` ｜ 人工

**`post` 函式只捕捉 `URLError`，其他例外可能導致程式崩潰**

existing_code:
```
except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`urllib.request.urlopen` 除了 `URLError` 之外，還可能拋出 `ValueError`（例如 URL 格式錯誤）、`TimeoutError`（在 Python 3.10+ 中 timeout 會拋出 `TimeoutError`，它是 `URLError` 的子類別，但某些情況可能不是）或 `http.client.HTTPException`。目前只捕捉 `URLError`，其他例外會讓程式直接崩潰。建議捕捉更廣泛的例外（例如 `Exception`）或至少加上 `except Exception as e` 並記錄錯誤。

evidence：diff 第 79-81 行，只捕捉 `URLError`，未涵蓋所有可能的例外。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M097 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**tag 清單為空時，prev 會取到最後一個元素而非第一個**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tags` 為空時，`tags.index(tag)` 會拋出 `ValueError`，但若 `tags` 非空且 `tag` 位於第一個位置，`tags.index(tag) - 1` 會是 -1，取到最後一個 tag，而非前一個版本。這會導致 release notes 範圍錯誤。建議先檢查 `tags.index(tag) > 0`，否則回報錯誤。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未處理邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M098 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，每次呼叫都會共用同一個 list。若多次呼叫此函式（例如在同一個程序內處理多個 repo），先前的作者會被保留，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 31 行：`seen=[]` 為可變預設值，且函式內有 `seen.append(...)` 修改該 list。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

# 抽查（自動標記；同意就不用寫，有異議才寫進 blind-labels.csv）

## S001 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**local 關鍵字在函式外使用**

existing_code:
```
local target="$ROOT/$d"
```

body：`main` 函式中使用 `local target="$ROOT/$d"`，但 `local` 僅能在函式內使用。雖然在 bash 中可能不會報錯，但這是不良實踐，可能導致變數作用域混淆。

建議移除 `local` 或將該段程式碼放入函式中。

evidence：diff 第 82 行：在 `main` 函式內使用 `local`，但 `main` 本身是函式，此處 `local` 是多餘的。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## S002 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**collect_authors 使用可變預設值，導致跨呼叫累積作者**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[])` 的預設參數 `seen` 是 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果呼叫者沒有傳入 `seen`，作者會被累積到同一個 list 中，造成結果錯誤。建議改為 `seen=None`，並在函式內初始化為空 list。

evidence：diff 第 28 行：可變預設值 `seen=[]`，且函式內對其進行 `append` 操作。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## S003 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入風險：eval 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`eval "$hook $repo"` 會將 `$hook` 與 `$repo` 的內容當作 shell 指令執行。若 `$ROOT/.hooks/post-sync` 檔案名稱或 `$repo` 包含特殊字元（如 `;`、`$(...)`），可能導致任意命令執行。

建議改用直接執行：`"$hook" "$repo"`，避免 eval。

evidence：第 61 行使用 eval，且參數來自檔案系統路徑與 repo 名稱，可能包含惡意內容。

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S004 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但腳本未檢查其退出狀態。若 fetch 失敗（如網路問題），後續 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

evidence：diff 第 36-38 行，未檢查退出碼。

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S005 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**cleanup_cache 使用 rm -rf 可能誤刪重要檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查 `.cache` 是否為目錄，並避免使用 `*` 萬用字元，或使用更安全的刪除方式。

evidence：diff 第 60 行，使用 rm -rf 與萬用字元。

- 規則提示 SH-S5：$ROOT 未檢查就 rm -rf
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S006 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**`tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中先檢查 `if tag not in tags`，但 `tags` 是 `list_tags` 回傳的 list，而 `list_tags` 只回傳符合 `TAG_RE` 的 tag。若使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為 True，會先印出錯誤並 return 2，不會執行到 `tags.index(tag)`。但若 `list_tags` 因某些原因回傳的 list 不包含該 tag（例如 tag 名稱符合 regex 但實際不存在），則 `tags.index(tag)` 會拋出 `ValueError`，導致程式崩潰。建議使用 `try/except` 或先檢查 `tag in tags` 再取 index。

evidence：diff 中 `main` 函式在 `if tag not in tags` 檢查後直接使用 `tags.index(tag)`，但未處理 `ValueError`。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## S007 ｜ 標的 probe ｜ `sandbox/release_notes.py:39` ｜ 自動：PR-X1 → valid

**max_items 未處理負數或非整數的 NOTES_MAX**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將 `NOTES_MAX` 轉為整數，但未檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，導致最後一個 commit 被排除，且沒有警告。另外，若 `NOTES_MAX` 為空字串，會回傳預設值，但若為 `0` 則會回傳 0，導致 `commits[:0]` 為空，後續 `latest = commits[0][0]` 會拋出 IndexError。

建議：驗證 `NOTES_MAX` 為正整數，否則回傳預設值並記錄警告。

evidence：diff 中 `max_items` 只處理 ValueError，未處理負數或 0 的情況。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## S008 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

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

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S009 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

**使用 ls 解析目錄名稱，特殊字元可能導致錯誤**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 ls 的輸出進行 word splitting，若目錄名稱包含空格、換行或 glob 字元，會導致迴圈變數錯誤。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

evidence：diff 第 68 行：`for d in $(ls "$ROOT"); do`。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## S010 ｜ 標的 python ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**threshold_from_env 的 int(raw) 未處理轉換失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為整數，若使用者設定非數字字串（例如 `abc`），會拋出 `ValueError` 導致程式崩潰。

建議：捕捉 `ValueError` 並提供預設值或明確錯誤訊息。

evidence：diff 第 44 行：`int(raw)` 無例外處理。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## S011 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

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

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## S012 ｜ 標的 python ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 函式依賴可能不存在的鍵**

existing_code:
```
if pr["additions"] > 500:
```

body：`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 回傳的資料可能缺少這些鍵（例如 API 回應格式變更或部分 PR 資料不完整），導致 `KeyError`。

具體失敗情境：GitHub API 回傳的 PR 物件缺少 `additions` 欄位（例如某些事件類型），程式在 `classify` 中拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證資料結構。

evidence：diff 第 54 行，直接存取鍵，未檢查存在性。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## S013 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**在迴圈內使用 local 宣告變數，可能導致非預期行為**

existing_code:
```
local target="$ROOT/$d"
```

body：`local target="$ROOT/$d"` 在 for 迴圈內使用 local，但 local 僅在函數內有效。此處位於 main 函數中，因此有效，但若未來重構可能造成混淆。建議改為一般賦值。

evidence：第 77 行在迴圈內使用 local。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## S014 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:68` ｜ 自動：SH-B2 → invalid

**summarize 中 total 計算可能因 grep 失敗而錯誤**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 若 `grep` 因檔案不存在而失敗，`total` 會被設為 0，但若檔案存在但為空，`grep -c .` 回傳 0 且 exit code 為 1，此時 `total` 會被設為 0，但實際上檔案存在且為空，後續 `if [ "$total" -gt 100 ]` 判斷正確，但 `echo` 顯示的筆數為 0，可能造成誤解。

**建議修法**：使用 `wc -l < "$LOG"` 或先檢查檔案是否存在。

evidence：diff 第 70 行：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0`

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S015 ｜ 標的 python ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

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

- 規則提示 PY-A6：open 沒用 with

## S016 ｜ 標的 python ｜ `sandbox/pr_stats.py:26` ｜ 自動：PY-A1 → valid

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。建議：至少記錄例外並重新拋出，或回傳一個明確的錯誤物件，讓呼叫端能處理。

evidence：diff 第 26 行：`except: pass` 吞掉所有例外，且函式沒有回傳值，導致呼叫端無法區分成功與失敗。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## S017 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入風險：run_hook 使用 eval 執行未受信任的參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函數使用 `eval "$hook $repo"`，其中 `$repo` 來自 repo 目錄名稱（由 `ls` 取得）。若目錄名稱包含 shell 特殊字元（如 `; rm -rf ~`），可能導致任意命令執行。

建議避免使用 eval，改用直接執行並傳遞參數：
```bash
"$hook" "$repo"
```
若 hook 需要 shell 解析，應明確限制輸入或使用其他安全機制。

evidence：diff 第 55 行：`eval "$hook $repo"`

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S018 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：`eval "$hook $repo"` 執行未受信任的 hook 路徑與 repo 名稱**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval` 執行 `$hook $repo`。`$hook` 是固定路徑，但 `$repo` 來自目錄名稱，未經驗證。若 repo 名稱包含 shell 特殊字元（例如 `$(rm -rf ~)`），會被執行。

**失敗情境**：若 `$ROOT` 下有名為 `$(touch /tmp/pwned)` 的目錄，執行此腳本會建立 `/tmp/pwned` 檔案。

**建議**：避免使用 `eval`，改用直接執行：`"$hook" "$repo"`。若 hook 需要 shell 解析，應明確限制 repo 名稱格式（例如只允許 `[A-Za-z0-9._-]+`）。

evidence：diff 第 52 行：`eval "$hook $repo"`

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S019 ｜ 標的 python ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

**`export_csv` 未使用 `with` 管理檔案資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`open(path, "w")` 後手動 `close()`，若寫入過程拋出例外，檔案控制代碼不會被關閉，可能導致資源洩漏。建議改用 `with open(...) as f:` 確保自動關閉。

evidence：diff 第 57-61 行顯示檔案操作未使用 `with` 語句。

- 規則提示 PY-A6：open 沒用 with

## S020 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

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

- 規則提示 SH-S5：$ROOT 未檢查就 rm -rf
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S021 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:68` ｜ 自動：SH-B2 → invalid

**`summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `|| total=0` 處理**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `$LOG` 不存在時，`grep` 回傳非零，`total` 會被設為 0，但 `grep` 的錯誤輸出已被重導向，因此不會顯示錯誤。此處理方式可接受，但建議明確檢查檔案是否存在。

evidence：第 61 行使用 `||` 處理錯誤，但未檢查檔案存在性。

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S022 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 參數，該參數來自命令列輸入（`sys.argv[1]`），完全由使用者控制。攻擊者可注入任意 shell 指令，例如傳入 `repo` 為 `foo; rm -rf /` 或 `$(malicious)`。

**失敗情境**：使用者執行 `python3 pr_stats.py 'repo; touch /tmp/pwned' 1`，`archive` 會執行 `tar czf /tmp/pr-stats-repo; touch /tmp/pwned.tgz ...`，導致任意指令執行。

**建議**：避免使用 `shell=True`，改用參數列表傳遞，並驗證 `repo` 格式。例如：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)
subprocess.run(["gh", "repo", "view", repo], check=True)
```

evidence：diff 第 65 行：`subprocess.run` 使用 `shell=True`，且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## S023 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：eval 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"`，若 `$hook` 或 `$repo` 包含 shell 特殊字元，將導致任意命令執行。例如 repo 名稱為 `; rm -rf ~` 時，會執行刪除指令。建議改用直接執行 `"$hook" "$repo"`，避免 eval。

evidence：第 50 行使用 eval 執行字串，變數未經安全處理。

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S024 ｜ 標的 python ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

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

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## S025 ｜ 標的 python ｜ `sandbox/pr_stats.py:21` ｜ 自動：PY-K-token → valid

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

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## S026 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:70` ｜ 自動：SH-B2 → invalid

**日誌截斷邏輯可能丟失資料**

existing_code:
```
if [ "$total" -gt 100 ]; then
    tail -100 "$LOG" > "$LOG.trimmed"
    mv "$LOG.trimmed" "$LOG"
  fi

  echo "本次同步共 $total 筆紀錄，詳見 $LOG"
```

body：`summarize` 中若日誌行數超過 100，會將日誌截斷為最後 100 行，但 `total` 變數仍記錄原始行數，導致輸出訊息「本次同步共 $total 筆紀錄」與實際日誌內容不符。建議在截斷後更新 total 或調整訊息。

evidence：第 67-71 行截斷日誌但未更新 total。

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S027 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能產生不完整的 release notes**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，程式會繼續執行，可能產生空的或不完整的 commit 清單，最後發布錯誤的公告。建議加上 `check=True` 或明確檢查 `returncode` 並處理錯誤。

evidence：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## S028 ｜ 標的 python ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

**classify 假設 pr 有 additions、changed_files、title 鍵，可能 KeyError**

existing_code:
```
if pr["additions"] > 500:
        return "large"
    elif pr["changed_files"] > 20:
        return "wide"
    elif pr["title"].startswith("fix"):
```

body：`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但若 API 回傳的 PR 物件缺少這些鍵（例如某些事件或權限不足），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證必要欄位。

evidence：diff 第 58-61 行：直接索引字典。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## S029 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**`max_items()` 未處理負數或過大的值**

existing_code:
```
return int(raw)
```

body：`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為負數或過大。如果設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit；如果設定為極大值，可能導致記憶體問題（雖然 commit 數量通常有限）。

建議：限制範圍，例如 `max(0, min(value, 1000))`。

evidence：diff 中 `max_items()` 直接回傳 `int(raw)`，沒有範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）
