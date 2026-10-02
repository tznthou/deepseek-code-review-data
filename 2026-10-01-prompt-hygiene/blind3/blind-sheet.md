# 殘差盲標單（自動標記；同意就不用寫，有異議才寫進 blind-labels.csv）

## R001 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能導致後續處理錯誤資料**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身出錯而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，然後 `main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R002 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**max_items 未驗證範圍**

body：`NOTES_MAX` 環境變數轉成整數後沒有檢查是否為負數或過大。負數會導致 `commits[: max_items()]` 切片行為異常（例如 `commits[:-1]` 會排除最後一個元素），過大的值可能導致記憶體問題。建議加上範圍檢查，例如限制在 1 到某個合理上限。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R003 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 來解析。建議加上 `check=True`，或至少檢查 `proc.returncode != 0` 時記錄錯誤並回傳空列表。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R004 ｜ 標的 probe ｜ `sandbox/release_notes.py:38` ｜ 自動：PR-X1 → valid

**`max_items()` 未處理負數或零，可能導致空白公告**

body：`max_items()` 只處理了非整數輸入，但若 `NOTES_MAX` 設為負數或零，`commits[: max_items()]` 會得到空列表，導致 `render` 產生只有標題的公告，並可能貼出空白內容。

建議：在 `max_items()` 中檢查數值是否大於 0，否則回傳預設值或記錄警告。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R005 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能誤判為無 commit**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list，導致主流程印出「之間沒有新 commit」並回傳 0，但實際上是錯誤。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或記錄錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R006 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 git log 的失敗回傳碼**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，後續 `main` 中的 `commits[0][0]` 會拋出 `IndexError`，導致程式崩潰。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R007 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能導致後續崩潰**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串，函式回傳空列表。接著在 `main` 中 `commits[0]` 會拋出 `IndexError`，程式以 traceback 結束。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並回報錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R008 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**NOTES_MAX 未限制為正整數，負值或零會造成切片異常**

body：`max_items` 將環境變數 NOTES_MAX 轉為整數後直接回傳，未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空 list 或錯誤切片（負數切片會從尾端取，可能導致非預期行為）。建議驗證數值必須大於 0，否則使用預設值。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R009 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**子程序失敗未檢查，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑無效、權限不足），`proc.stdout` 可能為空字串，但函式仍回傳空 list，後續 `main` 中 `commits[0][0]` 會拋出 `IndexError`。建議加上 `check=True` 或檢查 `returncode`，並在失敗時記錄錯誤並回傳非零狀態。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R010 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**NOTES_MAX 為負數或零時未處理**

body：`max_items` 函式將 `NOTES_MAX` 轉為整數，但未檢查是否為正數。如果設定為負數或零，`commits[: max_items()]` 會產生空列表或錯誤切片，導致公告內容不正確。建議限制最小值為 1 或使用預設值。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R011 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能導致後續崩潰**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list。接著 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式以 traceback 結束，使用者只看到堆疊而沒有明確錯誤訊息。

建議：加上 `check=True` 或檢查 `proc.returncode != 0` 時記錄錯誤並回傳空 list 或拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R012 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 執行失敗時未檢查，導致靜默產生空結果**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，且沒有檢查 `proc.returncode`。如果 `repo` 路徑不存在、不是 git repo，或 `prev..tag` 範圍無效，`git log` 會以非零狀態碼結束，但程式會繼續執行，將 `proc.stdout`（可能是空字串或錯誤訊息）解析成空的 commit 清單。這會讓 `main` 誤判為「沒有新 commit」而回傳 0（成功），實際上根本沒有產生任何 release notes。

**失敗情境**：使用者提供錯誤的 repo 路徑，或 tag 名稱拼錯，程式會靜默地回報成功，但沒有貼出任何公告。

**建議**：在 `subprocess.run` 中加入 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R013 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**子程序失敗時未檢查回傳碼，可能導致後續處理錯誤資料**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空列表，呼叫端會誤以為沒有 commit 而正常結束（回傳 0）。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R014 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**`tags.index(tag)` 在 tag 不存在時拋出 `ValueError`，導致程式崩潰**

body：`main` 中先檢查 `if tag not in tags`，但 `tags` 是 `list_tags` 回傳的列表，而 `list_tags` 只回傳符合 `TAG_RE` 的 tag。如果使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為真，程式會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，如果 `list_tags` 因為某些原因回傳的列表不包含該 tag（例如 tag 名稱大小寫不同），則 `tags.index(tag)` 會拋出 `ValueError`。建議使用更安全的方式取得前一個 tag，例如 `prev = tags[tags.index(tag) - 1] if tag in tags else None`，或直接使用 `try/except` 處理。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## R015 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 執行失敗時未檢查回傳碼，可能誤判為沒有 commit**

body：`commits_between` 使用 `subprocess.run` 執行 `git log`，但沒有設定 `check=True`，也沒有檢查 `proc.returncode`。當 `repo` 路徑無效、git 指令不存在、或 repository 損毀時，`git log` 會以非零狀態結束，但 `proc.stdout` 可能是空的，導致函式回傳空 list。呼叫端 `main` 看到空 list 會印出「沒有新 commit」並回傳 0（成功），但實際上根本沒有取得任何資料。

**失敗情境**：使用者提供錯誤的 repo 路徑，或 repo 尚未初始化，程式會回報成功但沒有產生任何 release notes。

**建議**：在 `subprocess.run` 加上 `check=True`，讓失敗時拋出 `CalledProcessError`，或在函式內檢查 `proc.returncode != 0` 並記錄錯誤後回傳空 list 或拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R016 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`commits_between` 未檢查子程序失敗，可能回傳空列表並誤導流程**

body：`subprocess.run` 沒有設定 `check=True`，當 `git log` 失敗（例如 repo 路徑無效、git 不在 PATH、或 `prev..tag` 不是有效範圍）時，`proc.returncode` 非零但程式不會拋出例外。`proc.stdout` 可能為空字串，導致函式回傳空列表，`main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並記錄錯誤後回傳非零。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R017 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查退出碼，可能貼出空公告**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。當 `repo` 路徑不存在、不是 git repo，或 `prev`/`tag` 不存在時，`git log` 會以非零退出碼結束，但程式會繼續執行，`proc.stdout` 會是空字串，最後 `commits` 為空 list。接著 `main` 會因為 `if not commits` 而直接回傳 0，不會貼出任何東西，但也不會回報錯誤，使用者會以為成功。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R018 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**只有一個 tag 時會取到錯誤的 prev tag**

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是列表第一個元素時，`tags.index(tag)` 為 0，`-1` 會取到最後一個 tag，而不是沒有前一個 tag。這會導致 release notes 包含從最後一個 tag 到目前 tag 的所有 commit，內容錯誤。建議檢查 `tags.index(tag) == 0` 並處理（例如回報錯誤或使用 repo 初始 commit）。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## R019 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能導致誤報成功**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損壞、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list。後續 `main` 會因 `commits` 為空而回傳 0（成功），但實際上沒有產生任何公告。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R020 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**`max_items()` 未處理負數或過大的值**

body：`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為負數或過大。如果設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，意外排除最後一個 commit；如果設定為極大值，可能導致記憶體問題（雖然 commit 數量通常有限）。

建議：限制範圍，例如 `max(0, min(value, 1000))`。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R021 ｜ 標的 probe ｜ `sandbox/release_notes.py:43` ｜ 自動：PR-X1 → valid

**`max_items` 未限制 `NOTES_MAX` 的範圍，可能導致記憶體耗盡或負數切片**

body：`max_items` 直接將環境變數轉為整數，沒有檢查是否為負數或過大。若 `NOTES_MAX` 設為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，意外排除最後 n 筆；若設為極大值，可能嘗試處理大量 commit 造成記憶體壓力。建議加上範圍檢查（例如 1 到某個合理上限）。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R022 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 git log 子程序的回傳碼**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致後續流程誤以為沒有 commit 而正常結束（回傳 0），但實際上根本沒有產生 release notes。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R023 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 `git log` 執行結果，可能導致後續處理空輸出或錯誤輸出**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空字串，函式會回傳空列表，導致 `main` 誤判為「沒有新 commit」而回傳 0，或後續 `commits[0][0]` 拋出 `IndexError`。建議加上 `check=True` 或檢查 `proc.returncode`，並在失敗時記錄錯誤並回傳非零狀態。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R024 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空 list。接著在 `main` 中 `commits[0][0]` 會拋出 `IndexError`，程式直接 crash。建議加上 `check=True`，或在呼叫後檢查 `proc.returncode` 並處理錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R025 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**commits_between 未檢查 git log 的失敗**

body：`subprocess.run` 沒有設定 `check=True`，如果 `git log` 失敗（例如 repo 路徑不正確、git 指令不存在），`proc.returncode` 非零但程式不會拋出例外，而是繼續處理空的 `stdout`，導致後續邏輯誤判為沒有 commit。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R026 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續處理空輸出**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑錯誤、權限不足），`proc.stdout` 可能為空字串，函式會回傳空 list，後續 `main` 會印出「沒有新 commit」並回傳 0，但實際上並未成功取得 commit 清單。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R027 ｜ 標的 probe ｜ `sandbox/release_notes.py:35` ｜ 自動：PR-X1 → valid

**max_items 未限制負數或過大值**

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未檢查範圍。若設定為負數，`commits[: max_items()]` 會回傳空 list，導致後續 `commits[0][0]` 出錯；若設定為極大值，可能造成記憶體壓力。建議限制在合理範圍（例如 1 到 1000）。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R028 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 指令失敗時未檢查回傳碼**

body：`commits_between` 使用 `subprocess.run` 但未設定 `check=True`，也未檢查 `returncode`。若 git 執行失敗，`proc.stdout` 可能為空，導致後續處理錯誤。建議加上 `check=True` 或明確檢查 `returncode`。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R029 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能靜默產生空列表**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身出錯而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致 `main` 誤以為「沒有新 commit」而回傳 0，實際上根本沒有成功取得任何資料。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R030 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時沒有 `check=True`，若 `git log` 因 repo 損毀或權限問題失敗，`proc.stdout` 會是空字串，`commits` 會是空 list。接著在 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式直接 crash。建議加上 `check=True` 或檢查 `proc.returncode` 並回報錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R031 ｜ 標的 probe ｜ `sandbox/release_notes.py:38` ｜ 自動：PR-X1 → valid

**NOTES_MAX 未處理負數或零值**

body：`max_items` 將環境變數轉為整數後直接回傳，若設定為負數或 0，`commits[: max_items()]` 會得到空列表或全部 commit（負數切片會從尾端取），可能造成非預期行為。建議限制最小值為 1 或驗證範圍。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R032 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**max_items 未驗證負數或零值**

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空列表或意外結果。建議驗證值必須大於 0，否則回退到預設值。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R033 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**當 tag 是第一個版本時，prev 會取到錯誤的 tag**

body：`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，會取到 `tags[-1]`（最後一個 tag），而不是沒有前一個版本。這會導致 `commits_between` 使用錯誤的範圍，產生不正確的 release notes。

建議：檢查 `tags.index(tag) == 0` 的情況，並處理沒有前一個 tag 的邏輯（例如從 repo 初始 commit 開始）。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## R034 ｜ 標的 probe ｜ `sandbox/release_notes.py:39` ｜ 自動：PR-X1 → valid

**NOTES_MAX 設為負數或零時沒有防護**

body：`max_items` 直接將環境變數轉為整數，沒有檢查是否為正數。如果 `NOTES_MAX` 設為負數，`commits[: max_items()]` 會取到空列表或部分列表；設為 0 也會得到空列表。建議限制最小值為 1，或在使用前檢查。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R035 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查退出碼，錯誤訊息會被當成 commit 內容**

body：`subprocess.run` 沒有設定 `check=True`，當 `git log` 失敗時（例如 repo 路徑不存在、tag 不存在、或 git 本身出錯），`proc.returncode` 非零，但程式碼仍會繼續處理 `proc.stdout`。此時 stdout 可能為空，但 stderr 的錯誤訊息不會被讀取，導致後續邏輯誤以為沒有 commit 或產生錯誤的公告。

**失敗情境**：使用者執行 `python3 release_notes.py /nonexistent v1.2.3`，`git log` 會輸出錯誤到 stderr 並回傳非零退出碼，但 `commits_between` 會回傳空列表，`main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。

**建議**：在 `subprocess.run` 加上 `check=True`，讓失敗時拋出 `CalledProcessError`，由呼叫端處理或直接讓程式以非零碼結束。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R036 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致誤判為無 commit**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空 list，而 `main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R037 ｜ 標的 probe ｜ `sandbox/release_notes.py:30` ｜ 自動：PR-B2 → invalid

**`load_config` 未限制設定檔大小，可能讀入超大檔案**

body：`load_config` 直接 `json.load(fh)`，若 `.release-notes.json` 被意外放入超大檔案，可能耗盡記憶體。建議在讀取前檢查檔案大小或限制讀取位元組數。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## R038 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**max_items() 未處理負數或零，可能造成切片行為異常**

body：`max_items()` 將環境變數 `NOTES_MAX` 轉成整數，但沒有檢查是否為正數。如果設定為負數或零，`commits[: max_items()]` 會得到空 list 或意外的結果。建議加上檢查，若小於 1 則使用預設值或報錯。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R039 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 `git log` 子程序的回傳碼**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致後續流程誤判為「沒有新 commit」而正常結束，或產生不完整的 release notes。建議加上 `check=True` 或明確檢查 `returncode`，並在失敗時拋出例外或記錄錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R040 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續處理錯誤**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑錯誤、權限不足），`proc.stdout` 可能為空字串，函式會回傳空 list，導致後續 `commits[0]` 拋出 IndexError，或產生不完整的 release notes。建議加上 `check=True` 或檢查 returncode 並拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R041 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成正常結果**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或檢查 `proc.returncode != 0` 並拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R042 ｜ 標的 probe ｜ `sandbox/release_notes.py:30` ｜ 自動：PR-B2 → invalid

**設定檔讀取未限制大小，可能造成記憶體耗盡**

body：`load_config` 直接 `json.load(fh)`，若 `.release-notes.json` 非常大（例如誤放大型檔案），可能耗盡記憶體。建議限制檔案大小或使用串流解析。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## R043 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**未檢查 git log 的 return code，可能把錯誤輸出當成正常結果**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R044 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查退出碼，可能靜默產生空結果**

body：`subprocess.run` 沒有設定 `check=True`，當 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗時，`proc.returncode` 非零，但程式碼完全沒有檢查，會繼續處理空的 `stdout`，最後回報成功並可能貼出空白公告。

建議：加上 `check=True`，或在執行後檢查 `proc.returncode != 0` 並記錄錯誤後返回非零退出碼。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R045 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，`commits` 會是空 list。接著在 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式直接 crash。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並記錄錯誤後回傳空 list 或拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R046 ｜ 標的 probe ｜ `sandbox/release_notes.py:45` ｜ 自動：PR-X1 → valid

**NOTES_MAX 未限制範圍，負值或超大值可能造成異常**

body：`max_items` 只檢查是否能轉成整數，沒有檢查範圍。如果使用者設定 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個以外的所有 commit，可能不是預期行為；如果設定超大值（例如 10^9），雖然切片本身不會出錯，但後續 render 可能產生極大的字串，造成記憶體壓力。建議加上範圍檢查（例如 1 到某個合理上限）。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R047 ｜ 標的 probe ｜ `sandbox/release_notes.py:42` ｜ 自動：PR-X1 → valid

**max_items 未處理負數或零**

body：`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空列表或意外結果（負數切片會從尾端取元素），可能導致公告內容不正確。建議驗證數值必須大於 0，否則使用預設值。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R048 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**`max_items` 未處理負數或零，可能導致非預期行為**

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會得到空 list 或全部 commit（負數切片會從尾端取），可能造成非預期結果。

**失敗情境**：使用者誤設 `NOTES_MAX=-1`，程式會將所有 commit 納入（因為 `commits[:-1]` 取到倒數第二個），而不是限制數量。

**建議**：在 `max_items` 中檢查數值是否大於 0，若否則使用預設值並記錄警告。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R049 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**`git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果**

body：`subprocess.run` 沒有設定 `check=True`，當 `git log` 因為 repo 路徑錯誤、tag 不存在或權限問題失敗時，`proc.returncode` 非零，但程式仍會繼續解析 `proc.stdout`（可能是空字串或錯誤訊息），導致後續流程在錯誤的基礎上執行。建議加上 `check=True`，或明確檢查 `proc.returncode` 並在非零時拋出例外或回傳空列表。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R050 ｜ 標的 probe ｜ `sandbox/release_notes.py:34` ｜ 自動：PR-B2 → invalid

**load_config 的 JSON 解析錯誤處理可能造成程式提前終止**

body：`load_config` 在 JSON 解析失敗時直接 `raise SystemExit`，這會讓整個程式終止，即使設定檔是選配的。若設定檔損壞，使用者可能無法產生 release notes。建議改為記錄警告並回傳空字典，或讓呼叫端決定是否終止。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）

## R051 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.returncode` 非零但程式不會拋出例外，`proc.stdout` 可能是空字串。接著 `main` 中 `commits[0][0]` 會因為 `commits` 為空而拋出 `IndexError`，且沒有提供有用的錯誤訊息。

建議：在 `subprocess.run` 加上 `check=True`，或在取得 `commits` 後檢查是否為空並回傳明確錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R052 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**NOTES_MAX 可設為負數導致切片錯誤**

body：`max_items` 直接將環境變數轉為整數，未驗證是否為正數。若設定為負數，`commits[: max_items()]` 會產生錯誤切片（例如 `[:-1]` 會排除最後一個元素）。建議檢查數值範圍，例如 `if n < 1: return DEFAULT_MAX`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R053 ｜ 標的 probe ｜ `sandbox/release_notes.py:36` ｜ 自動：PR-X1 → valid

**`max_items` 未處理負數或零，可能導致公告內容為空**

body：`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。如果設定為 `0` 或負數，`commits[: max_items()]` 會得到空列表或錯誤切片，導致公告內容為空或行為異常。建議加上驗證，例如 `if value < 1: return DEFAULT_MAX`。

- 規則提示 PR-B2：設定檔是選配（註解寫明）；壞 JSON 以明確訊息結束（實測）
- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R054 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**子程序失敗未檢查，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑無效、權限不足或 git 本身錯誤而失敗，`proc.stdout` 可能為空字串，後續 `commits[0][0]` 會拋出 `IndexError`，程式直接崩潰且無明確錯誤訊息。建議加上 `check=True` 或檢查 `returncode`，並在失敗時記錄錯誤並回傳非零 exit code。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R055 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能誤判為無 commit**

body：`commits_between` 呼叫 `subprocess.run` 時沒有 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.returncode` 非零但程式不會拋出例外，`proc.stdout` 可能為空，導致函式回傳空列表。呼叫端 `main` 看到空列表會印出「沒有新 commit」並回傳 0，但實際上可能是錯誤。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時記錄錯誤並回傳非零。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R056 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空字串，`commits` 會是空 list。在 `main` 中，`latest = commits[0][0]` 會因此拋出 `IndexError`，程式直接 crash。建議在 `subprocess.run` 加上 `check=True`，或檢查 `proc.returncode != 0` 時記錄錯誤並回傳空 list 或拋出例外。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R057 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查 returncode，可能產生錯誤結果**

body：`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空清單，導致後續流程誤以為沒有 commit 而提前結束，或產生不完整的 release notes。

建議：加上 `check=True`，或明確檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R058 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**子程序失敗未檢查，可能導致後續 IndexError**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑無效、tag 不存在或權限問題失敗，`proc.stdout` 可能為空字串，後續 `commits[0][0]` 會拋出 `IndexError`。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）

## R059 ｜ 標的 probe ｜ `sandbox/release_notes.py:42` ｜ 自動：PR-X1 → valid

**`max_items` 未處理負數或零，可能產生空公告**

body：`max_items` 直接將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或 0，`commits[: max_items()]` 會得到空 list，導致 `group` 回傳空 sections，`render` 只輸出標題，最後仍會呼叫 `post` 貼出無內容的公告。建議限制最小值為 1，或對非法值回退到預設值。

- 規則提示 PR-B3：int() 包在 try/except ValueError，警告後用預設值（實測）
- 規則提示 PR-X1：NOTES_MAX=-1 靜默丟掉最舊一筆、0 只剩標題（實測）

## R060 ｜ 標的 probe ｜ `sandbox/release_notes.py:118` ｜ 自動：PR-A1 → valid

**`tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError`**

body：`main` 中先檢查 `if tag not in tags`，但 `tags` 來自 `list_tags`，該函式只回傳符合 `TAG_RE` 的 tag。如果使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為真，程式會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，如果 `list_tags` 因為某種原因回傳的列表不包含該 tag（例如 tag 名稱大小寫不同），`tags.index(tag)` 仍可能拋出 `ValueError`。建議使用 `try/except` 或先取得 index 再檢查。

- 規則提示 PR-A1：第一個 tag 的 index 0 - 1 = -1，prev 變成最後一個 tag，範圍為空、靜默回 0（實測）
- 規則提示 PR-B9：第 120 行已守住空列表（實測）

## R061 ｜ 標的 probe ｜ `sandbox/release_notes.py:58` ｜ 自動：PR-X2 → valid

**git log 失敗時未檢查回傳碼，可能導致後續處理錯誤資料**

body：`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空或包含錯誤訊息，函式仍會回傳空清單或解析出錯誤的 commit 資料。建議加上 `check=True` 或明確檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤。

- 規則提示 PR-B1：subprocess 用 list 參數、沒有 shell；tag 先過 regex；repo 是操作者自己給的路徑
- 規則提示 PR-X2：git log 失敗被當成沒有 commit、靜默回 0（實測）
