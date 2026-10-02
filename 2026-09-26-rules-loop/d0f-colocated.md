# D0f 同位置的 finding：重複留言，還是同一處兩個問題？

判準（沿用盲標的 Martian 邊界）：一個 code change 能同時修掉兩則 → 重複；同處但各講各的 → 不同問題。

## hold-v01a #1：aspnetcore-5　`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs`

**規範 pass**（`hold-v01a:aspnetcore-5:1`，第 10 行，信心 0.95，引用 R02 Use File-Scoped Namespace Declarations）
- title：[R02] 使用 block-scoped namespace 而非 file-scoped namespace
- body：此檔案將原本的 file-scoped namespace 宣告改為 block-scoped namespace，違反了專案規範 R02（Use File-Scoped Namespace Declarations）。

**建議修法**：改回 file-scoped namespace 宣告，例如：
```csharp
namespace Microsoft.AspNetCore.Components.Server.Circuits;
```
並移除多餘的括號。
- 盲標 same：aspnetcore-5#0（rule）Traditional namespace declaration with braces
- 位置命中：aspnetcore-5#0（rule）Traditional namespace declaration with braces

**一般 pass**（`base-1:aspnetcore-5:2`，第 10 行，信心 0.6）
- title：命名空間與類別縮排變更可能造成不必要的 diff
- body：此變更將原本的 file-scoped namespace 改為 block-scoped namespace，並調整類別縮排。這與專案中其他測試檔案的風格可能不一致，且增加了 diff 的噪音。若無特殊原因，建議維持原本的 file-scoped namespace 寫法。
- 盲標 same：aspnetcore-5#0（rule）Traditional namespace declaration with braces
- 位置命中：aspnetcore-5#0（rule）Traditional namespace declaration with braces

→ 盲標：兩邊都跟 ['aspnetcore-5#0'] same → 對那則 GT 是重複

---

## hold-v01a #2：cal.com-11　`packages/features/bookings/lib/handleCancelBooking.ts`

**規範 pass**（`hold-v01a:cal.com-11:1`，第 414 行，信心 0.9，引用 R07 Environment Variables Must Not Be Accessed Directly in Non-Configuration Code）
- title：[R07] 直接存取 process.env 判斷 webhook 是否啟用
- body：在 handleCancelBooking.ts 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反 R07（環境變數不應在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致行為不一致。建議將此判斷移至設定模組或透過依賴注入傳入。
- 盲標 same：cal.com-11#0（rule）Direct process.env access in handler
- 位置命中：cal.com-11#0（rule）Direct process.env access in handler

**一般 pass**（`base-1:cal.com-11:2`，第 414 行，信心 0.85）
- title：新增 ENABLE_WEBHOOKS 環境變數可能意外停用 webhook
- body：此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），則會意外停用所有取消 booking 的 webhook，可能導致下游系統收不到通知。建議確認此環境變數名稱是否專用，或改用更明確的名稱，並在文件中說明。
- 盲標 same：無
- 位置命中：cal.com-11#0（rule）Direct process.env access in handler

→ 盲標判不出來，要讀

---

## hold-v01a #3：dify-13　`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py`

**規範 pass**（`hold-v01a:dify-13:1`，第 62 行，信心 0.95，引用 R03 Backend Code Must Use Logging Instead of Print Statements）
- title：[R03] 使用 print 而非 logging
- body：在生產程式碼中使用 `print` 違反專案規範 R03，應改用 `logging` 模組。這會導致輸出不受日誌系統控制，且可能洩漏敏感資訊。建議移除該行或改用 `logger.debug`。
- 盲標 same：dify-13#0（rule）Print statement in production code
- 位置命中：dify-13#0（rule）Print statement in production code；dify-13#1（func）Node execution started before being enqueued and marked as TAKEN

**一般 pass**（`base-1:dify-13:1`，第 62 行，信心 0.8）
- title：不必要的 print 陳述式
- body：新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。
- 盲標 same：dify-13#0（rule）Print statement in production code
- 位置命中：dify-13#0（rule）Print statement in production code；dify-13#1（func）Node execution started before being enqueued and marked as TAKEN

→ 盲標：兩邊都跟 ['dify-13#0'] same → 對那則 GT 是重複

---

## hold-v01a #4：dify-5　`web/app/components/share/text-generation/index.tsx`

**規範 pass**（`hold-v01a:dify-5:1`，第 199 行，信心 0.95，引用 R25 Frontend Code Must Not Use console Statements）
- title：[R25] 新增 console.log 違反前端禁止 console 語句規範
- body：在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，違反 R25 規範。應移除或改用適當的 logging 機制。
- 盲標 same：dify-5#0（rule）Console.log in production frontend code
- 位置命中：dify-5#0（rule）Console.log in production frontend code

**一般 pass**（`base-1:dify-5:1`，第 199 行，信心 0.95）
- title：console.log 可能洩漏使用者輸入資料
- body：新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。
- 盲標 same：dify-5#0（rule）Console.log in production frontend code
- 位置命中：dify-5#0（rule）Console.log in production frontend code

→ 盲標：兩邊都跟 ['dify-5#0'] same → 對那則 GT 是重複

---

## hold-v01a #5：dify-8　`web/app/components/devtools/react-scan/loader.tsx`

**規範 pass**（`hold-v01a:dify-8:1`，第 10 行，信心 0.9，引用 R25 Frontend Code Must Not Use console Statements）
- title：[R25] 使用 console.error 違反前端規範
- body：此處使用 `console.error` 記錄錯誤，違反專案規範 R25（Frontend Code Must Not Use console Statements）。建議改用專案允許的 logging 機制，或移除該 console 語句。
- 盲標 same：dify-8#4（rule）console.error used in frontend code
- 位置命中：dify-8#4（rule）console.error used in frontend code

**一般 pass**（`base-1:dify-8:1`，第 10 行，信心 0.8）
- title：React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊
- body：當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。
- 盲標 same：dify-8#4（rule）console.error used in frontend code
- 位置命中：dify-8#4（rule）console.error used in frontend code

**一般 pass**（`base-1:dify-8:2`，第 10 行，信心 0.7）
- title：TanStack Devtools 載入失敗時完全靜默
- body：catch 區塊僅回傳空元件，沒有任何錯誤記錄。這使得在開發環境中若動態 import 失敗，開發者將無法得知原因，增加除錯困難。建議至少加入 `console.error` 或使用 Sentry 記錄錯誤。
- 盲標 same：無
- 位置命中：dify-8#4（rule）console.error used in frontend code

→ 盲標：兩邊都跟 ['dify-8#4'] same → 對那則 GT 是重複

---

## hold-v01a #6：prefect-10　`ui-v2/tsconfig.app.json`

**規範 pass**（`hold-v01a:prefect-10:1`，第 19 行，信心 0.95，引用 R11 TypeScript Must Enable Strict Type Checking）
- title：[R11] 關閉 TypeScript 嚴格模式
- body：將 `strict` 從 `true` 改為 `false` 違反了專案規範 R11，會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復為 `true`，並修正因此產生的型別錯誤。
- 盲標 same：prefect-10#0（rule）TypeScript strict mode is disabled
- 位置命中：prefect-10#0（rule）TypeScript strict mode is disabled

**一般 pass**（`base-1:prefect-10:1`，第 19 行，信心 0.95）
- title：關閉 TypeScript strict 模式將大幅降低型別安全
- body：將 `strict` 從 `true` 改為 `false` 會停用多項關鍵的型別檢查（如 `strictNullChecks`、`strictFunctionTypes` 等），可能導致未處理的 `null`/`undefined` 錯誤在編譯期無法被發現，增加 runtime 錯誤風險。此變更與 PR 的主要功能無關，且會影響整個專案的型別安全。建議恢復為 `true`，若有必要可針對特定檔案使用 `// @ts-ignore` 或調整型別定義，而非全域關閉。
- 盲標 same：prefect-10#0（rule）TypeScript strict mode is disabled
- 位置命中：prefect-10#0（rule）TypeScript strict mode is disabled

→ 盲標：兩邊都跟 ['prefect-10#0'] same → 對那則 GT 是重複

---

## hold-v01a #7：redis-3　`src/cluster.c`

**規範 pass**（`hold-v01a:redis-3:2`，第 1110 行，信心 0.9，引用 R02 Use zmalloc/zfree Wrappers Instead of Direct malloc/free）
- title：[R02] 使用 malloc/free 而非 zmalloc/zfree
- body：新增的 `malloc` 與 `free` 呼叫違反專案規範 R02，應使用 `zmalloc` 與 `zfree` 以利記憶體追蹤。

**建議修法**：將 `malloc` 改為 `zmalloc`，`free` 改為 `zfree`。
- 盲標 same：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

**一般 pass**（`base-1:redis-3:1`，第 1112 行，信心 0.95）
- title：迴圈邊界錯誤導致 heap buffer overflow
- body：迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。
- 盲標 same：redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

**一般 pass**（`base-1:redis-3:3`，第 1110 行，信心 0.8）
- title：malloc 未檢查失敗
- body：`malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。
- 盲標 same：無
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

**一般 pass**（`base-1:redis-3:5`，第 1110 行，信心 0.6）
- title：slot_buffer 可能造成不必要的記憶體分配
- body：原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。
- 盲標 same：無
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

→ 盲標判不出來，要讀

---

## hold-v01a #8：tauri-2　`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs`

**規範 pass**（`hold-v01a:tauri-2:5`，第 309 行，信心 0.6，引用 R07 Public APIs Must Include Documentation Comments）
- title：[R07] 公開函式缺少文件註解
- body：write_and_make_executable 函式是公開的（pub fn），但沒有文件註解。根據規範 R07，所有公開 API 都應該有 /// 文件說明其用途、參數和回傳值。建議補充文件。
- 盲標 same：無
- 位置命中：tauri-2#2（func）File permissions set before file creation causes failure

**一般 pass**（`base-1:tauri-2:1`，第 312 行，信心 0.8）
- title：write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋
- body：函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。
- 盲標 same：tauri-2#2（func）File permissions set before file creation causes failure
- 位置命中：tauri-2#2（func）File permissions set before file creation causes failure

→ 盲標判不出來，要讀

---

## hold-v01a #9：tauri-2　`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs`

**規範 pass**（`hold-v01a:tauri-2:6`，第 312 行，信心 0.6，引用 R16 Functions Should Return Result Types for Fallible Operations）
- title：[R16] 使用 expect 可能導致 panic
- body：在 write_and_make_executable 中，使用 fs::set_permissions 和 fs::write 並以 map_err 處理錯誤，但沒有使用 expect 或 unwrap。然而，函式簽名回傳 Result<(), FileWriteError>，但內部可能因為其他原因 panic？實際上沒有直接使用 expect，但建議確認所有可能的錯誤都被妥善處理。
- 盲標 same：無
- 位置命中：tauri-2#2（func）File permissions set before file creation causes failure

**一般 pass**（`base-1:tauri-2:1`，第 312 行，信心 0.8）
- title：write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋
- body：函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。
- 盲標 same：tauri-2#2（func）File permissions set before file creation causes failure
- 位置命中：tauri-2#2（func）File permissions set before file creation causes failure

→ 盲標判不出來，要讀

---

## hold-v01b #1：cal.com-11　`packages/features/bookings/lib/handleCancelBooking.ts`

**規範 pass**（`hold-v01b:cal.com-11:1`，第 414 行，信心 0.9，引用 R07 Environment Variables Must Not Be Accessed Directly in Non-Configuration Code）
- title：[R07] 直接存取 process.env 判斷 webhook 是否啟用
- body：在 `handleCancelBooking.ts` 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反 R07（環境變數不得在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致 webhook 意外停用。建議將此判斷移至集中式設定模組，或透過依賴注入傳入。
- 盲標 same：cal.com-11#0（rule）Direct process.env access in handler
- 位置命中：cal.com-11#0（rule）Direct process.env access in handler

**一般 pass**（`base-2:cal.com-11:2`，第 414 行，信心 0.7）
- title：新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook
- body：此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 來決定是否發送 webhook。若部署環境未設定此變數，則 `webhooksEnabled` 為 true，行為不變；但若設定為 "false"，則所有取消相關的 webhook 都會被靜默停用，且沒有 log 記錄。這可能導致生產環境中 webhook 意外失效。建議確認此環境變數的用途與部署設定，並考慮在停用時輸出警告 log。
- 盲標 same：無
- 位置命中：cal.com-11#0（rule）Direct process.env access in handler

→ 盲標判不出來，要讀

---

## hold-v01b #2：dify-13　`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py`

**規範 pass**（`hold-v01b:dify-13:1`，第 62 行，信心 0.95，引用 R03 Backend Code Must Use Logging Instead of Print Statements）
- title：[R03] 使用 print 而非 logging
- body：在 propagate_skip_from_edge 方法中新增了 print 陳述式，違反專案規範 R03（Backend Code Must Use Logging Instead of Print Statements）。print 會直接輸出到 stdout，無法被日誌系統收集，且可能造成效能問題。應改用 logging 模組，並在模組頂部宣告 logger。
- 盲標 same：dify-13#0（rule）Print statement in production code
- 位置命中：dify-13#0（rule）Print statement in production code；dify-13#1（func）Node execution started before being enqueued and marked as TAKEN

**一般 pass**（`base-2:dify-13:1`，第 63 行，信心 0.7）
- title：start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致
- body：在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。
- 盲標 same：dify-13#1（func）Node execution started before being enqueued and marked as TAKEN
- 位置命中：dify-13#0（rule）Print statement in production code；dify-13#1（func）Node execution started before being enqueued and marked as TAKEN

**一般 pass**（`base-2:dify-13:2`，第 62 行，信心 0.9）
- title：使用 print 輸出日誌，應改用 logging
- body：在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。
- 盲標 same：dify-13#0（rule）Print statement in production code
- 位置命中：dify-13#0（rule）Print statement in production code；dify-13#1（func）Node execution started before being enqueued and marked as TAKEN

→ 盲標：兩邊都跟 ['dify-13#0'] same → 對那則 GT 是重複

---

## hold-v01b #3：dify-5　`web/app/components/share/text-generation/index.tsx`

**規範 pass**（`hold-v01b:dify-5:1`，第 199 行，信心 0.95，引用 R25 Frontend Code Must Not Use console Statements）
- title：[R25] 新增 console.log 除錯語句
- body：在批次輸入驗證前新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將資料輸出到瀏覽器主控台，可能洩漏使用者輸入內容，且違反專案規範 R25（禁止 console 語句）。請移除該行。
- 盲標 same：dify-5#0（rule）Console.log in production frontend code
- 位置命中：dify-5#0（rule）Console.log in production frontend code

**一般 pass**（`base-2:dify-5:1`，第 199 行，信心 0.9）
- title：新增的 console.log 可能洩漏批次輸入資料
- body：在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將使用者上傳的批次輸入資料（至少包含標頭列）輸出到瀏覽器主控台。如果資料包含敏感資訊（例如個人資料），可能造成隱私外洩。建議移除這行 console.log，或改用適當的日誌機制（如 debug 級別且不輸出資料內容）。
- 盲標 same：dify-5#0（rule）Console.log in production frontend code
- 位置命中：dify-5#0（rule）Console.log in production frontend code

→ 盲標：兩邊都跟 ['dify-5#0'] same → 對那則 GT 是重複

---

## hold-v01b #4：prefect-10　`ui-v2/tsconfig.app.json`

**規範 pass**（`hold-v01b:prefect-10:1`，第 19 行，信心 0.95，引用 R11 TypeScript Must Enable Strict Type Checking）
- title：[R11] 關閉 TypeScript strict 模式
- body：將 `strict` 從 `true` 改為 `false` 違反了專案規範 R11（TypeScript Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復 `strict: true`，並修正因此產生的型別錯誤。
- 盲標 same：prefect-10#0（rule）TypeScript strict mode is disabled
- 位置命中：prefect-10#0（rule）TypeScript strict mode is disabled

**一般 pass**（`base-2:prefect-10:1`，第 19 行，信心 0.95）
- title：關閉 TypeScript strict 模式會降低型別安全
- body：將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查，包括 `strictNullChecks`、`strictFunctionTypes` 等，可能導致未處理的 null/undefined 錯誤、錯誤的型別推斷，並隱藏潛在的執行時期錯誤。這通常不是一個可接受的變更，除非有明確的技術原因。建議恢復為 `true`，並修正任何因此產生的型別錯誤。
- 盲標 same：prefect-10#0（rule）TypeScript strict mode is disabled
- 位置命中：prefect-10#0（rule）TypeScript strict mode is disabled

→ 盲標：兩邊都跟 ['prefect-10#0'] same → 對那則 GT 是重複

---

## hold-v01b #5：redis-3　`src/cluster.c`

**規範 pass**（`hold-v01b:redis-3:3`，第 1110 行，信心 0.9，引用 R02 Use zmalloc/zfree Wrappers Instead of Direct malloc/free）
- title：[R02] 使用 malloc/free 而非 zmalloc/zfree
- body：根據規範 R02，應使用 zmalloc/zfree 而非標準 malloc/free。此處新增的 `malloc` 和 `free` 違反規範，且無法追蹤記憶體使用。建議改用 `zmalloc` 和 `zfree`。
- 盲標 same：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

**一般 pass**（`base-2:redis-3:1`，第 1112 行，信心 0.95）
- title：迴圈邊界錯誤導致堆積緩衝區溢位
- body：在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。
- 盲標 same：redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

**一般 pass**（`base-2:redis-3:2`，第 1110 行，信心 0.8）
- title：記憶體配置失敗未檢查
- body：`malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。
- 盲標 same：無
- 位置命中：redis-3#0（rule）Direct malloc/free instead of zmalloc/zfree；redis-3#1（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

→ 盲標判不出來，要讀

---

## hold-v01b #6：redis-7　`src/server.h`

**規範 pass**（`hold-v01b:redis-7:1`，第 15 行，信心 0.99，引用 R03 Header Files Must Use Double-Underscore Include Guards）
- title：[R03] Include guard 命名不符合規範
- body：變更將 include guard 從 `__REDIS_H` 改為 `_REDIS_H`，違反專案規範 R03（必須使用雙底線開頭與結尾）。此變更可能導致與其他標頭檔的 include guard 衝突，且破壞一致性。建議恢復為 `__REDIS_H`。
- 盲標 same：redis-7#0（rule）Single underscore include guard used
- 位置命中：redis-7#0（rule）Single underscore include guard used

**一般 pass**（`base-2:redis-7:5`，第 15 行，信心 0.5）
- title：變更 include guard 巨集名稱可能影響外部程式碼
- body：將 `__REDIS_H` 改為 `_REDIS_H` 可能導致與其他使用相同 guard 的程式碼衝突，或破壞依賴舊巨集名稱的條件編譯。雖然影響不大，但建議確認此變更的必要性。
- 盲標 same：redis-7#0（rule）Single underscore include guard used
- 位置命中：redis-7#0（rule）Single underscore include guard used

→ 盲標：兩邊都跟 ['redis-7#0'] same → 對那則 GT 是重複

---
