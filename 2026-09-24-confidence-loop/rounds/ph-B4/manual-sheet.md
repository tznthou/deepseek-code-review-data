# ph-B4 人工標記單（盲標：不含 confidence、severity）

自動 69 筆、人工 21 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-B4:python:1:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

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

## ph-B4:python:1:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

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

## ph-B4:python:2:1 ｜ `sandbox/pr_stats.py:26` ｜ 候選：PY-A1, PY-K-status

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

## ph-B4:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-B4:python:2:4 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

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

## ph-B4:python:3:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

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

## ph-B4:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-B4:python:3:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

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

## ph-B4:python:4:6 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有序**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接取 `events[0]` 和 `events[-1]`，但沒有檢查 `events` 是否為空（雖然有 `if not events` 的檢查，但若 `events` 為 `None` 會拋出 `TypeError`）。此外，它假設事件按時間排序，但 GitHub API 的回傳順序可能不保證。建議明確處理 `None` 情況，並考慮對事件按時間排序後再計算。

evidence：diff 第 40-41 行：直接索引 events，未處理 None 或順序問題。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-B4:python:5:2 ｜ `sandbox/pr_stats.py:22` ｜ 候選：PY-A1, PY-K-status

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

## ph-B4:python:5:4 ｜ `sandbox/pr_stats.py:31` ｜ 候選：PY-A3, PY-A4

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

## ph-B4:python:5:7 ｜ `sandbox/pr_stats.py:77` ｜ 候選：無

**`archive` 未檢查 `subprocess.run` 回傳值**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`subprocess.run` 預設不拋出例外，若 `tar` 或 `gh` 指令失敗（例如路徑不存在、權限不足），程式仍會繼續執行並回報成功。建議檢查 `returncode` 或使用 `check=True`。

evidence：diff 第 64 行顯示 `subprocess.run` 未檢查回傳值。

- 規則提示 PY-A7：shell=True + f-string 拼 argv 來的 repo

## ph-B4:shell:1:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能失敗且未處理**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（如 branch 不存在），`ahead` 會是空字串，後續 `[ "$ahead" -gt 0 ]` 會因語法錯誤而終止腳本。建議檢查 `ahead` 是否為數字，失敗時設為 0 或跳過。

evidence：diff 第 36 行，未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B4:shell:1:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

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

## ph-B4:shell:2:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**變數 ahead 可能未定義或為空，導致 SQL 插入失敗或錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 git 指令失敗（例如 branch 不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會造成 SQL 語法錯誤。建議在計算後檢查 `ahead` 是否為數字，失敗時設為 0 或中止。

evidence：第 31 行未處理 git 指令失敗時 ahead 為空的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B4:probe:1:2 ｜ `sandbox/release_notes.py:94` ｜ 候選：無

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

## ph-B4:probe:1:3 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 是第一個版本時會 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 的第一個元素。如果使用者指定了最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致錯誤的比較範圍。建議檢查 `tags.index(tag) == 0` 並處理此情況。

evidence：diff 中該行直接使用 `-1` 索引，未處理 `tag` 為第一個元素的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B4:probe:3:3 ｜ `sandbox/release_notes.py:39` ｜ 候選：PR-X1, PR-B3(unless)

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

## ph-B4:probe:4:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳的第一個 tag（例如 repo 中只有一個符合 `v*` 的 tag），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式會直接 crash。建議在取 `prev` 前檢查 index 是否大於 0，若為 0 則提示使用者這是第一個版本，或改用其他方式取得起始點。

evidence：diff 第 104 行，直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為負數。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B4:probe:4:3 ｜ `sandbox/release_notes.py:32` ｜ 候選：PR-B2(unless)

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

## ph-B4:probe:5:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

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

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-B4:python:2:6 ｜ `sandbox/pr_stats.py:59` ｜ 自動：PY-K-classify → disputed

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

## ph-B4:python:4:1 ｜ `sandbox/pr_stats.py:26` ｜ 自動：PY-A1 → valid

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。建議：至少記錄例外並重新拋出，或回傳一個明確的錯誤物件，讓呼叫端能處理。

evidence：diff 第 26 行：`except: pass` 吞掉所有例外，且函式沒有回傳值，導致呼叫端無法區分成功與失敗。

## ph-B4:python:5:6 ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

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

## ph-B4:shell:2:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：eval 執行未受信任的 hook 路徑與參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"`，若 `$hook` 或 `$repo` 包含 shell 特殊字元，將導致任意命令執行。例如 repo 名稱為 `; rm -rf ~` 時，會執行刪除指令。建議改用直接執行 `"$hook" "$repo"`，避免 eval。

evidence：第 50 行使用 eval 執行字串，變數未經安全處理。

## ph-B4:shell:3:4 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行**

existing_code:
```
git fetch origin --prune 2>>"$LOG"
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`git fetch`、`git checkout`、`git merge` 的錯誤僅被重導向到 log，但腳本未檢查其退出狀態。若 fetch 失敗（如網路問題），後續 checkout 與 merge 可能基於過時的遠端分支，導致錯誤的同步結果。建議在每個 git 指令後檢查 `$?` 並在失敗時中止或記錄錯誤。

evidence：diff 第 36-38 行，未檢查退出碼。

## ph-B4:shell:4:6 ｜ `sandbox/repo_sync.sh:68` ｜ 自動：SH-B2 → invalid

**`summarize` 中 `grep -c .` 可能因檔案不存在而回傳非零，但已用 `|| total=0` 處理**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`total=$(grep -c . "$LOG" 2>/dev/null) || total=0` 在 `$LOG` 不存在時，`grep` 回傳非零，`total` 會被設為 0，但 `grep` 的錯誤輸出已被重導向，因此不會顯示錯誤。此處理方式可接受，但建議明確檢查檔案是否存在。

evidence：第 61 行使用 `||` 處理錯誤，但未檢查檔案存在性。

## ph-B4:probe:1:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

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

## ph-B4:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**`tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中先檢查 `if tag not in tags`，但 `tags` 是 `list_tags` 回傳的 list，而 `list_tags` 只回傳符合 `TAG_RE` 的 tag。若使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為 True，會先印出錯誤並 return 2，不會執行到 `tags.index(tag)`。但若 `list_tags` 因某些原因回傳的 list 不包含該 tag（例如 tag 名稱符合 regex 但實際不存在），則 `tags.index(tag)` 會拋出 `ValueError`，導致程式崩潰。建議使用 `try/except` 或先檢查 `tag in tags` 再取 index。

evidence：diff 中 `main` 函式在 `if tag not in tags` 檢查後直接使用 `tags.index(tag)`，但未處理 `ValueError`。
