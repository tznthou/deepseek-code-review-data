# ph-A1 人工標記單（盲標：不含 confidence、severity）

自動 60 筆、人工 28 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-A1:python:1:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

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

## ph-A1:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-A1:python:1:4 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

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

## ph-A1:python:1:5 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

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

## ph-A1:python:1:7 ｜ `sandbox/pr_stats.py:23` ｜ 候選：PY-A1, PY-K-status

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

## ph-A1:python:2:5 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

**review_latency 假設 events 存在且非空，但 PR 物件可能沒有 timeline 鍵**

existing_code:
```
events = pr.get("timeline", [])
```

body：`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 鍵，因此 `events` 會是空 list，函式回傳 0。這可能不是預期行為。建議確認 API 回應結構或改用其他方式取得時間資料。

evidence：diff 第 34 行：`events = pr.get("timeline", [])`，但 GitHub PR API 回應中沒有 `timeline` 欄位。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A1:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

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

## ph-A1:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-A1:python:3:4 ｜ `sandbox/pr_stats.py:38` ｜ 候選：PY-B1

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

## ph-A1:python:4:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

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

## ph-A1:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-A1:python:5:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 events 非空且元素有 created_at**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但若事件物件缺少 `created_at` 欄位（例如 API 回應格式變更），會拋出 `KeyError`。建議使用 `.get()` 或驗證結構。

evidence：diff 第 35-36 行直接存取鍵，沒有防禦性檢查。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## ph-A1:shell:1:5 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

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

## ph-A1:shell:3:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 可能為空字串，導致 SQL 語法錯誤**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若 rev-list 失敗（例如 origin/$BRANCH 不存在），ahead 會是空字串。後續 `[ "$ahead" -gt 0 ]` 會出錯，且 SQL 插入時 `$ahead` 為空會造成語法錯誤。建議在 rev-list 失敗時設定 ahead=0 或中止。

evidence：第 42 行未處理 rev-list 失敗的情況。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-A1:shell:4:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

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

## ph-A1:shell:4:5 ｜ `sandbox/repo_sync.sh:88` ｜ 候選：SH-S7, SH-K-local

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

## ph-A1:shell:4:6 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

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

## ph-A1:shell:5:5 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

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

## ph-A1:probe:1:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，prev 會取到最後一個 tag**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`0 - 1` 等於 -1，Python 會取到最後一個元素。這會導致 release notes 涵蓋從最後一個 tag 到第一個 tag 的所有 commit，而不是空範圍。建議在 `tags.index(tag) == 0` 時處理為沒有前一個 tag 的情況（例如回傳空列表或提示錯誤）。

evidence：diff 中 `main` 函式內 `prev = tags[tags.index(tag) - 1]`，沒有檢查 `tags.index(tag)` 是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A1:probe:2:3 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

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

## ph-A1:probe:3:5 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 清單可能為空導致 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`main` 中 `prev = tags[tags.index(tag) - 1]` 假設 `tags` 至少有一個元素。若 `list_tags` 回傳空清單（例如 repo 中沒有符合的 tag），`tags.index(tag)` 會拋出 `ValueError`，但若 `tag` 存在於空清單中不可能，因此實際上會先觸發 `ValueError`。但若 `tags` 只有一個元素且 `tag` 是第一個，`tags.index(tag) - 1` 會是 -1，導致 `prev` 為最後一個元素，可能不是預期的前一個 tag。建議檢查 `tags.index(tag) > 0`。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未檢查索引是否大於 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-A1:probe:3:7 ｜ `sandbox/release_notes.py:104` ｜ 候選：無

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

## ph-A1:probe:4:2 ｜ `sandbox/release_notes.py:42` ｜ 候選：PR-X1, PR-B3(unless)

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

## ph-A1:probe:4:3 ｜ `sandbox/release_notes.py:28` ｜ 候選：PR-B2(unless)

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

## ph-A1:probe:4:4 ｜ `sandbox/release_notes.py:95` ｜ 候選：PR-A2, PR-B7(unless)

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

## ph-A1:probe:4:5 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

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

## ph-A1:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

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

## ph-A1:probe:5:3 ｜ `sandbox/release_notes.py:37` ｜ 候選：無

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

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-A1:python:3:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

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

## ph-A1:python:5:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（外部輸入）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`，導致任意指令執行。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 80 行使用 `shell=True` 且 f-string 包含外部輸入 `repo`。

## ph-A1:shell:1:4 ｜ `sandbox/repo_sync.sh:37` ｜ 自動：SH-K-gitfail → valid

**`git checkout` 與 `git merge` 失敗時未中止，可能導致後續操作在錯誤狀態下執行**

existing_code:
```
git checkout $BRANCH 2>>"$LOG"
git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中執行 `git checkout $BRANCH` 與 `git merge --ff-only "origin/$BRANCH"`，但未檢查其退出狀態。如果 checkout 失敗（例如 branch 不存在），後續的 merge 與 rev-list 可能基於錯誤的 HEAD 執行，導致資料不正確。

建議在每個 git 指令後檢查 `$?`，失敗時記錄錯誤並返回非零狀態。

evidence：diff 第 31-32 行：`git checkout` 與 `git merge` 未檢查退出狀態。

## ph-A1:shell:2:7 ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

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

## ph-A1:shell:4:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

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

## ph-A1:probe:1:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

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

## ph-A1:probe:3:4 ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

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
