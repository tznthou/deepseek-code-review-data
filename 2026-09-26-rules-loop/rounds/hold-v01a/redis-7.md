<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了 `aof-load-broken` 與 `aof-load-broken-max-size` 設定，讓 Redis 在啟動時若 AOF 檔案中間有格式錯誤，且損壞部分小於指定大小，可以自動截斷並繼續載入。主要風險在於 `loadSingleAppendOnlyFile` 中 `fmterr` 處理路徑的邏輯：`valid_up_to` 可能為 -1 或指向錯誤位置，導致截斷過多或過少；另外 `truncate` 失敗時沒有設定 `ret`，可能讓函式回傳成功但檔案未修復。此外，`server.h` 的 include guard 從 `__REDIS_H` 改成 `_REDIS_H`，違反了專案規範 R03。整體而言，功能方向合理，但錯誤處理與邊界條件需要加強，且必須修正 include guard。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1728` | truncate 失敗時未設定 ret，可能導致函式回傳成功但 AOF 未修復 | 0.90 |
| ⚠️ | Major | `src/server.h:15` | [R03] Include guard 從 __REDIS_H 改成 _REDIS_H，違反專案規範 | 0.95 |
| ⚠️ | Major | `src/aof.c:1725` | valid_up_to 可能為 -1 或指向錯誤位置，導致截斷過多或過少 | 0.80 |
| ⚠️ | Major | `src/aof.c:1734` | 截斷後未更新 AOF 檔案大小或相關狀態，可能導致後續寫入錯誤 | 0.75 |
| 🔸 | Minor | `src/aof.c:1732` | 日誌訊息中使用了錯誤的變數名稱 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1728</code> truncate 失敗時未設定 ret，可能導致函式回傳成功但 AOF 未修復</summary>

在 `fmterr` 處理中，如果 `truncate(aof_filepath, valid_up_to)` 失敗（例如權限不足或檔案系統錯誤），程式只記錄警告，但沒有將 `ret` 設為 `AOF_FAILED`。這會讓函式繼續執行到 `cleanup`，最後回傳 `ret` 的目前值（可能是 `AOF_OK` 或 `AOF_TRUNCATED`），導致 Redis 認為 AOF 載入成功，但實際上檔案仍然損壞。

**失敗情境**：當 AOF 檔案權限為唯讀，或磁碟空間不足導致 truncate 失敗時，Redis 會無視錯誤繼續啟動，之後可能讀到損壞的資料或再次崩潰。

**建議**：在 `truncate` 失敗的分支中，將 `ret` 設為 `AOF_FAILED`，並確保後續流程正確處理。

**判斷依據**：diff 中新增的 `truncate` 錯誤處理分支只記錄 log，沒有修改 `ret`，而函式最後會回傳 `ret`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/server.h:15</code> [R03] Include guard 從 __REDIS_H 改成 _REDIS_H，違反專案規範</summary>

專案規範 R03 要求 header file 的 include guard 必須使用雙底線開頭和結尾（例如 `__REDIS_H`）。這個 PR 將 `__REDIS_H` 改成 `_REDIS_H`，違反了規範。

**建議**：改回 `__REDIS_H`，或使用符合規範的命名。

**判斷依據**：diff 中將 `__REDIS_H` 改為 `_REDIS_H`，而規範 R03 明確要求雙底線。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1725</code> valid_up_to 可能為 -1 或指向錯誤位置，導致截斷過多或過少</summary>

在 `fmterr` 處理中，程式使用 `valid_up_to` 作為截斷位置。但 `valid_up_to` 的初始值為 -1，且只有在成功解析命令後才會更新。如果格式錯誤發生在第一個命令之前，`valid_up_to` 會是 -1，此時 `sb.st_size - valid_up_to` 會變成 `sb.st_size + 1`，可能大於 `aof_load_broken_max_size`，導致無法自動修復。另外，如果 `valid_up_to` 指向的位置不是命令邊界（例如在多命令 AOF 中，某個命令解析到一半失敗），截斷後可能留下不完整的命令，造成後續載入錯誤。

**失敗情境**：AOF 檔案開頭就是損壞資料，且 `aof-load-broken-max-size` 設定大於檔案大小，程式會因為 `valid_up_to == -1` 而拒絕修復，但實際上整個檔案都應該被丟棄。

**建議**：在 `valid_up_to == -1` 時，應將截斷位置設為 0（或直接視為空檔案），並確保截斷位置落在命令邊界上。

**判斷依據**：diff 中新增的 `valid_up_to == -1` 分支只記錄警告，沒有處理截斷，而 `valid_up_to` 的初始值為 -1。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1734</code> 截斷後未更新 AOF 檔案大小或相關狀態，可能導致後續寫入錯誤</summary>

在成功截斷 AOF 檔案後，程式只將檔案描述子 seek 到結尾，但沒有更新 `server.aof_current_size` 或其他記錄 AOF 大小的變數。這可能導致後續 AOF 重寫或寫入時，Redis 認為檔案比實際大，進而產生錯誤或資料不一致。

**失敗情境**：截斷後，Redis 繼續寫入 AOF，但 `server.aof_current_size` 仍保留舊值，導致 AOF 重寫觸發條件判斷錯誤，或寫入位置偏移。

**建議**：截斷後應更新相關的 AOF 大小記錄，或至少確保後續寫入使用正確的檔案偏移。

**判斷依據**：diff 中只處理了檔案描述子的 seek，沒有看到更新 `server.aof_current_size` 的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1732</code> 日誌訊息中使用了錯誤的變數名稱</summary>

在成功恢復的日誌中，程式使用了 `server.aof_load_broken_max_size`，但這個變數在 `server.h` 中定義為 `off_t aof_load_broken_max_size`，而日誌格式字串使用 `%lld`，並將變數強制轉型為 `long long`。這在大多數平台上可能沒問題，但嚴格來說 `off_t` 不一定是 `long long`，可能導致未定義行為或警告。

**建議**：使用 `%lld` 搭配明確的 `(long long)` 轉型，或改用 `%zu` 搭配 `size_t` 轉型。

**判斷依據**：diff 中新增的日誌訊息使用了 `%lld` 和 `(long long)` 轉型，但 `server.aof_load_broken_max_size` 的型別是 `off_t`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7358 (cache hit 6272) ｜ completion tokens 1990 ｜ PR #7</sub>