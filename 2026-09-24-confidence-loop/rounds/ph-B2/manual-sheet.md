# ph-B2 人工標記單（盲標：不含 confidence、severity）

自動 65 筆、人工 27 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-B2:python:2:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取 `pr["user"]["login"]` 等欄位，若 `_fetch` 回傳 `None` 或非 dict，會拋出 `TypeError` 或 `KeyError`，且沒有上下文可除錯。

具體失敗情境：GitHub API 回傳 404（PR 不存在）或 401（token 無效）時，`urlopen` 會拋出 `HTTPError`，被 `except` 吞掉，`_fetch` 回傳 `None`，接著 `pr["user"]` 就會拋出 `TypeError: 'NoneType' object is not subscriptable`。

建議：至少記錄錯誤並重新拋出，或回傳明確的錯誤物件；並在呼叫端檢查回傳值。

evidence：diff 第 25-26 行：`except:` 後只有 `pass`，且函式沒有回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B2:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次。每次呼叫若未傳入 `seen`，都會共用同一個 list，導致作者名單跨呼叫累積。

具體失敗情境：第一次呼叫 `collect_authors(repo, [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors(repo, [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：改用 `seen=None`，在函式內判斷 `if seen is None: seen = []`。

evidence：diff 第 29 行：參數預設值為 `[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## ph-B2:python:2:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且元素有 created_at，未處理空列表或缺失欄位**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 欄位（例如 API 回應格式變更），`events[0]["created_at"]` 會拋出 `KeyError`。

建議：使用 `events[0].get("created_at")` 並檢查是否為 None。

evidence：diff 第 36-37 行：直接以鍵值存取，未使用 `.get()`。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B2:python:3:1 ｜ `sandbox/pr_stats.py:22` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取，例如 `pr["user"]["login"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`。此外，`urlopen` 在 HTTP 錯誤（如 404）時會拋出 `HTTPError`，也被吞掉。建議：讓 `_fetch` 重新拋出例外，或回傳明確的錯誤值並在呼叫端檢查。

evidence：diff 第 22-23 行：`except: pass`，且 `_fetch` 的回傳值在 `collect_authors` 和 `main` 中被直接當作 dict 使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B2:python:3:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且第一個事件是 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]`，但若第一個事件沒有 `created_at` 欄位（例如某些事件型別），會拋出 `KeyError`。建議檢查事件型別或使用 `get`。

evidence：diff 第 34-35 行：`first = events[0]["created_at"]` 和 `last = events[-1]["created_at"]`

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B2:python:3:8 ｜ `sandbox/pr_stats.py:48` ｜ 候選：無

**_to_epoch 使用 fromisoformat 可能無法解析所有 ISO 格式**

existing_code:
```
return int(datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
```

body：`_to_epoch` 使用 `datetime.datetime.fromisoformat`，但 GitHub API 的時間格式可能包含微秒或時區偏移，某些 Python 版本可能無法解析。建議使用更寬容的解析方式，如 `dateutil.parser`。

evidence：diff 第 40 行：`datetime.datetime.fromisoformat`


## ph-B2:python:4:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致靜默失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使呼叫端無法得知失敗，後續程式碼會因 `pr` 為 `None` 而拋出 `TypeError` 或 `KeyError`。例如：當 GitHub API 回傳 404 或網路中斷時，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]["login"]` 會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或讓呼叫端處理 `None`。

evidence：diff 第 24 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B2:python:4:7 ｜ `sandbox/pr_stats.py:38` ｜ 候選：PY-B1

**review_latency 對空 timeline 回傳 0 可能誤導**

existing_code:
```
if not events:
        return 0
```

body：當 `events` 為空時回傳 0，但 0 可能被解讀為「無延遲」，與實際情況（無資料）混淆。建議回傳 `None` 或拋出例外，讓呼叫端處理。

evidence：diff 第 34-35 行：空列表回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B2:python:5:6 ｜ `sandbox/pr_stats.py:72` ｜ 候選：無

**CSV 欄位未處理逗號或換行，可能破壞格式**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 寫入 CSV，若 `author` 或 `kind` 包含逗號或換行，會破壞 CSV 結構。建議使用 `csv` 模組的 writer。

evidence：diff 第 53 行：手動拼接 CSV 欄位，未做 escaping。

- 規則提示 PY-A6：open 沒用 with

## ph-B2:python:5:7 ｜ `sandbox/pr_stats.py:21` ｜ 候選：PY-A1, PY-K-token

**Authorization header 直接使用環境變數，可能洩漏 token**

existing_code:
```
req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
```

body：`_fetch` 從環境變數讀取 `GITHUB_TOKEN` 並直接放入 header，若請求被記錄或發生例外，token 可能外洩。建議使用更安全的方式管理憑證，例如從 keyring 讀取。

evidence：diff 第 21 行：直接使用環境變數作為敏感 header。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## ph-B2:shell:1:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：無

**變數未加引號可能導致意外展開**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 中，若 `$BRANCH` 包含特殊字元（雖然已驗證格式，但可能包含 `..` 等），可能導致 rev-list 參數解析錯誤。建議對所有變數使用引號，並考慮使用 `--` 分隔選項與參數。

evidence：diff 第 39 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B2:shell:1:6 ｜ `sandbox/repo_sync.sh:43` ｜ 候選：SH-S3(unless)

**ahead 可能為空導致數值比較錯誤**

existing_code:
```
if [ "$ahead" -gt 0 ]; then
```

body：若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 可能為空字串，後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而中止腳本。建議先檢查 `ahead` 是否為數字，或設定預設值 0。

evidence：diff 第 41 行：`if [ "$ahead" -gt 0 ]; then`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B2:shell:2:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄列表，可能受特殊檔名影響**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空格或換行符號，會導致迴圈變數 `d` 被錯誤分割。建議改用 `for d in "$ROOT"/*/; do` 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

evidence：diff 第 68 行新增的迴圈。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-B2:shell:3:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**使用 ls 解析目錄列表，可能受特殊檔名影響**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 使用 `ls` 的輸出進行迴圈，若目錄名稱包含空白、換行或 glob 字元，將導致錯誤分割。此外，若 `$ROOT` 不存在，`ls` 會輸出錯誤至 stderr，但迴圈仍可能執行。

建議改用 `for d in "$ROOT"/*/; do` 或 `find` 搭配 `-print0`。

evidence：diff 第 73 行。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## ph-B2:shell:4:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入：repo 名稱與 branch 未跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：在 `sync_one` 函式中，`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 與 `$BRANCH` 插入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），將破壞 SQL 語法或造成注入。雖然 branch 有正規表示式驗證，但 repo 名稱（來自 `basename "$dir"`）完全未驗證。攻擊者可建立惡意名稱的 repo 目錄，導致任意 SQL 執行。

建議使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數進行單引號跳脫（`${name//\'/\'\'}`）。

evidence：diff 第 42 行新增此 SQL 語句，變數直接拼接。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B2:shell:4:4 ｜ `sandbox/repo_sync.sh:33` ｜ 候選：SH-S4, SH-K-gitfail

**cd 失敗未中止，可能操作錯誤目錄**

existing_code:
```
cd "$dir"
```

body：`sync_one` 函式開頭 `cd "$dir"` 未檢查是否成功。若 `$dir` 不存在或無法進入，後續 git 指令將在錯誤的目錄執行（可能是上一個 repo 的目錄或腳本啟動目錄），造成不可預期的結果。

建議改為 `cd "$dir" || return 1` 或 `cd "$dir" || exit 1`。

evidence：diff 第 30 行，無錯誤檢查。

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-B2:shell:5:2 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 中，`$name` 和 `$BRANCH` 直接拼接進 SQL 字串。雖然 `$BRANCH` 有正規表示式驗證，但 `$name` 完全未驗證。如果 repo 目錄名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法或注入惡意 SQL。

**失敗情境**：建立一個名為 `x'); DROP TABLE runs;--` 的 repo 目錄，執行腳本後 runs 表會被刪除。

**建議**：使用參數化查詢（sqlite3 支援 `?` 佔位符）或對所有插入值進行跳脫（例如將 `'` 替換為 `''`）。

evidence：diff 第 43 行：直接將 `$name` 和 `$BRANCH` 插入 SQL 字串，未使用參數化或跳脫。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B2:shell:5:5 ｜ `sandbox/repo_sync.sh:37` ｜ 候選：SH-K-gitfail, SH-B1(unless)

**git checkout 未加引號，branch 名稱可能被 shell 展開**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 中 `$BRANCH` 未加引號。雖然前面有正規表示式驗證，但若 branch 名稱包含 glob 字元（例如 `*`）或空格（雖然正規表示式不允許空格），仍可能被 shell 展開或分割。

**失敗情境**：若 branch 名稱包含 `*`（例如 `feature/*`），shell 會嘗試展開為符合的檔案名稱，可能導致 checkout 錯誤的分支。

**建議**：將 `$BRANCH` 加上雙引號：`git checkout "$BRANCH"`。

evidence：diff 第 34 行：`$BRANCH` 未加引號。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## ph-B2:probe:1:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**只有一個 tag 時 `tags.index(tag) - 1` 會取到最後一個 tag**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]`。若 `tags` 只有一個元素（即目前 tag 是第一個 tag），`tags.index(tag)` 為 0，`-1` 會變成 -1，Python 會取到最後一個元素（也就是自己），導致 `prev == tag`，`git log prev..tag` 會是空範圍，`commits` 為空，進而觸發 `IndexError`。建議在 `tags.index(tag) == 0` 時處理（例如回報錯誤或使用 repo 初始 commit）。

evidence：diff 中 `prev = tags[tags.index(tag) - 1]` 未處理 `index` 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B2:probe:1:3 ｜ `sandbox/release_notes.py:31` ｜ 候選：無

**NOTES_MAX 為負數或非整數時行為不一致**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 對 `NOTES_MAX` 的處理：若為空字串回傳預設值；若無法轉為整數則記錄警告並回傳預設值；但若轉為負數（例如 `-1`），會直接回傳負數。在 `main` 中 `commits[: max_items()]` 若 `max_items()` 為負數，切片會取到倒數幾個元素，可能不是預期行為。建議對負數也回傳預設值或設定下限。

evidence：diff 中 `max_items` 未處理負數輸入。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-B2:probe:1:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能造成 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查 scheme 是否為 http/https。若攻擊者能控制環境變數（例如 CI 設定），可指定 `file://` 或 `gopher://` 等 scheme，導致任意檔案讀取或內網請求。建議限制 scheme 為 `http` 或 `https`。

evidence：diff 中 `post` 未對 `url` 做 scheme 驗證。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B2:probe:1:5 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

**設定檔 JSON 型別未驗證**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 回傳 `json.load` 的結果，但未驗證其型別是否為 dict。若 `.release-notes.json` 內容為 list 或字串，後續 `cfg.get('title', ...)` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，否則回傳空 dict 或拋出明確錯誤。

evidence：diff 中 `load_config` 直接回傳 `json.load` 結果，未做型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## ph-B2:probe:2:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**第一個 tag 時 `prev` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 之前一定還有其他 tag。如果使用者指定的 `tag` 是 repo 中第一個符合 `v*` 的 tag（例如 `v0.1.0`），`tags.index(tag)` 會是 0，`tags[-1]` 會取到最後一個 tag，而不是正確的前一個版本，導致 release notes 範圍錯誤。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個版本。

evidence：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1` 作為索引，未處理索引為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B2:probe:3:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能造成 SSRF 或誤用**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查是否為 http/https。若誤設為 `file://` 或其他 scheme，可能讀取本機檔案或造成非預期行為。建議驗證 URL scheme 為 http 或 https。

evidence：diff 中 `post` 函式直接將 `url` 傳給 `urllib.request.Request`，無任何 scheme 檢查。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B2:probe:4:3 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

**post 函式未檢查 HTTP 狀態碼**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
```

body：`post` 函式在 `urlopen` 成功後僅回傳 `200 <= resp.status < 300`，但未處理其他狀態碼（如 4xx、5xx）。若 webhook 回傳 404 或 500，函式會回傳 `False`，但呼叫端 `main` 會回傳 1，導致程式被視為失敗。建議明確處理非 2xx 狀態碼，記錄錯誤並回傳 `False`。

evidence：diff 中 `post` 函式僅回傳布林值，未區分不同錯誤。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## ph-B2:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**只有一個符合條件的 tag 時，`prev` 會取到最後一個 tag 而非前一個**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳所有符合 `TAG_RE` 的 tag，若 repo 中只有一個符合條件的 tag（例如只有 `v1.0.0`），則 `tags.index(tag)` 為 0，`prev = tags[-1]` 會是 `v1.0.0` 本身，導致 `prev..tag` 範圍為空，`commits_between` 回傳空 list，最後輸出「沒有新 commit」。建議在 `tags.index(tag) == 0` 時處理（例如從 repo 初始 commit 開始，或提示使用者）。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未處理 index 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B2:probe:5:3 ｜ `sandbox/release_notes.py:35` ｜ 候選：PR-X1, PR-B3(unless)

**`NOTES_MAX` 為負數時會導致 `commits[:max_items()]` 切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了非整數的情況，若 `NOTES_MAX` 設為負數（例如 `-1`），`int(raw)` 會成功，回傳負數。之後 `commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit。建議在 `max_items` 中檢查數值是否為正整數，否則回傳預設值。

evidence：diff 中 `max_items` 函式只捕捉 `ValueError`，未檢查轉換後的數值是否為正。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-B2:python:2:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串中拼接了 `path` 和 `repo`。這兩個參數來自命令列參數（`repo`）或由 `repo` 衍生（`path`），攻擊者可注入額外 shell 命令。

具體攻擊情境：執行 `python pr_stats.py '$(rm -rf /)' 1` 時，`repo` 的值會被 shell 展開，導致任意命令執行。

建議：改用 `subprocess.run` 的 list 形式，避免 `shell=True`；或使用 `shlex.quote` 對參數進行轉義。

evidence：diff 第 73 行：`shell=True` 且 f-string 包含外部輸入。

## ph-B2:python:3:6 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

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

body：`classify` 假設 `pr` 一定有 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限或版本不同而缺少這些欄位，導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

evidence：diff 第 55-60 行：直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`。

## ph-B2:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**可變預設值 seen=[] 跨呼叫共用**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen=[]` 是可變預設值，每次呼叫都會累積到同一個 list，導致結果包含前一次呼叫的作者。例如第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`。建議改用 `seen=None` 並在函式內初始化。

evidence：diff 第 28 行：函式定義使用可變預設值 `seen=[]`。

## ph-B2:shell:2:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：在 `sync_one` 中，`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 和 `$BRANCH` 嵌入 SQL 字串。雖然 `$BRANCH` 已用正規表達式限制字元集，但 `$name` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"` 的輸出，攻擊者若能在 repo 根目錄建立名稱包含單引號的目錄（例如 `'; DROP TABLE runs; --`），即可注入任意 SQL 語句，造成資料毀損或洩漏。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 和 `$BRANCH` 進行單引號跳脫。

evidence：diff 第 42 行新增的 SQL 插入語句，直接使用變數拼接。

## ph-B2:shell:3:4 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中所有 git 指令的 stderr 僅重導向至 log，未檢查退出碼。若 `git fetch` 或 `git checkout` 失敗（例如網路問題、branch 不存在），腳本仍會繼續執行後續指令，可能導致錯誤的 ahead 計算或資料庫寫入不正確的資料。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：diff 第 35-37 行。

## ph-B2:shell:4:8 ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**local 關鍵字在函式外使用，可能導致非預期行為**

existing_code:
```
local target="$ROOT/$d"
```

body：在 `main` 函式中，`local target="$ROOT/$d"` 使用了 `local`，但 `local` 只能在函式內使用。雖然在 bash 中函式外的 `local` 會被忽略，但可能造成混淆。建議移除 `local` 或改為一般變數賦值。

evidence：diff 第 74 行，local 使用於函式外。

## ph-B2:probe:2:3 ｜ `sandbox/release_notes.py:32` ｜ 自動：PR-B2 → invalid

**`load_config` 可能因權限問題拋出未處理的例外**

existing_code:
```
except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但 `open` 可能因為權限不足或其他 I/O 錯誤拋出 `PermissionError` 或 `OSError`，導致程式直接崩潰。建議捕捉更廣泛的 `OSError` 並記錄警告，或讓呼叫端處理。

evidence：diff 中 `load_config` 函式的例外處理僅涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`，未涵蓋其他可能的 `OSError`。

## ph-B2:probe:5:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能產生空公告**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損壞、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，導致後續產生空公告並貼到 webhook。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外。

evidence：diff 中 `commits_between` 函式呼叫 `subprocess.run` 沒有 `check=True`，且未檢查 `proc.returncode`。
