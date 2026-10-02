<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，允許在 AOF 檔案中間發生格式錯誤時自動截斷損壞部分。主要風險在於自動截斷可能導致資料遺失，且程式碼中對 valid_up_to 的處理、truncate 失敗時的回退、以及與既有 aof-load-truncated 的互動需要更謹慎的錯誤處理與測試。最關鍵的問題是當 truncate 失敗時，程式碼仍可能繼續執行並回報成功，造成資料不一致。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1728` | truncate 失敗時仍可能回報成功 | 0.95 |
| ⚠️ | Major | `src/aof.c:1725` | valid_up_to 可能為 -1 導致計算錯誤 | 0.85 |
| ⚠️ | Major | `src/aof.c:1734` | lseek 失敗時未處理 | 0.80 |
| ⚠️ | Major | `src/aof.c:1661` | aof-load-broken 與 aof-load-truncated 同時啟用時可能重複處理 | 0.80 |
| ⚠️ | Major | `src/aof.c:1830` | AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理 | 0.75 |
| 🔸 | Minor | `src/server.h:15` | 標頭檔 include guard 變更可能造成相容性問題 | 0.70 |
| 🔸 | Minor | `tests/integration/aof.tcl:707` | 測試中未清理可能殘留的 AOF 檔案 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1728</code> truncate 失敗時仍可能回報成功</summary>

在 `fmterr` 處理中，當 `truncate(aof_filepath, valid_up_to)` 失敗時，程式碼僅記錄警告，但未設定 `ret` 為失敗，也未跳轉到錯誤處理。接著程式碼會繼續執行，可能到達 `loaded_ok` 標籤並回傳成功，導致伺服器在 AOF 檔案未正確截斷的情況下啟動，可能載入損壞的資料或造成後續寫入問題。

建議：在 truncate 失敗時，設定 `ret = AOF_FAILED` 並跳轉到 `cleanup`，或直接 `goto cleanup`。

**判斷依據**：diff 中新增的程式碼片段，truncate 失敗時僅記錄警告，沒有設定 ret 或跳轉，後續可能執行到 `goto loaded_ok`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1725</code> valid_up_to 可能為 -1 導致計算錯誤</summary>

在 `fmterr` 處理中，程式碼檢查 `valid_up_to == -1` 並記錄警告，但之後仍可能使用 `valid_up_to` 進行計算（例如 `sb.st_size - valid_up_to`）。如果 `valid_up_to` 為 -1，計算結果會是 `sb.st_size + 1`，可能導致錯誤的判斷或 truncate 到錯誤的位置。

建議：在 `valid_up_to == -1` 時直接跳轉到錯誤處理，不要繼續執行。

**判斷依據**：diff 中新增的程式碼片段，valid_up_to 為 -1 時僅記錄警告，後續仍可能使用該值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1734</code> lseek 失敗時未處理</summary>

在 truncate 成功後，程式碼嘗試將 `server.aof_fd` 的檔案偏移移到結尾，但若 `lseek` 失敗，僅記錄警告，未設定錯誤狀態。這可能導致後續寫入 AOF 時從錯誤的位置開始，造成檔案損壞。

建議：在 lseek 失敗時，設定 `ret = AOF_FAILED` 並跳轉到錯誤處理。

**判斷依據**：diff 中新增的程式碼片段，lseek 失敗時僅記錄警告，未設定 ret 或跳轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1661</code> aof-load-broken 與 aof-load-truncated 同時啟用時可能重複處理</summary>

在 `loadSingleAppendOnlyFile` 中，原本的 `aof_load_truncated` 處理會將 `valid_up_to` 更新為檔案結尾，而新的 `aof_load_broken` 處理也會在格式錯誤時嘗試截斷。如果兩者同時啟用，且檔案同時有截斷和格式錯誤，可能導致 `valid_up_to` 被錯誤更新，或重複截斷。

建議：明確兩者的優先順序，或避免同時啟用。

**判斷依據**：diff 中修改的這一行，將條件從 `aof_load_truncated` 改為 `aof_load_truncated || aof_load_broken`，可能導致行為重疊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1830</code> AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理</summary>

在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且不是最後一個檔案時，程式碼將其視為致命錯誤並設定 `ret = AOF_FAILED`，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 會導致即使已經設定為 `AOF_FAILED`，仍會進入 `cleanup`。這可能導致錯誤訊息不一致或資源未正確釋放。

建議：在設定 `ret = AOF_FAILED` 後，直接跳轉到 `cleanup`，避免後續判斷。

**判斷依據**：diff 中修改的程式碼片段，新增了 AOF_BROKEN_RECOVERED 的處理，但可能導致重複判斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.h:15</code> 標頭檔 include guard 變更可能造成相容性問題</summary>

將 `__REDIS_H` 改為 `_REDIS_H` 可能與其他程式碼或第三方庫衝突，因為以底線開頭的巨集名稱是保留給編譯器或標準庫使用的。雖然實際上可能不會有問題，但這是不必要的變更，且可能違反專案慣例。

建議：除非有明確原因，否則不要更改 include guard。

**判斷依據**：diff 中修改的 include guard 名稱。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/integration/aof.tcl:707</code> 測試中未清理可能殘留的 AOF 檔案</summary>

在測試開始時，可能殘留先前測試的 AOF 檔案，導致測試結果不穩定。建議在每個測試案例前明確清理 AOF 目錄。

**判斷依據**：diff 中新增的測試程式碼，未見清理步驟。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6321 (cache hit 6272) ｜ completion tokens 2041 ｜ PR #7</sub>