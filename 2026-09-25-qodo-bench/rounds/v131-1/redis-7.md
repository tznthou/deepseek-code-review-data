<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，允許在 AOF 檔案中間發生格式錯誤時自動截斷損壞部分並繼續載入。主要風險在於自動截斷可能導致資料遺失，且實作中對 valid_up_to 的處理、檔案截斷後的狀態同步、以及與多檔案 AOF 的互動存在潛在問題。最需要先修的是確保 valid_up_to 在格式錯誤時的正確性，以及避免在非最後一個檔案上進行截斷。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/aof.c:1661` | valid_up_to 可能未正確更新，導致截斷位置錯誤 | 0.90 |
| ⚠️ | Major | `src/aof.c:1734` | 截斷後未同步 AOF 檔案描述符的偏移量 | 0.80 |
| ⚠️ | Major | `src/aof.c:1735` | 在非最後一個 AOF 檔案上進行截斷可能導致資料不一致 | 0.80 |
| 🔸 | Minor | `src/aof.c:1724` | 錯誤訊息中使用 %lld 但參數型別為 off_t，可能導致格式不符 | 0.70 |
| 🔸 | Minor | `src/server.h:15` | 變更 include guard 可能導致重複定義 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/aof.c:1661</code> valid_up_to 可能未正確更新，導致截斷位置錯誤</summary>

在 `fmterr` 標籤處，程式碼依賴 `valid_up_to` 來決定截斷位置。然而，`valid_up_to` 只在成功解析命令後更新（在 `if (server.aof_load_truncated || server.aof_load_broken) valid_up_to = ftello(fp);` 中）。如果格式錯誤發生在命令解析中途（例如命令不完整或參數錯誤），`valid_up_to` 可能停留在上一個成功命令的結尾，而不是錯誤發生的位置。這會導致截斷掉比實際損壞更多的資料，甚至可能截斷掉有效的命令。

**失敗情境**：假設 AOF 檔案包含 `SET key value\nINCR counter\nCORRUPT`，其中 `INCR counter` 是完整的，但後面的 `CORRUPT` 導致格式錯誤。如果 `valid_up_to` 在解析 `INCR counter` 後沒有更新（因為錯誤發生在讀取下一條命令時），則截斷位置會在 `INCR counter` 之前，導致 `INCR counter` 被丟棄。

**建議修法**：在進入 `fmterr` 之前，確保 `valid_up_to` 反映最後一次成功讀取的位置。可以考慮在每次成功讀取命令後立即更新 `valid_up_to`，或者在錯誤處理中重新定位到最後一個已知良好的偏移量。

**判斷依據**：diff 中第 1658 行附近的修改將條件從 `server.aof_load_truncated` 改為 `server.aof_load_truncated || server.aof_load_broken`，但 `valid_up_to` 的更新時機不變。在 `fmterr` 處理中直接使用 `valid_up_to` 進行截斷，若 `valid_up_to` 未更新到錯誤點，將導致過度截斷。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1734</code> 截斷後未同步 AOF 檔案描述符的偏移量</summary>

在 `truncate(aof_filepath, valid_up_to)` 成功後，程式碼嘗試使用 `lseek(server.aof_fd, 0, SEEK_END)` 來將檔案描述符的偏移量設定到檔案結尾。然而，`server.aof_fd` 可能不是當前載入的 AOF 檔案的描述符，或者可能尚未開啟。此外，`lseek` 失敗時僅記錄警告，但未將 `ret` 設為錯誤，可能導致後續寫入使用錯誤的偏移量。

**失敗情境**：如果 `server.aof_fd` 指向另一個檔案（例如在載入多個 AOF 檔案時），`lseek` 會影響錯誤的檔案描述符，導致後續寫入到錯誤的位置。

**建議修法**：在截斷後，應使用 `fseek` 或 `ftruncate` 來同步檔案指標，並確保操作的是正確的檔案描述符。若無法確保，應關閉並重新開啟檔案。

**判斷依據**：diff 中新增的程式碼在 `truncate` 後使用 `lseek` 來調整 `server.aof_fd`，但未驗證 `server.aof_fd` 是否對應於 `aof_filepath`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1735</code> 在非最後一個 AOF 檔案上進行截斷可能導致資料不一致</summary>

在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且 `!last_file` 時，程式碼會將 `ret` 設為 `AOF_FAILED` 並記錄錯誤，但此時檔案已經被截斷。這意味著即使載入失敗，AOF 檔案已經被修改，可能導致後續手動修復更加困難。

**失敗情境**：假設有多個 AOF 檔案，第一個檔案損壞且被截斷，但因為不是最後一個檔案而導致載入失敗。此時第一個檔案已被修改，但伺服器並未啟動，使用者需要手動修復，但原始損壞資料已丟失。

**建議修法**：在決定是否截斷之前，應先判斷該檔案是否為最後一個檔案。如果不是，則不應進行截斷，直接回報錯誤。

**判斷依據**：diff 中修改了 `loadAppendOnlyFiles` 的條件，但截斷操作發生在 `loadSingleAppendOnlyFile` 內部，無法得知是否為最後一個檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1724</code> 錯誤訊息中使用 %lld 但參數型別為 off_t，可能導致格式不符</summary>

在 `serverLog` 中使用 `%lld` 格式說明符，但傳入的參數 `(long long)(sb.st_size - valid_up_to)` 和 `(long long)(server.aof_load_broken_max_size)` 已經轉型為 `long long`，因此格式正確。然而，`server.aof_load_broken_max_size` 的型別是 `off_t`，在某些平台上可能是 64 位元，但轉型為 `long long` 是安全的。此處沒有實際問題，但建議保持一致性。

**判斷依據**：diff 中新增的日誌語句使用了 `%lld` 並進行了轉型，但未見明顯錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/server.h:15</code> 變更 include guard 可能導致重複定義</summary>

將 `__REDIS_H` 改為 `_REDIS_H` 可能與其他標頭檔的 include guard 衝突，尤其是以底線開頭的巨集名稱在 C 標準中保留給實作使用。雖然不太可能造成實際問題，但建議避免使用保留名稱。

**判斷依據**：diff 中修改了 include guard，從 `__REDIS_H` 改為 `_REDIS_H`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6321 (cache hit 1408) ｜ completion tokens 1920 ｜ PR #7</sub>