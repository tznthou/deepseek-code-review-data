# 盲標單（不含 confidence、severity、輪次）

人工 110 筆、抽查 29 筆。結果寫進 blind-labels.csv（code,item,label,reason）。
label 只能是 valid／invalid／disputed；item 寫 expected-rules 的 id，對不到就寫 NONE。

# 需要人工判定

## M001 ｜ 標的 probe ｜ `sandbox/release_notes.py:42` ｜ 人工

**NOTES_MAX 未驗證範圍，負數或零會造成非預期行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會得到空清單或意外的切片結果（例如 `commits[:-1]` 會排除最後一個 commit）。這可能導致 release notes 內容不完整或完全空白。

**失敗情境**：CI 或部署環境誤設 `NOTES_MAX=0`，程式會貼出只有標題、沒有任何 commit 的公告。

**建議**：在轉換後檢查 `value <= 0`，若小於等於 0 則記錄警告並使用預設值，或直接回傳錯誤。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有對轉換成功的值做範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M002 ｜ 標的 probe ｜ `sandbox/release_notes.py:34` ｜ 人工

**NOTES_MAX 為負數或零時切片行為異常**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 只處理了非整數的情況，沒有檢查負數或零。如果使用者設定 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個 commit 以外的所有 commit；如果設定 `NOTES_MAX=0`，會回傳空 list，導致公告沒有內容。

建議：在 `max_items` 中檢查 `value <= 0` 時回傳預設值或記錄警告。

evidence：diff 中 `max_items` 函式只處理了 `ValueError`，沒有處理負數或零。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M003 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**`_fetch` 吞掉所有例外且不回報，導致後續程式碼在資料缺失時直接崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except:` 區塊只有 `pass`，沒有記錄或重新拋出。當網路錯誤、API 回傳非 200、JSON 解析失敗或 `GITHUB_TOKEN` 未設定時，函式會回傳 `None`。呼叫端（`collect_authors`、`main`）直接對回傳值做 `pr["user"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且錯誤訊息不明確。

**失敗情境**：
- 未設定 `GITHUB_TOKEN` 環境變數時，`os.environ["GITHUB_TOKEN"]` 會拋出 `KeyError`，但被 `except` 捕捉後回傳 `None`，後續 `pr["user"]` 拋出 `TypeError`。
- API 回傳 404（PR 不存在）時，`urlopen` 拋出 `HTTPError`，同樣被吞掉，後續程式碼崩潰。

**建議**：
- 至少記錄例外（`logging.exception`）並重新拋出，或讓函式回傳明確的錯誤結果。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 使用 `raise ... from err` 保留原始追蹤資訊。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有其他回傳值，呼叫端直接使用回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M004 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

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

## M005 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M006 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳的 `tags` 清單可能為空（例如 repo 中沒有任何 `v*` tag）。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 這一行，如果 `tag` 不在 `tags` 中，`tags.index(tag)` 會拋出 `ValueError`，但這個例外沒有被捕捉，程式會直接崩潰。雖然 `main` 前面有檢查 `if tag not in tags`，但這個檢查是在 `list_tags` 之後，如果 `list_tags` 回傳空清單，`tag not in tags` 為真，會先記錄錯誤並回傳 2，所以實際上不會執行到 `tags.index`。然而，如果 `list_tags` 因為某種原因回傳了不包含 `tag` 的非空清單（例如 tag 格式不符），`tag not in tags` 也會攔截。因此這個問題只有在 `list_tags` 拋出例外時才會發生，但 `list_tags` 本身沒有處理 `subprocess.run` 的錯誤（見另一個 finding）。

**建議**：在 `main` 中對 `tags.index` 的呼叫加上例外處理，或改用更安全的方式取得前一個 tag。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag)`，沒有處理 `ValueError`。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M007 ｜ 標的 python ｜ `sandbox/pr_stats.py:72` ｜ 人工

**main 中重複呼叫 _fetch，且未檢查回傳值**

existing_code:
```
pr = _fetch(f"/repos/{repo}/pulls/{n}")
```

body：`main` 在迴圈中對每個 PR 呼叫 `_fetch`，但 `_fetch` 可能回傳 `None`（因為錯誤被吞掉），導致後續 `pr["user"]` 拋出 `TypeError`。此外，`collect_authors` 已經呼叫過 `_fetch`，這裡又重複呼叫，造成不必要的 API 請求。

失敗情境：若某個 PR 的 API 請求失敗，`_fetch` 回傳 `None`，`pr["user"]` 拋出 `TypeError`，程式崩潰。

建議：在 `_fetch` 中讓錯誤向上傳播，或在 `main` 中檢查回傳值。另外，可以考慮重用 `collect_authors` 的結果，避免重複請求。

evidence：diff 第 72 行：直接使用 `_fetch` 的回傳值，未檢查是否為 `None`。

- 規則提示 PY-A6：open 沒用 with

## M008 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M009 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:33` ｜ 人工

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

## M010 ｜ 標的 probe ｜ `sandbox/release_notes.py:104` ｜ 人工

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

body：`load_config` 只處理 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案權限不足或讀取時發生其他 I/O 錯誤，程式會崩潰。建議捕捉 `OSError` 或更廣泛的例外並記錄。

evidence：diff 中 `load_config` 的例外處理僅限於 `FileNotFoundError` 和 `json.JSONDecodeError`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑

## M011 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

**使用 `ls` 解析目錄列表，可能因檔名包含換行或空格而失敗**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若 repo 目錄名稱包含空格或換行，會導致迴圈變數錯誤。

建議使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 來處理。

evidence：第 73 行使用 ls 的輸出進行迴圈。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## M012 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**tag 清單可能為空導致 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中 `prev = tags[tags.index(tag) - 1]` 假設 `tags` 至少有一個元素。若 `list_tags` 回傳空清單（例如 repo 中沒有符合的 tag），`tags.index(tag)` 會拋出 `ValueError`，但若 `tag` 存在於空清單中不可能，因此實際上會先觸發 `ValueError`。但若 `tags` 只有一個元素且 `tag` 是第一個，`tags.index(tag) - 1` 會是 -1，導致 `prev` 為最後一個元素，可能不是預期的前一個 tag。建議檢查 `tags.index(tag) > 0`。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未檢查索引是否大於 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M013 ｜ 標的 python ｜ `sandbox/pr_stats.py:51` ｜ 人工

**threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出未處理的例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
    raw = os.environ.get("PR_STALE_DAYS", "")
    if raw:
        return {"days": int(raw)}
```

body：`threshold_from_env` 的參數 `default={"days": 7}` 是可變預設值，雖然函式內沒有修改 `default`，但若未來修改就可能引入 bug。更嚴重的問題是 `int(raw)` 沒有處理轉換失敗：如果環境變數 `PR_STALE_DAYS` 不是整數（例如設為 `abc`），會拋出 `ValueError` 且沒有被捕捉，導致程式崩潰。

具體情境：
- 使用者設定 `PR_STALE_DAYS=abc`，程式在 `int(raw)` 處拋出 `ValueError`。

建議：
- 將預設值改為 `None` 並在函式內處理。
- 對 `int(raw)` 加上 try/except，或使用更安全的轉換方式。

evidence：diff 第 44-47 行，`default` 是可變 dict，且 `int(raw)` 未處理例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## M014 ｜ 標的 python ｜ `sandbox/pr_stats.py:97` ｜ 人工

**輸出檔案路徑可能包含特殊字元，導致命令注入或路徑問題**

existing_code:
```
out = f"/tmp/pr-stats-{repo.replace('/', '-')}.csv"
```

body：`out` 的檔名由 `repo` 替換 `/` 為 `-` 而來，但 `repo` 可能包含其他特殊字元（如 `;`、`&`、空格），在 `archive` 的 shell 指令中可能造成問題。

失敗情境：`repo` 為 `a; rm -rf /`，`out` 變成 `/tmp/pr-stats-a; rm -rf /.csv`，在 `archive` 的 shell 指令中可能被解釋為多個命令。

建議：對 `repo` 進行更嚴格的驗證或轉義，或避免在 shell 指令中使用未清理的輸入。

evidence：diff 第 78 行：`repo` 未經過完整清理，僅替換 `/`。

- 規則提示 PY-A7b：out 由 repo 組成、replace 只換 /，再進 archive 的 shell=True
- 規則提示 PY-K-tmp：固定、可預測的 /tmp 檔名

## M015 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

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

## M016 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M017 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值是一個 list，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若呼叫多次，作者會被重複加入，且無法清空。

建議：
- 改為 `seen=None`，在函式內 `if seen is None: seen = []`。

evidence：diff 第 28 行：可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M018 ｜ 標的 probe ｜ `sandbox/release_notes.py:125` ｜ 人工

**`commits[0]` 在 commits 為空時會拋出 IndexError**

existing_code:
```
latest = commits[0][0]
```

body：雖然前面有 `if not commits: return 0`，但 `commits_between` 可能因為 git 指令失敗而回傳空 list（見另一個 finding），此時 `commits[0]` 會拋出 IndexError。建議在取得 `latest` 前再次確認 commits 非空，或讓 `commits_between` 在失敗時拋出例外。

evidence：diff 中 main 函式直接取 commits[0]，但 commits 可能因 git 失敗而為空。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）
- 規則提示 PR-X5：設定檔是合法 JSON 但不是物件時 AttributeError；設定檔由操作者自己維護

## M019 ｜ 標的 python ｜ `sandbox/pr_stats.py:21` ｜ 人工

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

## M020 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**`review_latency` 依賴不存在的 `timeline` 欄位，可能永遠回傳 0**

existing_code:
```
events = pr.get("timeline", [])
```

body：`events = pr.get("timeline", [])` 嘗試從 PR 物件取得 `timeline` 欄位，但 GitHub API 的 PR 物件通常不包含 `timeline`（需要另外請求 timeline API）。因此 `events` 幾乎總是空列表，函式回傳 0，導致延遲指標失效。

**失敗情境**：
- 對任何 PR 呼叫 `review_latency`，都會得到 0，即使實際上有 review 活動。

**建議**：
- 確認 API 回應是否包含 `timeline`，若無，需另外呼叫 timeline API 或改用其他欄位（如 `created_at` 與 `updated_at`）。
- 若 `timeline` 不存在，應拋出錯誤或記錄警告，而不是靜默回傳 0。

evidence：diff 第 34 行：使用 `pr.get("timeline", [])`，但 GitHub PR 物件通常無此欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M021 ｜ 標的 python ｜ `sandbox/pr_stats.py:48` ｜ 人工

**_to_epoch 使用 fromisoformat 可能無法解析 GitHub 的時間格式**

existing_code:
```
return int(datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
```

body：`_to_epoch` 使用 `datetime.datetime.fromisoformat` 解析時間字串，但 GitHub API 回傳的時間格式為 ISO 8601，例如 `2023-01-01T12:00:00Z`，Python 3.10 及以下版本的 `fromisoformat` 不支援 `Z` 後綴，會拋出 `ValueError`。

失敗情境：在 Python 3.9 環境中執行，遇到 `Z` 結尾的時間字串會崩潰。

建議：使用 `datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")` 或先替換 `Z` 為 `+00:00`（目前程式碼有做 `replace`，但 `fromisoformat` 在舊版仍可能不支援）。

evidence：diff 第 39 行：依賴 `fromisoformat` 的行為，但未考慮版本相容性。


## M022 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 依賴不存在的 timeline 欄位，永遠回傳 0**

existing_code:
```
events = pr.get("timeline", [])
```

body：`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中沒有 `timeline` 欄位（需另外請求 `/issues/{n}/timeline` 或使用 `events_url`）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。

建議：
- 使用正確的 API 端點取得事件，或改用 `created_at` 和 `updated_at` 計算。

evidence：diff 第 35 行：`pr.get("timeline", [])`，但 `_fetch` 只呼叫 `/pulls/{n}`，回應中無 `timeline`。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M023 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**_fetch 吞掉所有例外，呼叫端無法得知失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors`、`main`）會直接對回傳值做 `pr["user"]` 或 `pr["additions"]`，導致 `TypeError: 'NoneType' object is not subscriptable` 或 `KeyError`。此外，裸 `except:` 也會攔截 `KeyboardInterrupt` 和 `SystemExit`。

建議：
- 至少記錄錯誤並重新拋出，或回傳明確的錯誤值。
- 使用 `except Exception as e:` 並 `raise` 或 `return None`，讓呼叫端處理。
- 考慮使用 `urllib.error.HTTPError` 處理非 200 狀態碼。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M024 ｜ 標的 python ｜ `sandbox/pr_stats.py:27` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當成 dict 來存取鍵（例如 `pr["user"]["login"]`），當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，造成程式崩潰。

具體失敗情境：
- GitHub API 回傳 404（PR 不存在）或 401（token 無效）時，`urlopen` 會拋出 `HTTPError`，被 `except` 吞掉，`_fetch` 回傳 `None`，接著 `pr["user"]` 就會拋出 `TypeError: 'NoneType' object is not subscriptable`。
- 網路逾時或 DNS 失敗時，同樣會回傳 `None` 並導致後續崩潰。

建議：
- 讓 `_fetch` 在失敗時拋出例外（或回傳明確的錯誤值），並在呼叫端處理。
- 至少記錄錯誤訊息，不要完全靜默。

evidence：diff 第 27 行 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 31 行）和 `main`（第 73 行）被直接當成 dict 使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M025 ｜ 標的 python ｜ `sandbox/pr_stats.py:42` ｜ 人工

**threshold_from_env 對無效環境變數拋出未處理的 ValueError**

existing_code:
```
if raw:
        return {"days": int(raw)}
```

body：threshold_from_env 將環境變數 PR_STALE_DAYS 轉為整數，若值不是有效整數（如 'abc'），int() 會拋出 ValueError，導致程式崩潰。建議捕捉例外並回退到預設值或提供明確錯誤訊息。

evidence：diff 第 42-43 行

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M026 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**只有一個符合條件的 tag 時，`prev` 會取到最後一個 tag 而非前一個**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳所有符合 `TAG_RE` 的 tag，若 repo 中只有一個符合條件的 tag（例如只有 `v1.0.0`），則 `tags.index(tag)` 為 0，`prev = tags[-1]` 會是 `v1.0.0` 本身，導致 `prev..tag` 範圍為空，`commits_between` 回傳空 list，最後輸出「沒有新 commit」。建議在 `tags.index(tag) == 0` 時處理（例如從 repo 初始 commit 開始，或提示使用者）。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未處理 index 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M027 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**可變預設值 `seen=[]` 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。在 Python 中，預設值只會在函式定義時建立一次，之後每次呼叫若未提供 `seen` 參數，都會共用同一個 list。這會導致多次呼叫 `collect_authors` 時，作者名單會不斷累積，而不是每次重新開始。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 30 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M028 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**可變預設值 seen=[] 導致跨呼叫污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。若呼叫者未傳入 `seen`，則每次呼叫都會共用同一個 list，導致結果累積。例如連續呼叫 `collect_authors(repo, [1])` 和 `collect_authors(repo, [2])`，第二次呼叫會回傳 `[author1, author2]` 而非 `[author2]`。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：參數 `seen=[]` 為可變預設值，且函式內對其進行 `append` 操作（第 30 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M029 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 人工

**NOTES_MAX 未設上限，可能造成資源耗盡**

existing_code:
```
try:
        return int(raw)
    except ValueError:
```

body：`max_items` 直接將環境變數 `NOTES_MAX` 轉成整數，沒有上限。如果使用者設定一個極大的值（例如 10^9），`commits[: max_items()]` 會嘗試建立一個巨大的列表，可能耗盡記憶體。此外，webhook payload 也可能過大而被拒絕。

建議：設定一個合理的上限（例如 1000），或至少檢查是否為正整數。

evidence：diff 中 `return int(raw)` 沒有範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M030 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M031 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 與 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 會拋出 `TypeError`，且錯誤訊息不明確。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 若允許回傳 `None`，呼叫端需檢查並處理。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 30 行）與 `main`（第 69 行）被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M032 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

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

## M033 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**`ahead` 變數可能為空，導致 `[ "$ahead" -gt 0 ]` 比較失敗**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 `[ "$ahead" -gt 0 ]` 會因為空字串不是整數而報錯，且 `sqlite3` 插入時 `$ahead` 為空可能導致 SQL 錯誤。

建議在取得 `ahead` 後檢查是否為數字，若不是則設為 0 或中止。

evidence：diff 第 35 行：`ahead` 可能為空，未做防護。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M034 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 假設 events 存在且非空，但 PR 物件可能沒有 timeline 鍵**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 鍵，因此 `events` 會是空 list，函式回傳 0。這可能不是預期行為。建議確認 API 回應結構或改用其他方式取得時間資料。

evidence：diff 第 34 行：`events = pr.get("timeline", [])`，但 GitHub PR API 回應中沒有 `timeline` 欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M035 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**第一個 tag 時 `prev` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 之前一定還有其他 tag。如果使用者指定的 `tag` 是 repo 中第一個符合 `v*` 的 tag（例如 `v0.1.0`），`tags.index(tag)` 會是 0，`tags[-1]` 會取到最後一個 tag，而不是正確的前一個版本，導致 release notes 範圍錯誤。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個版本。

evidence：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1` 作為索引，未處理索引為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M036 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**`ahead` 可能為空字串，導致 SQL 語法錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。後續的 SQL 插入會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 錯誤。

建議在計算後檢查 `ahead` 是否為空，並設定預設值（如 0）或中止。

evidence：第 38 行未處理命令失敗時變數為空的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M037 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M038 ｜ 標的 probe ｜ `sandbox/release_notes.py:35` ｜ 人工

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

## M039 ｜ 標的 python ｜ `sandbox/pr_stats.py:38` ｜ 人工

**review_latency 對空 timeline 回傳 0，可能誤導為無延遲**

existing_code:
```
if not events:
        return 0
```

body：`review_latency` 在 `events` 為空時回傳 `0`，但這可能表示資料缺失或 PR 尚未有任何事件，而非真正的零延遲。呼叫端（`main`）將此值寫入 CSV，可能造成錯誤的統計。

建議：
- 回傳 `None` 或拋出例外，讓呼叫端處理。
- 或記錄警告並回傳一個明確的無效值（如 -1）。

evidence：diff 第 34-35 行：空 `events` 時回傳 `0`，但 `0` 是有效的延遲值，無法區分。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M040 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M041 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**`list_tags` 回傳空列表時，`tags.index(tag) - 1` 會取到最後一個元素**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]`。如果 `tags` 是空列表（例如 repo 沒有任何符合 `v*` 的 tag），`tags.index(tag)` 會拋出 `ValueError`，但更隱晦的是如果 `tags` 非空但 `tag` 不在其中，`tags.index(tag)` 也會拋出 `ValueError`，這部分已有檢查。然而，如果 `tags` 只有一個元素且就是 `tag`，`tags.index(tag) - 1` 會是 `-1`，取到最後一個元素（即 `tag` 本身），導致 `prev` 等於 `tag`，`git log prev..tag` 會是空範圍。建議在取 `prev` 前檢查 `tags.index(tag) > 0`，否則回報錯誤。

evidence：diff 第 48 行：`prev = tags[tags.index(tag) - 1]`，未處理 `tags` 只有一個元素或 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M042 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M043 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 且通過 `TAG_RE` 的 tag）。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 會先執行 `tags.index(tag)`，若 `tag` 不在列表中會拋出 `ValueError`，但若列表為空且 `tag` 不在其中，`tags.index(tag)` 同樣拋出 `ValueError`，這部分已有處理。然而，若 `tag` 是列表中的第一個元素，`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個元素，這可能不是預期的「前一個 tag」。建議在 `main` 中檢查 `tags.index(tag) == 0` 的情況，並明確處理沒有前一個 tag 的狀況。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M044 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 人工

**archive 函式未檢查 subprocess.run 的回傳值**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run` 預設不會在子程序失敗時拋出例外，而是回傳一個 `CompletedProcess` 物件，其中 `returncode` 屬性表示退出碼。這裡沒有檢查 `returncode`，所以即使 `tar` 或 `gh` 指令失敗，程式也會繼續執行並回報成功。

具體情境：
- 如果 `tar` 因為路徑不存在而失敗，程式不會察覺，後續的 `print` 仍會顯示成功訊息。

建議：
- 檢查 `returncode`，或使用 `subprocess.run(..., check=True)` 在失敗時拋出例外。

evidence：diff 第 61 行，未檢查 `subprocess.run` 的回傳值。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## M045 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

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

## M046 ｜ 標的 probe ｜ `sandbox/release_notes.py:94` ｜ 人工

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

## M047 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**`collect_authors` 使用可變預設值參數，跨呼叫會累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值是空列表，但 Python 的預設參數在函式定義時只建立一次，之後每次呼叫都會共用同一個列表物件。若呼叫者未傳入 `seen`，多次呼叫會累積先前呼叫的結果，導致資料污染。

**失敗情境**：
- 第一次呼叫 `collect_authors("repo", [1])` 回傳 `["alice"]`。
- 第二次呼叫 `collect_authors("repo", [2])` 會回傳 `["alice", "bob"]`，而不是 `["bob"]`。

**建議**：
- 使用 `None` 作為預設值，並在函式內初始化：`def collect_authors(repo, numbers, seen=None):`，然後 `if seen is None: seen = []`。

evidence：diff 第 28 行：函式定義使用可變預設值 `[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M048 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M049 ｜ 標的 python ｜ `sandbox/pr_stats.py:38` ｜ 人工

**review_latency 對空 timeline 回傳 0 可能誤導**

existing_code:
```
if not events:
        return 0
```

body：當 `events` 為空時回傳 0，但 0 可能被解讀為「無延遲」，與實際情況（無資料）混淆。建議回傳 `None` 或拋出例外，讓呼叫端處理。

evidence：diff 第 34-35 行：空列表回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M050 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**tag 清單為空時 `tags.index(tag)` 會拋出未處理的 `ValueError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中先檢查 `if tag not in tags`，但若 `tags` 是空 list（例如 repo 沒有任何符合 `v*` 的 tag），`tag not in tags` 為 True，會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，若 `tags` 非空但 `tag` 不在其中，同樣會回傳 2。因此 `tags.index(tag)` 只有在 `tag` 存在於 `tags` 時才會執行，此時 `tags` 必非空，所以不會拋出 `ValueError`。

**但**：`list_tags` 可能因為 `git tag` 執行失敗而回傳空 list（例如 repo 路徑錯誤），此時 `tag not in tags` 為 True，程式會印出「找不到 tag」並回傳 2，不會崩潰。因此這個問題實際上不會觸發。

**重新評估**：此 finding 的 confidence 應降低，因為 `tag not in tags` 的檢查已經涵蓋了空 list 的情況。除非 `tags` 在檢查後被修改（但此處沒有），否則 `tags.index(tag)` 是安全的。

**建議**：無需修改，但可考慮將 `tags.index(tag)` 改為更明確的處理，例如使用 `try/except` 或先取得 index 再檢查，以增加可讀性。

evidence：diff 中 `main` 函式在 `if tag not in tags` 之後才執行 `tags.index(tag)`，但該檢查已確保 `tag` 存在於 `tags`，因此 `tags` 非空。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M051 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個版本時，prev 會取到最後一個 tag**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`0 - 1` 等於 -1，Python 會取到最後一個元素。這會導致 release notes 涵蓋從最後一個 tag 到第一個 tag 的所有 commit，而不是空範圍。建議在 `tags.index(tag) == 0` 時處理為沒有前一個 tag 的情況（例如回傳空列表或提示錯誤）。

evidence：diff 中 `main` 函式內 `prev = tags[tags.index(tag) - 1]`，沒有檢查 `tags.index(tag)` 是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M052 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

**SQL 寫入未處理 ahead 為非數字的情況**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：即使 ahead 為空或非數字，SQL 插入仍會執行，可能導致資料庫寫入失敗或寫入錯誤資料。建議在寫入前驗證 ahead 為整數。

evidence：第 42 行未對 ahead 進行型別檢查。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M053 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 計算可能失敗，導致變數為空或非數字**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空可能導致型別錯誤。建議檢查指令是否成功，失敗時設定預設值或中止。

evidence：第 38 行未檢查 rev-list 的 exit code。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M054 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M055 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M056 ｜ 標的 probe ｜ `sandbox/release_notes.py:34` ｜ 人工

**load_config 未處理 JSON 以外的檔案讀取錯誤**

existing_code:
```
except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")
```

body：`load_config` 只捕捉 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案存在但無法讀取（例如權限不足、I/O 錯誤），會拋出未處理的 `OSError` 導致程式崩潰。建議捕捉 `OSError` 並記錄警告後回傳空 dict，或讓錯誤向上傳播並在 main 中處理。

evidence：diff 中 `load_config` 的 except 子句僅涵蓋 `FileNotFoundError` 和 `json.JSONDecodeError`，未涵蓋其他可能的 `OSError`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M057 ｜ 標的 python ｜ `sandbox/pr_stats.py:48` ｜ 人工

**_to_epoch 使用 fromisoformat 可能無法解析所有 ISO 格式**

existing_code:
```
return int(datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
```

body：`_to_epoch` 使用 `datetime.datetime.fromisoformat`，但 GitHub API 的時間格式可能包含微秒或時區偏移，某些 Python 版本可能無法解析。建議使用更寬容的解析方式，如 `dateutil.parser`。

evidence：diff 第 40 行：`datetime.datetime.fromisoformat`


## M058 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 events 非空且元素有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但若事件物件缺少 `created_at` 欄位（例如 API 回應格式變更），會拋出 `KeyError`。建議使用 `.get()` 或驗證結構。

evidence：diff 第 35-36 行直接存取鍵，沒有防禦性檢查。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M059 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:43` ｜ 人工

**ahead 可能為空導致數值比較錯誤**

existing_code:
```
if [ "$ahead" -gt 0 ]; then
```

body：若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 可能為空字串，後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而中止腳本。建議先檢查 `ahead` 是否為數字，或設定預設值 0。

evidence：diff 第 41 行：`if [ "$ahead" -gt 0 ]; then`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M060 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M061 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**可變預設參數 seen=[] 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：collect_authors 的 seen 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若多次呼叫 collect_authors 而未傳入 seen，結果會累積先前呼叫的作者，導致資料污染。

建議：使用 None 作為預設值，並在函式內初始化為空串列。

evidence：diff 第 28 行顯示 seen=[]。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M062 ｜ 標的 python ｜ `sandbox/pr_stats.py:40` ｜ 人工

**review_latency 假設 events 非空且第一個事件是 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]`，但若第一個事件沒有 `created_at` 欄位（例如某些事件型別），會拋出 `KeyError`。建議檢查事件型別或使用 `get`。

evidence：diff 第 34-35 行：`first = events[0]["created_at"]` 和 `last = events[-1]["created_at"]`

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M063 ｜ 標的 probe ｜ `sandbox/release_notes.py:96` ｜ 人工

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

## M064 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 可能為空字串，導致 SQL 語法錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議在 rev-list 失敗時設定 ahead=0 或中止。

evidence：第 42 行未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M065 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 人工

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

## M066 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 假設 pr 有 timeline 欄位，但 API 回應可能沒有**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub Pull Request API 的回應中並不一定包含 `timeline` 欄位（除非特別要求）。若 `timeline` 不存在，`events` 會是空 list，函式回傳 0，但這可能不是真正的延遲。

失敗情境：呼叫 `_fetch` 取得 PR 資料時，若未要求 timeline，`pr` 中沒有 `timeline` 鍵，`review_latency` 回傳 0，導致 CSV 中的 latency 欄位全部為 0，失去統計意義。

建議：確認 API 回應結構，或明確處理缺少 timeline 的情況（例如回傳 None 或拋出例外）。

evidence：diff 第 34 行：使用 `get` 提供預設值，但未檢查 `timeline` 是否為有效資料。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M067 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**tag 是第一個 tag 時會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 會是 0，`0 - 1` 變成 -1，`tags[-1]` 會取到最後一個 tag，而不是報錯。這會導致 release notes 的範圍錯誤（從最後一個 tag 到第一個 tag）。

建議：檢查 `tags.index(tag) == 0` 時，提示使用者這是第一個 tag，沒有前一個 tag 可以比較。

evidence：diff 中 `main` 函式的這一行，沒有處理 `tag` 是第一個 tag 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M068 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 人工

**命令注入：`eval` 執行未受信任的 hook 路徑與 repo 名稱**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 函式使用 `eval "$hook $repo"` 執行 hook。`$hook` 是固定路徑，但 `$repo` 來自 repo 目錄名稱，可能包含 shell 特殊字元（例如 `; rm -rf ~`）。攻擊者若能在 repo 根目錄建立惡意名稱的目錄，即可執行任意命令。

**失敗情境**：假設 repo 目錄名稱為 `test; touch /tmp/pwned`，則 `eval` 會執行 `touch /tmp/pwned`。

**建議**：避免使用 `eval`，改為直接執行：
```bash
"$hook" "$repo"
```
並確保 `$hook` 與 `$repo` 都以引號包覆。

evidence：diff 第 52 行：`eval "$hook $repo"`

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M069 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值為可變的 list，會在多次呼叫間共用。若呼叫者未傳入 `seen`，第二次呼叫會包含第一次的結果，導致資料污染。

建議：
- 改用 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 28 行：可變預設值 `seen=[]`，且函式內對其進行 `append` 操作（第 30 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M070 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 人工

**archive 中的 gh repo view 可能將 token 暴露在命令列**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 執行 `gh repo view {repo}`，而 `gh` 命令可能使用環境變數中的 `GITHUB_TOKEN` 進行認證。在某些系統上，命令列參數可能被其他使用者透過 `ps` 看到，導致 token 外洩。

失敗情境：在多使用者系統上，其他使用者可以透過 `ps aux` 看到 `gh repo view` 的參數，若 `gh` 將 token 作為參數傳遞（而非從環境變數讀取），token 會暴露。

建議：確認 `gh` 如何處理認證，避免在命令列中傳遞敏感資訊。

evidence：diff 第 63 行：指令中包含 `gh repo view {repo}`，可能涉及認證。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## M071 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

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

## M072 ｜ 標的 probe ｜ `sandbox/release_notes.py:94` ｜ 人工

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

## M073 ｜ 標的 probe ｜ `sandbox/release_notes.py:30` ｜ 人工

**設定檔 JSON 型別未驗證**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 回傳 `json.load` 的結果，但未驗證其型別是否為 dict。若 `.release-notes.json` 內容為 list 或字串，後續 `cfg.get('title', ...)` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，否則回傳空 dict 或拋出明確錯誤。

evidence：diff 中 `load_config` 直接回傳 `json.load` 結果，未做型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M074 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**例外被完全吞掉，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx 狀態碼或 JSON 解析失敗時，函式會回傳 None。呼叫端（collect_authors 和 main）直接對回傳值進行索引或屬性存取，例如 pr["user"]["login"]，會引發 TypeError 或 KeyError，且錯誤訊息不明確。

建議：至少記錄例外（logging.exception），或重新拋出，讓呼叫端能處理。若希望函式回傳 None，呼叫端應檢查 None 並提供明確錯誤訊息。

evidence：diff 第 24-25 行顯示 except: pass，且後續 collect_authors 與 main 直接使用 pr["user"]["login"] 等索引。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M075 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**`review_latency` 計算邏輯可能不正確**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 從 `pr.get("timeline", [])` 取得事件列表，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位（需要另外請求 timeline API）。因此 `events` 會是空列表，函式回傳 0，導致延遲指標永遠為 0。

建議：確認 API 回應是否包含 timeline，若無則需額外請求或改用其他欄位（如 `created_at` 和 `updated_at`）。

evidence：diff 第 34 行：`pr.get("timeline", [])` 但 GitHub PR API 回應中沒有 `timeline` 欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M076 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

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

## M077 ｜ 標的 python ｜ `sandbox/pr_stats.py:38` ｜ 人工

**review_latency 對空 events 回傳 0，可能誤導指標**

existing_code:
```
if not events:
        return 0
```

body：`review_latency` 在 `events` 為空時回傳 0，但 0 可能被解讀為「零延遲」，而實際上可能是資料缺失。建議回傳 None 或拋出例外，讓呼叫端處理。

evidence：diff 第 35-36 行：空 events 回傳 0。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M078 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 人工

**git checkout 未加引號，branch 名稱可能被 shell 展開**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
```

body：`git checkout $BRANCH` 未將 `$BRANCH` 加上雙引號。雖然前面有格式驗證，但若 branch 名稱包含 glob 字元（例如 `*`）或空白（雖然格式驗證已排除空白），仍可能造成非預期行為。建議改為 `git checkout "$BRANCH"`。

evidence：第 34 行未對 `$BRANCH` 加引號。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## M079 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

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

## M080 ｜ 標的 python ｜ `sandbox/pr_stats.py:51` ｜ 人工

**`threshold_from_env` 的預設參數為可變字典，且未處理轉換例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`def threshold_from_env(default={"days": 7}):` 使用可變字典作為預設值，雖然函式內未修改 `default`，但若未來修改會造成跨呼叫污染。此外，`int(raw)` 轉換環境變數時未處理 `ValueError`，若 `PR_STALE_DAYS` 設為非數字字串，程式會崩潰。

**失敗情境**：
- 使用者設定 `PR_STALE_DAYS=abc`，`int(raw)` 拋出 `ValueError`，程式終止。

**建議**：
- 使用 `None` 作為預設值，並在函式內設定：`def threshold_from_env(default=None):`，然後 `if default is None: default = {"days": 7}`。
- 捕捉 `ValueError` 並提供有意義的錯誤訊息，或使用 `int(raw)` 前先驗證。

evidence：diff 第 44 行：可變預設值，且第 47 行 `int(raw)` 未處理例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## M081 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

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

## M082 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個版本時，prev 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是沒有前一個 tag。這會導致錯誤的 commit 範圍，甚至可能產生空公告或錯誤內容。

**失敗情境**：repo 只有一個 tag `v1.0.0`，使用者執行 `python3 release_notes.py repo v1.0.0`，`tags.index(tag)` 為 0，`prev` 會是 `tags[-1]`（即 `v1.0.0` 本身），`commits_between` 會執行 `git log v1.0.0..v1.0.0`，回傳空列表，程式印出「之間沒有新 commit」並回傳 0，但實際上應該要提示沒有前一個 tag 或改用其他方式。

**建議**：在取 `prev` 前檢查 `tags.index(tag) == 0`，若是則記錄錯誤並回傳非零碼，或改用 `git describe --tags --abbrev=0 <tag>^` 等方式取得前一個 tag。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，沒有處理 `tag` 是第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M083 ｜ 標的 probe ｜ `sandbox/release_notes.py:31` ｜ 人工

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

## M084 ｜ 標的 python ｜ `sandbox/pr_stats.py:25` ｜ 人工

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

## M085 ｜ 標的 python ｜ `sandbox/pr_stats.py:23` ｜ 人工

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

## M086 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sync_one` 函式中，`$name` 與 `$BRANCH` 直接以單引號包覆後插入 SQL 語句。若 repo 目錄名稱或 branch 名稱包含單引號（例如 `test'repo`），會破壞 SQL 語法，甚至可能執行任意 SQL 指令。

**失敗情境**：假設 repo 目錄名稱為 `x'; DROP TABLE runs;--`，則執行的 SQL 會變成：
```sql
INSERT INTO runs VALUES('x'; DROP TABLE runs;--', 'main', 0, datetime('now'))
```
這會刪除 `runs` 資料表。

**建議**：使用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少使用 `sqlite3` 的 `-cmd` 與 `-batch` 模式，並對輸入進行跳脫。

evidence：diff 第 42 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M087 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 人工

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

## M088 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 人工

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

## M089 ｜ 標的 probe ｜ `sandbox/release_notes.py:37` ｜ 人工

**NOTES_MAX 沒有上限，可能造成 payload 過大**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 直接將環境變數 `NOTES_MAX` 轉成整數回傳，沒有設定上限。如果使用者設定一個極大的值（例如 1000000），`commits[: max_items()]` 會嘗試將所有 commit 放入公告，可能導致 webhook payload 過大而被拒絕，或造成記憶體壓力。

**失敗情境**：使用者設定 `NOTES_MAX=1000000`，且 repo 有大量 commit，程式會產生超長的公告文字，webhook 端可能回傳 413 或直接斷線。

**建議**：在 `max_items()` 中設定一個合理的上限（例如 100），超過時記錄警告並使用上限值。

evidence：diff 中 `max_items()` 函式沒有對 `int(raw)` 的結果做上限檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## M090 ｜ 標的 probe ｜ `sandbox/release_notes.py:38` ｜ 人工

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

## M091 ｜ 標的 python ｜ `sandbox/pr_stats.py:37` ｜ 人工

**review_latency 依賴不存在的 timeline 欄位，可能引發 KeyError**

existing_code:
```
events = pr.get("timeline", [])
```

body：review_latency 使用 pr.get("timeline", [])，但 GitHub Pull Request API 的回應中沒有 timeline 欄位（timeline 是另一個 API 端點）。因此 events 永遠為空，函式回傳 0，無法計算實際延遲。若未來 API 變更，可能導致 KeyError。

建議：確認正確的 API 端點或欄位，或明確處理缺失情況。

evidence：diff 第 35 行顯示 pr.get("timeline", [])。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## M092 ｜ 標的 probe ｜ `sandbox/release_notes.py:28` ｜ 人工

**load_config 未驗證 JSON 頂層型別，可能導致後續 AttributeError**

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

body：`load_config` 直接回傳 `json.load` 的結果，沒有檢查是否為 dict。如果 `.release-notes.json` 的內容是合法的 JSON 但不是物件（例如陣列或字串），`main` 中的 `cfg.get('title', ...)` 會拋出 `AttributeError`，導致程式崩潰。

**失敗情境**：使用者誤將設定檔寫成 `["feat", "fix"]` 或 `"hello"`，程式會在執行到 `cfg.get` 時崩潰，且沒有友善的錯誤訊息。

**建議**：在 `load_config` 中檢查 `isinstance(data, dict)`，若不是則拋出 `SystemExit` 或記錄錯誤。

evidence：diff 中 `load_config` 函式直接回傳 `json.load` 的結果，沒有型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## M093 ｜ 標的 python ｜ `sandbox/pr_stats.py:23` ｜ 人工

**`_fetch` 未檢查 HTTP 狀態碼，非 2xx 回應會被當成成功處理**

existing_code:
```
with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
```

body：`urllib.request.urlopen` 在 HTTP 錯誤（如 404、500）時會拋出 `HTTPError`，但此處被 `except` 捕捉後回傳 `None`，呼叫端無法區分錯誤類型。若 API 回傳 401（token 無效），程式會繼續執行並在後續崩潰。

**失敗情境**：
- token 過期時，API 回傳 401，`_fetch` 回傳 `None`，`main` 中 `pr["user"]` 拋出 `TypeError`。

**建議**：
- 在 `urlopen` 後檢查 `resp.status`，非 2xx 時拋出例外或回傳錯誤。

evidence：diff 第 20-22 行：未檢查 `resp.status`，且例外處理不當。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-token：os.environ['GITHUB_TOKEN'] 在 try 外面，沒設就 KeyError
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M094 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 人工

**使用 ls 解析目錄列表，無法處理包含空白或特殊字元的目錄名稱**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 函式中使用 `for d in $(ls "$ROOT")` 來迭代目錄。這種方式會將 `ls` 的輸出以空白、換行等進行 word splitting，導致包含空白的目錄名稱被拆成多個部分，且可能受到 glob 擴展影響。

**失敗情境**：假設 `$ROOT` 下有一個名為 `my repo` 的目錄，則迴圈會將其視為兩個項目 `my` 和 `repo`，導致後續路徑錯誤。

**建議修法**：使用 glob 或 `find` 搭配 `-print0` 與 `while read -d ''` 迴圈：
```bash
while IFS= read -r -d '' d; do
  ...
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
```

evidence：diff 第 76 行：`for d in $(ls "$ROOT"); do`。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## M095 ｜ 標的 python ｜ `sandbox/pr_stats.py:22` ｜ 人工

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

## M096 ｜ 標的 python ｜ `sandbox/pr_stats.py:24` ｜ 人工

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 或 `pr["additions"]` 會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 若預期可能失敗，讓 `_fetch` 回傳 `None` 並在呼叫端檢查。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 72 行）被直接使用。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## M097 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**變數未加引號可能導致意外展開**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 中，若 `$BRANCH` 包含特殊字元（雖然已驗證格式，但可能包含 `..` 等），可能導致 rev-list 參數解析錯誤。建議對所有變數使用引號，並考慮使用 `--` 分隔選項與參數。

evidence：diff 第 39 行：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)`

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M098 ｜ 標的 probe ｜ `sandbox/release_notes.py:95` ｜ 人工

**post 未檢查 HTTP 狀態碼，非 2xx 回應仍視為成功**

existing_code:
```
try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False
```

body：`post` 函式在 `urlopen` 成功後，只回傳 `200 <= resp.status < 300` 的布林值，但呼叫端 `main` 只檢查回傳值是否為 `False`，沒有區分「HTTP 錯誤」和「網路錯誤」。如果 webhook 端回傳 404 或 500，`post` 會回傳 `False`，`main` 會回傳 1（失敗），但錯誤訊息只記錄在 `post` 內部的 `log`，沒有提供足夠的上下文（例如回應內容）。這對除錯不太方便，但功能上仍能正確反映失敗。

**建議**：在 `post` 中記錄 HTTP 狀態碼和回應內容，或讓 `post` 拋出例外由 `main` 統一處理。

evidence：diff 中 `post` 函式只回傳布林值，沒有記錄 HTTP 狀態碼或回應內容。

- 規則提示 PR-A2：log 整段印出含 token 的 webhook URL（實測）
- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M099 ｜ 標的 probe ｜ `sandbox/release_notes.py:91` ｜ 人工

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`post` 直接使用環境變數 NOTES_WEBHOOK 作為 URL，未檢查其 scheme 是否為 http/https。攻擊者若控制環境變數，可指定 `file://` 或 `gopher://` 等 scheme，導致任意檔案讀取或內網請求。建議驗證 URL 的 scheme 必須是 http 或 https。

evidence：diff 中 `url` 來自環境變數，未經 scheme 驗證即傳入 `urllib.request.Request`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## M100 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 計算可能因 rev-list 失敗而得到空值，導致 SQL 錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若指令失敗（例如 branch 不存在），ahead 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會報錯，且 SQL 插入會失敗。建議檢查 ahead 是否為數字，失敗時設為 0 或中止。

evidence：第 34 行未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M101 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:88` ｜ 人工

**`local` 使用在函式外，導致變數作用域錯誤**

existing_code:
```
local target="$ROOT/$d"
```

body：`main` 函式中的 `for d in $(ls "$ROOT"); do` 迴圈內使用了 `local target="$ROOT/$d"`。`local` 只能在函式內使用，在函式外使用會報錯（在某些 bash 版本中會導致腳本終止）。

應移除 `local`，直接賦值：`target="$ROOT/$d"`。

evidence：第 75 行在 main 函式內使用 local，但 main 本身是函式，此處 local 是合法的。然而，若此迴圈不在函式內（例如直接放在腳本主體），則會出錯。根據 diff，此行位於 main 函式內，因此可能不是問題。但需確認 main 函式的範圍。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## M102 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**只有一個 tag 時 `tags.index(tag) - 1` 會取到最後一個 tag**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]`。若 `tags` 只有一個元素（即目前 tag 是第一個 tag），`tags.index(tag)` 為 0，`-1` 會變成 -1，Python 會取到最後一個元素（也就是自己），導致 `prev == tag`，`git log prev..tag` 會是空範圍，`commits` 為空，進而觸發 `IndexError`。建議在 `tags.index(tag) == 0` 時處理（例如回報錯誤或使用 repo 初始 commit）。

evidence：diff 中 `prev = tags[tags.index(tag) - 1]` 未處理 `index` 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M103 ｜ 標的 probe ｜ `sandbox/release_notes.py:32` ｜ 人工

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

## M104 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 人工

**當 tag 是第一個 tag 時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個 tag），`tags.index(tag)` 為 0，`tags[-1]` 會取到最後一個 tag，而不是前一個 tag，這可能不是預期行為。更嚴重的是，如果 tags 為空（雖然前面已檢查 tag 存在，但若 tag 存在於 tags 中，tags 至少有一個元素），但若 tag 是第一個，`tags[-1]` 會取到最後一個，造成錯誤的 prev。建議明確檢查 index 是否為 0，並處理沒有前一個 tag 的情況。

evidence：diff 中 main 函式取得 prev 的方式，未處理 tag 為第一個的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## M105 ｜ 標的 python ｜ `sandbox/pr_stats.py:72` ｜ 人工

**CSV 欄位未處理逗號或換行，可能破壞格式**

existing_code:
```
f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
```

body：`export_csv` 直接使用 f-string 寫入 CSV，若 `author` 或 `kind` 包含逗號或換行，會破壞 CSV 結構。建議使用 `csv` 模組的 writer。

evidence：diff 第 53 行：手動拼接 CSV 欄位，未做 escaping。

- 規則提示 PY-A6：open 沒用 with

## M106 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:41` ｜ 人工

**ahead 可能為空字串，導致 SQL 寫入失敗或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。

建議在取得 ahead 後檢查是否為數字，若不是則設為 0 或中止處理。

evidence：第 38 行未處理 git 指令失敗時 ahead 為空的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## M107 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 人工

**可變預設值 seen=[] 導致跨呼叫狀態污染**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值。Python 在函式定義時只建立一次該 list，之後每次呼叫都會共用同一個 list 物件。如果呼叫者沒有傳入 `seen`，多次呼叫會累積之前的結果。

具體情境：
- 在同一個 process 中呼叫 `collect_authors('repo', [1])` 兩次，第二次呼叫會回傳 `['user1', 'user1']` 而不是 `['user1']`。
- 這在測試或互動式環境中很容易造成難以追蹤的 bug。

建議：
- 改用 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

evidence：diff 第 31 行，`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 33 行）。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## M108 ｜ 標的 probe ｜ `sandbox/release_notes.py:39` ｜ 人工

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

## M109 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:33` ｜ 人工

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

## M110 ｜ 標的 python ｜ `sandbox/pr_stats.py:72` ｜ 人工

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

# 抽查（自動標記；同意就不用寫，有異議才寫進 blind-labels.csv）

## S001 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**NOTES_MAX 可設為負數導致切片錯誤**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 直接將環境變數轉為整數，未驗證是否為正數。若設定為負數，`commits[: max_items()]` 會產生錯誤切片（例如 `[:-1]` 會排除最後一個元素）。建議檢查數值範圍，例如 `if n < 1: return DEFAULT_MAX`。

evidence：diff 中 `max_items` 未檢查轉換後的整數是否為正數。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## S002 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`name` 與 `BRANCH` 直接以字串串接方式插入 SQL 查詢，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'; DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對輸入進行單引號跳脫（`${name//\'/\'\'}`）。

evidence：第 42 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S003 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 與 `repo` 來自命令列參數（`sys.argv`），攻擊者可注入額外指令。例如 `repo` 設為 `x; rm -rf /` 會執行任意命令。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 與 `subprocess.run(["gh", "repo", "view", repo])`。
- 若必須使用 shell，需對輸入進行嚴格驗證或轉義。

evidence：diff 第 82 行：`shell=True` 且 f-string 包含 `path` 與 `repo`，兩者皆來自使用者輸入。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## S004 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**可變預設值 seen=[] 跨呼叫共用**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen=[]` 是可變預設值，每次呼叫都會累積到同一個 list，導致結果包含前一次呼叫的作者。例如第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`。建議改用 `seen=None` 並在函式內初始化。

evidence：diff 第 28 行：函式定義使用可變預設值 `seen=[]`。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## S005 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

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

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## S006 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

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

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## S007 ｜ 標的 probe ｜ `sandbox/release_notes.py:31` ｜ 自動：PR-B2 → invalid

**`load_config` 僅處理 FileNotFoundError 和 JSONDecodeError，其他例外（如權限錯誤）會導致程式崩潰**

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

body：`load_config` 使用 `open` 讀取檔案，若檔案存在但無法讀取（例如權限不足），會拋出 PermissionError，未被捕捉，導致程式以 traceback 結束。建議捕捉 OSError 或更廣泛的例外，並提供友善錯誤訊息。

evidence：diff 中 load_config 的例外處理僅限於 FileNotFoundError 和 JSONDecodeError。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## S008 ｜ 標的 python ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

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

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## S009 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入漏洞**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`$name` 與 `$BRANCH` 直接插入 SQL 字串，未經跳脫。若 repo 目錄名稱或 branch 名稱包含單引號，將可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。建議使用 sqlite3 的參數綁定功能，或至少以 `sqlite3_escape` 函數跳脫輸入。

evidence：第 42 行直接將變數嵌入 SQL 字串，未做任何跳脫。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S010 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中 `git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向至 log，未檢查退出碼。若 fetch 失敗（例如網路問題），後續 checkout 或 merge 可能基於過時資料，導致錯誤的 ahead 計算或合併失敗。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：diff 第 30-32 行：`git fetch origin --prune 2>>"$LOG"` 等

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S011 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

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

- 規則提示 SH-S4：cd 沒有 || exit
- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S012 ｜ 標的 python ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

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

- 規則提示 PY-A6：open 沒用 with

## S013 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串中拼接了 `path` 和 `repo`。這兩個參數來自命令列參數（`repo`）或由 `repo` 衍生（`path`），攻擊者可注入額外 shell 命令。

具體攻擊情境：執行 `python pr_stats.py '$(rm -rf /)' 1` 時，`repo` 的值會被 shell 展開，導致任意命令執行。

建議：改用 `subprocess.run` 的 list 形式，避免 `shell=True`；或使用 `shlex.quote` 對參數進行轉義。

evidence：diff 第 73 行：`shell=True` 且 f-string 包含外部輸入。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## S014 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**cleanup_cache 使用 rm -rf 且路徑未驗證，可能誤刪重要資料**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`rm -rf "$ROOT"/.cache/*` 若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期檔案。建議檢查 `$ROOT` 是否存在且為目錄，並避免使用萬用字元，或改用更安全的刪除方式（例如 find 搭配 -delete）。

evidence：第 63 行直接使用 rm -rf 搭配萬用字元，未做任何防護。

- 規則提示 SH-S5：$ROOT 未檢查就 rm -rf
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S015 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

**for 迴圈使用 ls 輸出，檔名含空格或換行會出錯**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 會將 `ls` 的輸出以空白分割，若 repo 目錄名稱包含空格或換行，會被拆成多個項目，導致後續路徑錯誤。

**失敗情境**：目錄名為 `my repo` 時，迴圈會迭代 `my` 和 `repo` 兩個項目，`target` 路徑錯誤。

**建議**：使用 glob 或 find 搭配 while read：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  ...
done
```

evidence：diff 第 78 行：`for d in $(ls "$ROOT")` 使用 ls 輸出且未正確處理檔名中的特殊字元。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## S016 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 自動：SH-K-gitfail → valid

**`git checkout` 與 `git merge` 失敗未中止，可能導致錯誤結果**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中 `git checkout $BRANCH` 與 `git merge --ff-only` 的輸出僅重導至 log，未檢查退出狀態。若 checkout 失敗（例如 branch 不存在），後續 merge 可能基於錯誤的 branch 執行，或 `ahead` 計算錯誤。建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並跳過該 repo。

evidence：第 34-35 行未檢查 git 指令的退出碼。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S017 ｜ 標的 python ｜ `sandbox/pr_stats.py:29` ｜ 自動：PY-A2 → valid

**collect_authors 使用可變預設值，跨呼叫累積結果**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時結果累積，且呼叫者無法預期初始狀態。

失敗情境：第一次呼叫 `collect_authors(repo, [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors(repo, [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：改用 `seen=None`，在函式內初始化為空 list。

evidence：diff 第 28 行：參數預設值為 `[]`，且函式內對 `seen` 進行 `append` 操作。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## S018 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 git log 的 return code，可能把錯誤輸出當成正常結果**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

evidence：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## S019 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**local 關鍵字在函式外使用，可能導致非預期行為**

existing_code:
```
local target="$ROOT/$d"
```

body：在 `main` 函式中，`local target="$ROOT/$d"` 使用了 `local`，但 `local` 只能在函式內使用。雖然在 bash 中函式外的 `local` 會被忽略，但可能造成混淆。建議移除 `local` 或改為一般變數賦值。

evidence：diff 第 74 行，local 使用於函式外。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## S020 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:37` ｜ 自動：SH-K-gitfail → valid

**`git checkout` 與 `git merge` 失敗時未中止，可能導致後續操作在錯誤狀態下執行**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中執行 `git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"`，但未檢查其退出狀態。如果 checkout 失敗（例如 branch 不存在），後續的 merge 與 rev-list 可能基於錯誤的 HEAD 執行，導致資料不正確。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並返回非零狀態。

evidence：diff 第 31-32 行：`git checkout` 與 `git merge` 未檢查退出狀態。

- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S021 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：`eval` 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"` 執行 hook。雖然 `$hook` 是固定路徑，但 `$repo` 來自目錄名稱，攻擊者可建立名稱包含 shell 特殊字元的 repo 目錄（例如 `x; rm -rf ~`），導致任意命令執行。

建議避免使用 `eval`，改為直接執行並正確引用參數：
```bash
"$hook" "$repo"
```

evidence：第 58 行使用 eval 執行包含未受信任變數的字串。

- 規則提示 SH-S2：eval 的 $repo 來自目錄名
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S022 ｜ 標的 python ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**環境變數轉換為整數未處理例外**

existing_code:
```
return {"days": int(raw)}
```

body：threshold_from_env 使用 int(raw) 轉換環境變數 PR_STALE_DAYS，若使用者設定非數字字串（例如 "abc"），會拋出 ValueError 且未處理，導致程式崩潰。

建議：捕捉 ValueError 並提供有意義的錯誤訊息，或使用預設值。

evidence：diff 第 44 行顯示 int(raw)。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## S023 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**路徑處理不當：`rm -rf "$ROOT"/.cache/*` 可能誤刪檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 使用 `rm -rf "$ROOT"/.cache/*`，若 `$ROOT` 未設定或為空，將變成 `rm -rf /.cache/*`，可能刪除系統檔案。此外，若 `.cache` 不存在，`rm` 會報錯但腳本仍繼續。建議先檢查 `$ROOT` 是否為空，並使用 `find` 或 `rm -rf -- "$ROOT/.cache"` 後再重建目錄。

evidence：第 58 行直接使用變數拼接路徑，且未檢查 `$ROOT` 是否為空。

- 規則提示 SH-S5：$ROOT 未檢查就 rm -rf
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S024 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:38` ｜ 自動：SH-K-gitfail → valid

**git merge 未檢查失敗，可能導致後續操作在錯誤狀態下執行**

existing_code:
```
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`git merge --ff-only "origin/$BRANCH"` 若因衝突或非 fast-forward 而失敗，腳本不會中止，仍會繼續計算 ahead 並寫入資料庫。這可能導致資料庫記錄不正確的同步結果。建議在 merge 後檢查 exit code，失敗時記錄錯誤並跳過該 repo。

evidence：第 36 行未檢查 merge 的 exit code。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-B1：第 16 行 regex 已排除空白與 glob。提到驗證、只建議加引號更穩健 → disputed（人工）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-gitfail：git fetch/checkout/merge 失敗照樣往下寫資料庫

## S025 ｜ 標的 python ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（外部輸入）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`，導致任意指令執行。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 80 行使用 `shell=True` 且 f-string 包含外部輸入 `repo`。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## S026 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 將 `$name` 與 `$BRANCH` 直接嵌入 SQL 字串。若 repo 目錄名稱或 branch 名稱包含單引號，會破壞 SQL 語法，甚至可注入任意 SQL。例如 repo 名稱為 `x'); DROP TABLE runs;--` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```
或至少對變數做單引號跳脫（`${name//\'/\'\'}`）。

evidence：diff 第 46 行：`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"`

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## S027 ｜ 標的 probe ｜ `sandbox/release_notes.py:32` ｜ 自動：PR-B2 → invalid

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

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## S028 ｜ 標的 python ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**threshold_from_env 的 int 轉換未處理例外，可能導致程式崩潰**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 int，若該值不是合法整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式終止。建議使用 try/except 或先驗證輸入。

evidence：diff 第 45 行：`int(raw)` 無例外處理。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## S029 ｜ 標的 shell ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：在 `sync_one` 中，`sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"` 直接將 `$name` 和 `$BRANCH` 嵌入 SQL 字串。雖然 `$BRANCH` 已用正規表達式限制字元集，但 `$name` 來自 `basename "$dir"`，而 `$dir` 來自 `ls "$ROOT"` 的輸出，攻擊者若能在 repo 根目錄建立名稱包含單引號的目錄（例如 `'; DROP TABLE runs; --`），即可注入任意 SQL 語句，造成資料毀損或洩漏。建議改用參數化查詢，例如 `sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"`，或至少對 `$name` 和 `$BRANCH` 進行單引號跳脫。

evidence：diff 第 42 行新增的 SQL 插入語句，直接使用變數拼接。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
