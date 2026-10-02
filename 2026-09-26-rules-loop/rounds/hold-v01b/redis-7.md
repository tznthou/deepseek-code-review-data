<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，允許在 AOF 檔案中間發生格式錯誤時自動截斷損壞部分以恢復載入。主要風險在於自動截斷可能導致資料遺失，且程式碼中對 valid_up_to 的處理、檔案截斷的時機與錯誤處理路徑需要更嚴謹的驗證。此外，server.h 的 include guard 變更違反了專案規範 R03，應立即修正。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/server.h:15` | [R03] Include guard 命名不符合規範 | 0.99 |
| ⚠️ | Major | `src/aof.c:1725` | valid_up_to 可能為 -1 時仍進行截斷 | 0.80 |
| ⚠️ | Major | `src/aof.c:1728` | truncate 失敗後仍可能繼續執行 | 0.75 |
| ⚠️ | Major | `src/aof.c:1734` | lseek 失敗後仍可能繼續執行 | 0.70 |
| ⚠️ | Major | `src/aof.c:1830` | AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理 | 0.70 |
| ⚠️ | Major | `src/aof.c:1860` | AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理（第二處） | 0.70 |
| 🔸 | Minor | `src/aof.c:1730` | 日誌訊息中 broken size 可能為負數 | 0.60 |
| 🔸 | Minor | `src/aof.c:1735` | 日誌訊息中 broken size 可能為負數（第二處） | 0.50 |
| 🔸 | Minor | `src/config.c:3258` | aof-load-broken-max-size 的範圍可能過大 | 0.50 |
| 🔸 | Minor | `tests/integration/aof.tcl:707` | 測試中未清理可能殘留的 AOF 檔案 | 0.40 |

<details><summary>🛑 <b>Blocker</b> — <code>src/server.h:15</code> [R03] Include guard 命名不符合規範</summary>

變更將 include guard 從 `__REDIS_H` 改為 `_REDIS_H`，違反專案規範 R03（必須使用雙底線開頭與結尾）。此變更可能導致與其他標頭檔的 include guard 衝突，且破壞一致性。建議恢復為 `__REDIS_H`。

**判斷依據**：diff 中將原本的 `#ifndef __REDIS_H` 改為 `#ifndef _REDIS_H`，且 `#define` 也同步變更，違反 R03。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1725</code> valid_up_to 可能為 -1 時仍進行截斷</summary>

在 `fmterr` 處理中，若 `valid_up_to == -1`，程式僅記錄警告，但之後仍可能執行 `truncate(aof_filepath, valid_up_to)`，此時 `valid_up_to` 為 -1，會導致截斷至檔案開頭前一個位元組，造成整個檔案被清空。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，並設定 `ret = AOF_FAILED`。

**判斷依據**：程式碼中 `valid_up_to` 可能為 -1（例如在讀取第一個命令前就發生格式錯誤），但後續的 `truncate` 呼叫並未排除此情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1728</code> truncate 失敗後仍可能繼續執行</summary>

若 `truncate` 失敗，程式記錄警告後並未設定 `ret` 或跳轉到錯誤處理，而是繼續執行後續的 `lseek` 與 `loaded_ok` 流程，可能導致 AOF 檔案未正確截斷但伺服器仍以成功狀態載入。建議在 `truncate` 失敗時設定 `ret = AOF_FAILED` 並跳轉到 cleanup。

**判斷依據**：錯誤處理分支僅記錄日誌，未改變控制流程，可能導致後續邏輯在檔案未截斷的情況下執行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1734</code> lseek 失敗後仍可能繼續執行</summary>

若 `lseek` 失敗，程式記錄警告後並未設定 `ret` 或跳轉到錯誤處理，而是繼續執行 `loaded_ok` 流程。這可能導致 AOF 檔案指標未正確更新，後續寫入可能覆蓋錯誤位置。建議在 `lseek` 失敗時設定 `ret = AOF_FAILED` 並跳轉到 cleanup。

**判斷依據**：錯誤處理分支僅記錄日誌，未改變控制流程，可能導致後續寫入位置錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1830</code> AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理</summary>

在 `loadAppendOnlyFiles` 中，若 `ret == AOF_BROKEN_RECOVERED` 且該檔案不是最後一個，程式會將 `ret` 改為 `AOF_FAILED` 並記錄錯誤，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 會再次進入 cleanup，可能導致重複處理。建議在設定 `ret = AOF_FAILED` 後直接跳轉到 cleanup，避免重複。

**判斷依據**：程式碼在將 `ret` 改為 `AOF_FAILED` 後，仍會進入下一個 `if` 條件並跳轉到 cleanup，但此時 `ret` 已不是 `AOF_BROKEN_RECOVERED`，所以不會重複，但邏輯上可簡化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/aof.c:1860</code> AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理（第二處）</summary>

與前一個 finding 相同，在第二個迴圈中也有相同的邏輯，建議一併修正。

**判斷依據**：程式碼在將 `ret` 改為 `AOF_FAILED` 後，仍會進入下一個 `if` 條件並跳轉到 cleanup，但此時 `ret` 已不是 `AOF_BROKEN_RECOVERED`，所以不會重複，但邏輯上可簡化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1730</code> 日誌訊息中 broken size 可能為負數</summary>

在日誌訊息中，`(long long)(sb.st_size - valid_up_to)` 可能為負數（若 `valid_up_to` 大於 `sb.st_size`），但此處未檢查。雖然在正常情況下 `valid_up_to` 不應大於檔案大小，但若發生異常，日誌會顯示負數，造成混淆。建議加入檢查或使用無符號型別。

**判斷依據**：計算 `sb.st_size - valid_up_to` 未檢查 `valid_up_to` 是否可能大於 `sb.st_size`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/aof.c:1735</code> 日誌訊息中 broken size 可能為負數（第二處）</summary>

與前一個 finding 類似，此處的 `(long long)(sb.st_size - valid_up_to)` 也可能為負數，建議加入檢查。

**判斷依據**：計算 `sb.st_size - valid_up_to` 未檢查 `valid_up_to` 是否可能大於 `sb.st_size`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/config.c:3258</code> aof-load-broken-max-size 的範圍可能過大</summary>

`createOffTConfig` 的範圍設定為 `0` 到 `LONG_MAX`，但 `aof_load_broken_max_size` 的型別是 `off_t`，在 32 位元系統上可能無法容納 `LONG_MAX`。建議確認 `off_t` 的範圍並使用適當的最大值。

**判斷依據**：`off_t` 可能是 32 位元，而 `LONG_MAX` 在 64 位元系統上為 2^63-1，可能導致溢位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/integration/aof.tcl:707</code> 測試中未清理可能殘留的 AOF 檔案</summary>

測試中多次使用 `create_aof` 建立檔案，但未在每個測試結束後清理，可能影響後續測試的獨立性。建議在每個測試區塊結束後刪除相關檔案。

**判斷依據**：測試程式碼中未見清理邏輯，可能導致檔案殘留。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7358 (cache hit 7296) ｜ completion tokens 2742 ｜ PR #7</sub>