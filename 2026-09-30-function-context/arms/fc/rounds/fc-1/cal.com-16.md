<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將錄製與逐字稿端點從未受保護改為需要驗證與授權，並新增對應的 e2e 測試。主要風險在於錄製端點的權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不足的使用者無法存取；此外，getRecordings 的呼叫移除了 await，若該方法回傳 Promise 將導致回傳未解析的 Promise。整體方向正確，但需確認權限變更的意圖與修正 await 問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227` | getRecordings 呼叫缺少 await，可能回傳未解析的 Promise | 0.95 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:184` | 錄製端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不足 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227</code> getRecordings 呼叫缺少 await，可能回傳未解析的 Promise</summary>

在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（從其他端點如 `getVideoSessions` 使用 `await` 可推測），則回傳的 `recordings` 會是 Promise 物件而非實際資料，導致 API 回傳錯誤的資料型態或序列化失敗。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件，而非錄製陣列，可能造成客戶端解析錯誤或資料外洩。

**建議**：恢復 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

**判斷依據**：diff 中此行從 `const recordings = await this.calVideoService.getRecordings(bookingUid);` 改為 `const recordings = this.calVideoService.getRecordings(bookingUid);`，移除了 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:184</code> 錄製端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不足</summary>

`getBookingRecordings` 端點的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄製通常只需要讀取權限，改為寫入權限可能導致僅有讀取權限的 API 金鑰或使用者無法存取錄製，造成不必要的授權失敗。

**失敗情境**：具有 `BOOKING_READ` 權限但無 `BOOKING_WRITE` 權限的 API 金鑰呼叫此端點時，會收到 403 Forbidden，即使該使用者有權讀取錄製。

**建議**：確認此變更是否為刻意設計。若錄製讀取不應要求寫入權限，請改回 `BOOKING_READ`。

**判斷依據**：diff 中 `@Permissions([BOOKING_READ])` 改為 `@Permissions([BOOKING_WRITE])`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11307 (cache hit 1536) ｜ completion tokens 818 ｜ PR #16</sub>