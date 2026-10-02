# v05 人工標記單（盲標：不含 confidence、severity）

自動 64 筆、人工 23 筆、抽查 8 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## v05:python:1:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值，導致跨呼叫累積作者**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為 `[]`，這是一個可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者附加到同一個 list，導致結果累積。例如：第一次呼叫後 `seen` 包含 A，第二次呼叫會包含 A 和 B。建議：將預設值改為 `None`，並在函式內初始化為空 list。

evidence：diff 第 31 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v05:python:1:4 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

**review_latency 假設 timeline 事件存在且有 created_at 欄位**

existing_code:
```
first = events[0]["created_at"]
    last = events[-1]["created_at"]
```

body：`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但事件物件可能缺少 `created_at` 欄位（例如某些事件類型），導致 `KeyError`。建議：使用 `.get("created_at")` 並處理缺失值。

evidence：diff 第 38-39 行：直接索引事件物件的 `created_at`。

- 規則提示 PY-B1：events[0]：第 38 行已守住空列表。報空列表 IndexError 而沒提第 38 行 → invalid；說 None 會通過 not events → invalid（not None 為真、直接 return 0）；說直接存取 pr['timeline'] → invalid（實際是 .get）；明說已處理、改報 created_at 缺欄位或順序 → disputed

## v05:python:1:5 ｜ `sandbox/pr_stats.py:54` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 的預設值為可變 dict，且 int() 轉換可能失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，這是一個可變 dict，但函式內沒有修改它，所以不會造成跨呼叫污染（此點不報）。然而，`int(raw)` 若環境變數不是有效整數會拋出 `ValueError`，導致程式崩潰。建議：捕捉 `ValueError` 並提供有意義的錯誤訊息。

evidence：diff 第 46 行：`int(raw)` 未處理轉換失敗。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## v05:python:2:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致靜默失敗**

existing_code:
```
except:
        pass
```

body：`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得呼叫端無法得知失敗。例如當 API 回傳 404 或 token 無效時，`_fetch` 會回傳 `None`，後續程式碼（如 `pr["user"]["login"]`）會拋出 `TypeError`，但真正的錯誤原因已被隱藏。建議至少記錄錯誤並重新拋出，或讓函式回傳明確的錯誤結果。

evidence：diff 第 24 行顯示 `except: pass`，且 `_fetch` 被多處呼叫（如 `collect_authors` 和 `main` 中），呼叫端未檢查回傳值是否為 `None`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v05:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取，若 `_fetch` 失敗，會拋出 `TypeError` 或 `KeyError`，且沒有原始錯誤資訊。

建議：
- 至少記錄錯誤（`logging.exception`）並重新拋出或回傳 None，讓呼叫端處理。
- 檢查 HTTP 狀態碼（`resp.status`），非 2xx 時拋出例外。
- 避免裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError`）。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v05:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**collect_authors 使用可變預設值 seen=[]，跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的 `seen` 參數預設為空 list，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者加到同一個 list，導致結果累積。

建議：改為 `seen=None`，在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

evidence：diff 第 28 行：`seen=[]` 是可變預設值。

- 規則提示 PY-A2：seen=[] 跨呼叫共用，第 32 行真的 append
- 規則提示 PY-A3：_fetch 失敗回 None，第 32 行直接 pr["user"]
- 規則提示 PY-A4：迴圈內 HTTP I/O；collect_authors 與 main 各 fetch 一次同一批 PR

## v05:python:4:4 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

**threshold_from_env 使用可變預設值，且未處理轉換例外**

existing_code:
```
def threshold_from_env(default={"days": 7}):
```

body：`threshold_from_env` 的參數 `default={"days": 7}` 使用可變預設值，雖然函式內未修改該字典，但若未來修改可能導致問題。此外，`int(raw)` 可能拋出 `ValueError`（例如環境變數設為非數字），導致程式崩潰。建議改用不可變預設值（如 `None`）並處理轉換例外。

evidence：diff 第 38 行顯示可變預設值，且第 40 行 `int(raw)` 未處理例外。

- 規則提示 PY-A5：int(raw) 轉環境變數沒處理 ValueError
- 規則提示 PY-B2：default={"days": 7} 從沒被修改（python.md 明寫不要報）

## v05:python:5:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

**_fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰**

existing_code:
```
except:
        pass
```

body：`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，當 `_fetch` 失敗時會得到 `None`，接著存取 `pr["user"]` 或 `pr["additions"]` 會拋出 `TypeError`，造成程式崩潰。

**失敗情境**：網路中斷、API 回傳 404（PR 不存在）、token 無效、回應不是合法 JSON 時，程式會以未處理的例外結束。

**建議**：
- 讓 `_fetch` 在失敗時拋出例外（不要 `pass`），或回傳一個明確的錯誤值，並在呼叫端檢查。
- 至少記錄錯誤訊息（例如 `logging.exception`）以便除錯。
- 考慮使用 `raise ... from err` 保留原始例外資訊。

evidence：diff 第 24-25 行：`except:` 後只有 `pass`，沒有回傳值或重新拋出。呼叫端如第 29 行 `pr = _fetch(...)` 後直接 `pr["user"]`，若 `_fetch` 回傳 `None` 會拋出 `TypeError`。

- 規則提示 PY-A1：裸 except + pass 吞掉所有例外；順帶講到 _fetch 回 None、下游 TypeError 也算在內（A3）
- 規則提示 PY-K-status：主張是『404 時 json.loads 會解析錯誤頁』→ invalid（urlopen 先拋 HTTPError）；只是 A1 的一部分 → 照 A1

## v05:python:5:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

**可變預設值 seen=[] 導致跨呼叫累積**

existing_code:
```
def collect_authors(repo, numbers, seen=[]):
```

body：`collect_authors` 的參數 `seen=[]` 使用可變預設值，該 list 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留，造成結果不正確。

**失敗情境**：若在同一個程序內呼叫 `collect_authors` 兩次（例如處理多個 repo），第二次呼叫的結果會包含第一次的作者。

**建議**：改用 `None` 作為預設值，並在函式內初始化：
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

## v05:shell:1:8 ｜ `sandbox/repo_sync.sh:68` ｜ 候選：無

**效能問題：summarize 使用 grep -c 計算行數，可能讀取整個檔案**

existing_code:
```
total=$(grep -c . "$LOG" 2>/dev/null) || total=0
```

body：`grep -c . "$LOG"` 會讀取整個日誌檔來計算行數，若日誌很大可能影響效能。

建議改用 `wc -l < "$LOG"` 來取得行數。

evidence：第 64 行使用 grep -c 計算行數，效率較低。

- 規則提示 SH-B2：v2：grep -c ... || total=0，四種 log 狀態實測都是數字
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v05:shell:2:5 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-S3

**ahead 可能為空字串，導致 SQL 語法錯誤**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：若 `git rev-list` 失敗（例如 HEAD 不存在），`ahead` 會是空字串，插入 SQL 時會變成 `INSERT INTO runs VALUES('repo', 'branch', , datetime('now'))`，導致 SQL 錯誤。建議在插入前檢查 ahead 是否為數字，或設定預設值 0。

evidence：第 45 行直接使用可能為空的 ahead。

- 規則提示 SH-S1：$name 內插進 SQL；順帶說 $BRANCH 也能注入是錯的，但主張成立
- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v05:shell:3:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3, SH-C1

**變數未加引號：`ahead` 可能為空導致 `[ "$ahead" -gt 0 ]` 報錯**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)

  if [ "$ahead" -gt 0 ]; then
```

body：`ahead=$(git rev-list --count ... 2>/dev/null)` 若 `git rev-list` 失敗（例如 branch 不存在），`ahead` 會是空字串。接著 `[ "$ahead" -gt 0 ]` 會因為空字串無法轉為整數而報錯，且錯誤訊息會輸出到終端（未重導），可能中斷腳本（若 `set -e` 啟用）或造成困擾。

**失敗情境**：若 `origin/$BRANCH` 不存在（例如 branch 名稱打錯但通過格式驗證），`git rev-list` 失敗，`ahead` 為空，`[ "$ahead" -gt 0 ]` 會輸出錯誤訊息，且後續 SQL 插入的 `ahead` 為空字串，可能導致型別不符。

**建議**：在計算 `ahead` 後檢查是否為數字，或提供預設值：
```bash
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null) || ahead=0
```
並在測試條件中使用 `[[ $ahead =~ ^[0-9]+$ ]] && [ "$ahead" -gt 0 ]`。

evidence：diff 第 40-42 行：`ahead` 可能為空，未處理。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## v05:shell:3:7 ｜ `sandbox/repo_sync.sh:87` ｜ 候選：SH-S7, SH-K-rootdir

**`for d in $(ls "$ROOT")` 無法處理含空格或換行的目錄名稱**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`main` 使用 `for d in $(ls "$ROOT")` 迭代目錄，若目錄名稱包含空格或換行，會被拆成多個項目，導致路徑錯誤。此外，`ls` 的輸出可能包含特殊字元，造成非預期行為。

**失敗情境**：若 `$ROOT` 下有名為 `my repo` 的目錄，`for` 迴圈會將其拆成 `my` 和 `repo` 兩個項目，後續 `target="$ROOT/$d"` 會指向不存在的路徑。

**建議**：使用 glob 或 `find` 搭配 `-print0` 和 `while read -d ''` 來處理：
```bash
for d in "$ROOT"/*/; do
  d=${d%/}
  d=${d##*/}
  ...
done
```

evidence：diff 第 82 行：使用 `$(ls ...)` 進行迭代。

- 規則提示 SH-S7：for d in $(ls)
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-local：main 是函式，local 合法；09-21 預期表列為附帶
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v05:shell:5:6 ｜ `sandbox/repo_sync.sh:94` ｜ 候選：無

**效能問題：每個 repo 都執行 `git fetch`，可能造成大量網路請求**

existing_code:
```
sync_one "$target"
```

body：若 repo 數量眾多，逐一 `git fetch` 可能耗時較長，且無平行處理。建議考慮使用 `xargs -P` 或平行工具來加速，或至少提供進度提示。

evidence：diff 第 74 行：在迴圈中呼叫 `sync_one`，其中包含 `git fetch`。

- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 SH-K-rootdir：說迴圈會進入不存在的目錄 → invalid（ls 沒輸出、迴圈不跑）；說會靜默什麼都沒做 → valid

## v05:probe:1:3 ｜ `sandbox/release_notes.py:39` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 為負數時切片行為出乎意料**

existing_code:
```
try:
        return int(raw)
    except ValueError:
```

body：`max_items()` 只檢查是否能轉成整數，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=-5`，`commits[: -5]` 會回傳除了最後 5 筆以外的所有 commit，而不是預期的「最多 5 筆」。

建議：轉換後檢查 `value > 0`，否則回傳預設值或記錄警告。

evidence：diff 中 `max_items` 函式直接回傳 `int(raw)`，沒有檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v05:probe:2:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**只有一個符合條件的 tag 時會 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tags` 只有一個元素且該元素就是 `tag` 時，`tags.index(tag)` 回傳 0，`0 - 1` 變成 -1，`tags[-1]` 會取到同一個 tag，導致 `prev == tag`，`git log prev..tag` 會是空範圍。如果 `tags` 是空 list（但前面已檢查 `tag in tags`，所以不會是空），但只有一個 tag 時會發生。建議在只有一個 tag 時明確處理，例如回傳錯誤或改用 `--max-count` 等方式。

evidence：diff 中 `prev = tags[tags.index(tag) - 1]` 沒有檢查 `tags.index(tag)` 是否為 0。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v05:probe:2:3 ｜ `sandbox/release_notes.py:38` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 設為負數或零時會產生空公告或錯誤**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items()` 只檢查 `int(raw)` 是否拋出 `ValueError`，但沒有檢查轉換後的值是否為正整數。如果 `NOTES_MAX=0`，`commits[:0]` 會是空 list，`group` 會回傳空 sections，`render` 會產生只有標題的公告。如果 `NOTES_MAX=-1`，`commits[:-1]` 會排除最後一個 commit，可能不是預期行為。建議加上 `if n <= 0: log(...); return DEFAULT_MAX` 或類似防護。

evidence：diff 中 `max_items` 只處理 `ValueError`，未檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v05:probe:2:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

**webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    # 不重試：webhook 端沒有冪等鍵，重送一次頻道裡就會出現兩則一樣的公告
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
```

body：`post` 直接使用 `urllib.request.urlopen(req)`，沒有檢查 URL 的 scheme 是否為 `https` 或 `http`。如果環境變數 `NOTES_WEBHOOK` 被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或傳送資料到非預期的位置。建議在 `main` 中驗證 URL 的 scheme 和 host，或至少限制為 `https`。

evidence：diff 中 `post` 未對 `url` 做任何驗證，直接傳給 `urlopen`。

- 規則提示 PR-B7：post 失敗回 False，main 第 128 行檢查後回 1（實測）；HTTPError 是 URLError 子類別
- 規則提示 PR-B8：不重試是註解寫明的刻意決定
- 規則提示 PR-B11：NOTES_WEBHOOK 由操作者設定，不是外部輸入
- 規則提示 PR-X4：讀取逾時丟 TimeoutError、post 沒接（實測）→ valid；說 HTTPError 沒被接 → invalid

## v05:probe:3:5 ｜ `sandbox/release_notes.py:58` ｜ 候選：無

**subprocess 未使用 with 管理資源**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`subprocess.run` 內部會建立 pipe 並等待子程序，雖然通常會自動清理，但若發生例外（如 `CalledProcessError`）可能導致資源洩漏。建議使用 `with subprocess.Popen(...) as proc:` 或確保在 `finally` 中關閉。

evidence：diff 中直接呼叫 `subprocess.run` 而未使用 `with` 或 `try/finally`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## v05:probe:4:2 ｜ `sandbox/release_notes.py:41` ｜ 候選：PR-X1, PR-B3(unless)

**NOTES_MAX 未限制下限，負數或零會造成非預期行為**

existing_code:
```
try:
        return int(raw)
    except ValueError:
```

body：`max_items()` 將環境變數 NOTES_MAX 轉為整數後直接回傳，沒有檢查是否為正數。若使用者設定 NOTES_MAX=0 或負數，`commits[: max_items()]` 會得到空列表或全部元素（負索引切片），導致 release notes 內容不正確。

建議：在轉換後檢查數值是否大於 0，否則回傳預設值或記錄警告。

evidence：diff 中 `max_items()` 函式只處理了 ValueError，未對轉換後的整數做範圍檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## v05:probe:4:4 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

**設定檔 JSON 型別未驗證，可能導致 AttributeError**

existing_code:
```
with open(path, encoding="utf-8") as fh:
            return json.load(fh)
```

body：`load_config` 回傳 `json.load` 的結果，但未檢查其是否為 dict。若 `.release-notes.json` 內容是陣列或字串，後續 `cfg.get('title', ...)` 會拋出 AttributeError，導致程式崩潰。

建議：在 `load_config` 中檢查回傳值是否為 dict，若不是則拋出錯誤或回傳空 dict。

evidence：diff 中 `load_config` 直接回傳 `json.load` 的結果，未做型別檢查。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## v05:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 清單只有一個元素時會 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`list_tags` 回傳符合 `TAG_RE` 的 tag 清單。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 在清單中且前面還有更早的 tag。如果 repo 只有一個符合條件的 tag（例如剛建立第一個 release），`tags.index(tag)` 會是 0，`tags[-1]` 會取到最後一個元素（也就是自己），導致 `prev` 等於 `tag`，`git log prev..tag` 會是空範圍，產生錯誤的結果。

**失敗情境**：在只有一個 tag 的 repo 上執行，程式會將該 tag 同時當作 prev 和 tag，導致 commit 清單為空，或產生非預期的輸出。

**建議**：在取 `prev` 前檢查 `tags.index(tag) > 0`，否則回報錯誤或改用其他方式決定起始點。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未檢查邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## v05:probe:5:3 ｜ `sandbox/release_notes.py:34` ｜ 候選：無

**NOTES_MAX 未處理負數或零**

existing_code:
```
try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX
```

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為正數。如果設定為 `0` 或負數，`commits[: max_items()]` 會產生空清單或錯誤的切片，導致輸出內容不完整或程式出錯。

**失敗情境**：使用者誤設 `NOTES_MAX=0`，程式會產生空的 release notes，但仍回報成功。

**建議**：在轉換後檢查數值是否大於 0，否則使用預設值或回報錯誤。

evidence：diff 中 `max_items` 只處理了 ValueError，未檢查數值範圍。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## v05:python:2:4 ｜ `sandbox/pr_stats.py:69` ｜ 自動：PY-A6 → valid

**export_csv 未使用 with 管理檔案，可能洩漏資源**

existing_code:
```
f = open(path, "w")
    f.write("author,latency,kind\n")
    for r in rows:
        f.write(f"{r['author']},{r['latency']},{r['kind']}\n")
    f.close()
```

body：`export_csv` 直接使用 `open` 和 `close`，若寫入過程中發生例外（例如磁碟滿），檔案不會被關閉，造成資源洩漏。建議改用 `with open(...) as f:` 確保檔案正確關閉。

evidence：diff 第 49-53 行顯示手動開啟和關閉檔案，沒有使用 `with`。

## v05:python:4:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

**archive 使用 shell=True 且參數未驗證，存在指令注入風險**

existing_code:
```
subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)
```

body：`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。這些參數來自命令列輸入（`repo` 來自 `sys.argv[1]`，`path` 來自 `out` 變數，而 `out` 包含 `repo`），攻擊者可注入任意 shell 指令。例如 `repo` 設為 `foo; rm -rf /` 會導致嚴重後果。建議改用參數列表形式（`subprocess.run([...])`）並避免 `shell=True`，或對輸入進行嚴格驗證。

evidence：diff 第 68 行顯示 `shell=True` 且指令字串由外部輸入拼接。

## v05:shell:1:1 ｜ `sandbox/repo_sync.sh:47` ｜ 自動：SH-S1 → valid

**SQL 注入風險：repo 名稱與 branch 未經跳脫直接插入 SQL 語句**

existing_code:
```
sqlite3 "$DB" "INSERT INTO runs VALUES('$name', '$BRANCH', $ahead, datetime('now'))"
```

body：`$name` 與 `$BRANCH` 直接拼接進 SQL 字串，若 repo 目錄名稱或 branch 名稱包含單引號，將導致 SQL 語法錯誤或注入攻擊。例如 repo 名稱為 `x'; DROP TABLE runs; --` 時，會執行惡意 SQL。

建議改用參數化查詢，例如：
```bash
sqlite3 "$DB" "INSERT INTO runs VALUES(?, ?, ?, datetime('now'))" "$name" "$BRANCH" "$ahead"
```

evidence：第 42 行直接將變數插入 SQL 字串，未做任何跳脫或參數化。

## v05:shell:2:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

**命令注入：eval 執行 hook 時未安全處理參數**

existing_code:
```
eval "$hook $repo"
```

body：`run_hook` 使用 `eval "$hook $repo"`，其中 `$repo` 是 repo 名稱（來自目錄名稱）。若 repo 名稱包含 shell 特殊字元（如 `; rm -rf ~`），可能導致任意命令執行。建議改用陣列方式執行：`"$hook" "$repo"`，避免 eval。

evidence：第 53 行使用 eval 執行字串，且參數未經跳脫。

## v05:shell:3:3 ｜ `sandbox/repo_sync.sh:34` ｜ 自動：SH-K-gitfail → valid

**錯誤處理不足：git 指令失敗仍繼續執行，可能導致錯誤資料寫入**

existing_code:
```
git fetch origin --prune 2>>"$LOG"

  # branch 已在開頭驗過格式，可以直接用
  git checkout $BRANCH 2>>"$LOG"
  git merge --ff-only "origin/$BRANCH" 2>>"$LOG"
```

body：`sync_one` 中所有 `git` 指令的 stderr 都被重導到 log，但 exit code 未檢查。若 `git fetch` 失敗（例如網路問題），後續 `git checkout` 或 `git merge` 可能基於過時的遠端分支執行，甚至 `git merge` 失敗後仍繼續計算 `ahead` 並寫入資料庫，造成報表數據不正確。

**失敗情境**：假設 `git fetch` 因網路中斷失敗，但本地已有舊的 `origin/$BRANCH`，`git merge --ff-only` 可能成功合併到舊狀態，而 `ahead` 計算的是與舊遠端的差異，導致回報的領先 commit 數不準確。

**建議**：在每個 git 指令後檢查 exit code，失敗時記錄錯誤並跳過該 repo，例如：
```bash
git fetch origin --prune 2>>"$LOG" || { echo "[$name] fetch failed" >> "$LOG"; return 1; }
```

evidence：diff 第 34-37 行：連續執行 git 指令，未檢查 exit code。

## v05:shell:4:6 ｜ `sandbox/repo_sync.sh:87` ｜ 自動：SH-S7 → valid

**使用 ls 解析目錄列表可能因檔名包含換行或空格而失敗**

existing_code:
```
for d in $(ls "$ROOT"); do
```

body：`for d in $(ls "$ROOT")` 若目錄名稱包含空格或換行，會導致迴圈變數被錯誤分割。建議改用 `for d in "$ROOT"/*/` 或 `find` 搭配 `-print0`。

evidence：diff 第 82 行：`for d in $(ls "$ROOT"); do`

## v05:probe:1:4 ｜ `sandbox/release_notes.py:91` ｜ 自動：PR-B11 → invalid

**webhook URL 未驗證 scheme，可能被用於 SSRF**

existing_code:
```
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
```

body：`NOTES_WEBHOOK` 環境變數由使用者控制，但程式直接將它傳給 `urllib.request.urlopen`。如果攻擊者能影響環境變數（例如 CI 設定），可以指定 `file:///etc/passwd` 或內網位址，造成資訊洩漏或 SSRF。

建議：檢查 URL 的 scheme 必須是 `https`（或至少 `http`），並考慮限制目標網域。

evidence：diff 中 `post` 函式直接使用 `url` 建立 Request，沒有驗證 scheme。

## v05:probe:5:1 ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 執行失敗時未檢查，導致靜默失敗**

existing_code:
```
proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
```

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `repo` 路徑不存在、不是 git repository，或 `git log` 因其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空 list。呼叫端 `main` 會將空 list 解讀為「沒有新 commit」並回傳 0（成功），但實際上根本沒有取得任何資料。

**失敗情境**：使用者提供錯誤的 repo 路徑，程式會印出「之間沒有新 commit」並以 exit code 0 結束，讓 CI 或排程誤以為成功。

**建議**：在 `subprocess.run` 加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

evidence：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。
