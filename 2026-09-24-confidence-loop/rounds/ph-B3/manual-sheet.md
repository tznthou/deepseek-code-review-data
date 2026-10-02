# ph-B3 人工標記單（盲標：不含 confidence、severity）

自動 62 筆、人工 28 筆、抽查 7 筆。
結果寫進 labels-manual.csv（id,item,label,reason），會覆蓋自動標記。

# 需要人工判定

## ph-B3:python:1:6 ｜ `sandbox/pr_stats.py:51` ｜ 候選：PY-A5, PY-B2

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

## ph-B3:python:1:8 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

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

## ph-B3:python:2:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-B3:python:2:5 ｜ `sandbox/pr_stats.py:37` ｜ 候選：PY-B1

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

## ph-B3:python:2:6 ｜ `sandbox/pr_stats.py:63` ｜ 候選：無

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

## ph-B3:python:3:1 ｜ `sandbox/pr_stats.py:24` ｜ 候選：PY-A1, PY-K-status

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

## ph-B3:python:3:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-B3:python:4:1 ｜ `sandbox/pr_stats.py:26` ｜ 候選：PY-A1, PY-K-status

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

## ph-B3:python:4:3 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A3

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

## ph-B3:python:4:7 ｜ `sandbox/pr_stats.py:40` ｜ 候選：PY-B1

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

## ph-B3:python:5:1 ｜ `sandbox/pr_stats.py:25` ｜ 候選：PY-A1, PY-K-status

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

## ph-B3:python:5:4 ｜ `sandbox/pr_stats.py:29` ｜ 候選：PY-A2, PY-A4

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

## ph-B3:python:5:6 ｜ `sandbox/pr_stats.py:63` ｜ 候選：無

**classify 使用 startswith("fix") 判斷，可能誤分類**

existing_code:
```
elif pr["title"].startswith("fix"):
```

body：`pr["title"].startswith("fix")` 會將標題開頭為 `fix` 但實際不是修復的 PR（例如 `fixation`）歸類為 `fix`。建議使用更精確的判斷，例如正規表示式或檢查完整單字。

evidence：diff 第 53 行：`startswith("fix")` 過於寬鬆。

- 規則提示 PY-C1：classify 沒有測試：陳述屬實，但要人工確認講的是缺測試
- 規則提示 PY-K-classify：單一 PR 端點一定有這兩個欄位；真正會出事的是 pr=None

## ph-B3:shell:1:4 ｜ `sandbox/repo_sync.sh:41` ｜ 候選：SH-S3(unless)

**ahead 計算可能失敗，導致 SQL 插入空值**

existing_code:
```
ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)
```

body：`ahead=$(git rev-list --count "origin/$BRANCH"..HEAD 2>/dev/null)` 若指令失敗（例如分支不存在），`ahead` 將為空字串。後續 `if [ "$ahead" -gt 0 ]` 會因語法錯誤而失敗，且 SQL 插入時 `$ahead` 為空會導致 SQL 錯誤。建議檢查 `ahead` 是否為數字，失敗時設定為 0 或中止。

evidence：diff 第 36 行，未處理指令失敗。

- 規則提示 SH-S3：[ "" -gt 0 ] 報 integer expected、分支不執行、腳本繼續；說會中止或會當成 0 → invalid（09-21 預登記）
- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B3:shell:2:1 ｜ `sandbox/repo_sync.sh:47` ｜ 候選：SH-S1, SH-C1

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

## ph-B3:shell:2:8 ｜ `sandbox/repo_sync.sh:75` ｜ 候選：無

**summarize 函式在日誌為空時仍輸出訊息**

existing_code:
```
echo "本次同步共 $total 筆紀錄，詳見 $LOG"
```

body：`summarize` 函式中，若 `$LOG` 檔案不存在或為空，`total` 為 0，但仍會輸出「本次同步共 0 筆紀錄，詳見 $LOG」。這可能造成誤導。

建議在 `total` 為 0 時輸出不同訊息或省略。

evidence：diff 第 68 行：未處理 `total` 為 0 的情況。

- 規則提示 SH-C1：零測試：陳述屬實，但要人工確認講的是缺測試

## ph-B3:probe:1:5 ｜ `sandbox/release_notes.py:30` ｜ 候選：PR-B2(unless)

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

## ph-B3:probe:2:3 ｜ `sandbox/release_notes.py:36` ｜ 候選：PR-X1, PR-B3(unless)

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

## ph-B3:probe:2:4 ｜ `sandbox/release_notes.py:91` ｜ 候選：PR-B11, PR-B7(unless)

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

## ph-B3:probe:3:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**tag 清單為空時，prev 會取到最後一個元素而非第一個**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 在 `tags` 為空時，`tags.index(tag)` 會拋出 `ValueError`，但若 `tags` 非空且 `tag` 位於第一個位置，`tags.index(tag) - 1` 會是 -1，取到最後一個 tag，而非前一個版本。這會導致 release notes 範圍錯誤。建議先檢查 `tags.index(tag) > 0`，否則回報錯誤。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未處理邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B3:probe:3:3 ｜ `sandbox/release_notes.py:37` ｜ 候選：PR-X1, PR-B3(unless)

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

## ph-B3:probe:3:5 ｜ `sandbox/release_notes.py:94` ｜ 候選：PR-A2, PR-B7(unless)

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

## ph-B3:probe:4:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：如果使用者指定的 tag 是 `list_tags` 回傳列表中的第一個元素（例如 repo 只有一個 tag，或該 tag 是最早的版本），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式直接崩潰。建議在取 `prev` 前檢查 `tags.index(tag) == 0`，並給出明確錯誤訊息或改用其他方式處理（例如從 repo 初始 commit 開始）。

evidence：diff 第 94 行，直接對 `tags.index(tag) - 1` 取值，未處理 index 為 0 的情況。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B3:probe:4:3 ｜ `sandbox/release_notes.py:43` ｜ 候選：PR-X1, PR-B3(unless)

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

## ph-B3:probe:4:4 ｜ `sandbox/release_notes.py:96` ｜ 候選：PR-A2, PR-X4

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

## ph-B3:probe:5:2 ｜ `sandbox/release_notes.py:118` ｜ 候選：PR-A1, PR-B9(unless)

**`prev` 取得方式在 tag 為第一個版本時會拋出 `IndexError`**

existing_code:
```
prev = tags[tags.index(tag) - 1]
```

body：`prev = tags[tags.index(tag) - 1]` 假設 `tag` 不是 `tags` 中的第一個元素。若使用者指定的是最早的 tag（例如 `v1.0.0`），`tags.index(tag)` 回傳 0，`tags[-1]` 會取到最後一個 tag，導致 `git log` 範圍錯誤，可能產生不正確的 commit 列表或空列表。建議檢查 `tags.index(tag) == 0` 的情況，並提示使用者或改用其他方式取得前一個 tag。

evidence：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 取得前一個 tag，未處理 index 為 0 的邊界。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## ph-B3:probe:5:3 ｜ `sandbox/release_notes.py:43` ｜ 候選：無

**`max_items` 未限制上限，可能導致 payload 過大**

existing_code:
```
return int(raw)
```

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未設定上限。若使用者設定極大值（例如 1000000），`commits[: max_items()]` 會將大量 commit 納入訊息，可能超過 webhook 的 payload 限制或造成記憶體壓力。建議設定合理上限（例如 1000）並在超過時警告。

evidence：diff 中 `max_items` 函式直接回傳 `int(raw)`，未檢查數值範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## ph-B3:probe:5:4 ｜ `sandbox/release_notes.py:31` ｜ 候選：PR-B2(unless)

**`load_config` 未處理 JSON 型別錯誤**

existing_code:
```
return json.load(fh)
```

body：`load_config` 假設 JSON 檔案內容是 dict，但若檔案內容是 list 或字串，`json.load` 會成功回傳非 dict 型別，後續 `cfg.get` 會拋出 `AttributeError`。建議檢查 `isinstance(data, dict)`，若不是則回報錯誤。

evidence：diff 中 `load_config` 直接回傳 `json.load(fh)` 的結果，未驗證型別。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

# 抽查（自動標記，複核後有異議才寫進 labels-manual.csv）

## ph-B3:python:2:2 ｜ `sandbox/pr_stats.py:77` ｜ 自動：PY-A7 → valid

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

## ph-B3:python:4:5 ｜ `sandbox/pr_stats.py:54` ｜ 自動：PY-A5 → valid

**threshold_from_env 的 int(raw) 未處理轉換失敗**

existing_code:
```
return {"days": int(raw)}
```

body：`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為整數，若使用者設定非數字字串（例如 `abc`），會拋出 `ValueError` 導致程式崩潰。

建議：捕捉 `ValueError` 並提供預設值或明確錯誤訊息。

evidence：diff 第 44 行：`int(raw)` 無例外處理。

## ph-B3:shell:1:5 ｜ `sandbox/repo_sync.sh:62` ｜ 自動：SH-S5 → valid

**cleanup_cache 使用 rm -rf 可能誤刪重要檔案**

existing_code:
```
rm -rf "$ROOT"/.cache/*
```

body：`cleanup_cache` 執行 `rm -rf "$ROOT"/.cache/*`。若 `$ROOT` 未正確設定或包含符號連結，可能刪除非預期的檔案。建議檢查 `.cache` 是否為目錄，並避免使用 `*` 萬用字元，或使用更安全的刪除方式。

evidence：diff 第 60 行，使用 rm -rf 與萬用字元。

## ph-B3:shell:2:7 ｜ `sandbox/repo_sync.sh:88` ｜ 自動：SH-K-local → disputed

**local 關鍵字在函式外使用**

existing_code:
```
local target="$ROOT/$d"
```

body：`main` 函式中使用 `local target="$ROOT/$d"`，但 `local` 僅能在函式內使用。雖然在 bash 中可能不會報錯，但這是不良實踐，可能導致變數作用域混淆。

建議移除 `local` 或將該段程式碼放入函式中。

evidence：diff 第 82 行：在 `main` 函式內使用 `local`，但 `main` 本身是函式，此處 `local` 是多餘的。

## ph-B3:shell:3:8 ｜ `sandbox/repo_sync.sh:70` ｜ 自動：SH-B2 → invalid

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

## ph-B3:shell:5:2 ｜ `sandbox/repo_sync.sh:56` ｜ 自動：SH-S2 → valid

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

## ph-B3:probe:1:4 ｜ `sandbox/release_notes.py:39` ｜ 自動：PR-X1 → valid

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
