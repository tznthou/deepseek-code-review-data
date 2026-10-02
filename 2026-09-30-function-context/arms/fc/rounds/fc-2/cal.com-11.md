<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與要求重新排程流程中保持一致，新增 requestReschedule 欄位，並補充 eventTypeId、length、iCalSequence、eventTitle 等欄位。主要風險在於 requestReschedule 的預設值不一致：新版 payload builder 預設為 true，而舊版 factory 預設為 false，可能導致下游系統誤判。此外，新增的 ENABLE_WEBHOOKS 環境變數若未設定，會意外停用所有 webhook，且該行為未在文件中說明。建議先修正預設值不一致與環境變數行為，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook | 0.85 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:416` | webhooksEnabled 為 false 時，promises 為空陣列，但後續仍執行 await Promise.all(promises) | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167` | requestReschedule 在取消座位時硬編碼為 true | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276` | iCalSequence 計算可能不正確 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:112` | 新增的 title 和 length 欄位可能造成型別錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致</summary>

在 BookingPayloadBuilder 中，`requestReschedule: dto.requestReschedule ?? true` 將預設值設為 true；但在 BookingWebhookFactory 中，`requestReschedule: params.requestReschedule ?? false` 將預設值設為 false。這會導致相同事件在不同路徑下產生不同的 payload，下游系統可能誤判。建議統一預設值，並明確指定所有呼叫點都傳入正確的 requestReschedule 值。

**判斷依據**：diff 中新增的這一行，與 BookingWebhookFactory.ts 中的 `requestReschedule: params.requestReschedule ?? false` 形成對比。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook</summary>

新增的 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 會讓所有未設定此環境變數的部署（預設為 undefined）停用 webhook 發送。這是一個破壞性變更，且沒有在 PR 描述或文件中說明。建議改為預設啟用（例如 `process.env.ENABLE_WEBHOOKS !== "true"` 或使用明確的布林解析），並在文件中記錄此行為。

**判斷依據**：diff 中新增的這一行，位於 webhooks.map 之前。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:416</code> webhooksEnabled 為 false 時，promises 為空陣列，但後續仍執行 await Promise.all(promises)</summary>

當 webhooksEnabled 為 false 時，`promises` 被指派為空陣列，後續的 `await Promise.all(promises)` 會立即完成，不會發送任何 webhook。這可能是預期行為，但建議在程式碼中加上註解說明，避免未來維護者誤解。

**判斷依據**：diff 中新增的條件運算式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167</code> requestReschedule 在取消座位時硬編碼為 true</summary>

在 cancelAttendeeSeat 中，payload 新增了 `requestReschedule: true`。這表示任何座位取消都會被視為要求重新排程，但實際上座位取消可能只是單純的取消。建議確認此行為是否符合預期，或改為根據實際情境傳入正確的值。

**判斷依據**：diff 中新增的這一行，位於 cancelAttendeeSeat.ts 的 payload 物件中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276</code> iCalSequence 計算可能不正確</summary>

在 requestReschedule.handler.ts 中，`iCalSequence: (bookingToReschedule.iCalSequence ?? 0) + 1` 將 iCalSequence 加 1。但若 bookingToReschedule.iCalSequence 為 null，則結果為 1，可能與實際行事曆序列不一致。建議確認 iCalSequence 的來源與計算方式，或考慮使用 evt.iCalSequence 等既有邏輯。

**判斷依據**：diff 中新增的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:112</code> 新增的 title 和 length 欄位可能造成型別錯誤</summary>

在 findByUidIncludeEventTypeAndReferences 中，select 新增了 `title: true` 和 `length: true`，但未確認回傳型別是否與使用端相容。若使用端預期 eventType 沒有這些欄位，可能導致型別錯誤。建議檢查相關型別定義。

**判斷依據**：diff 中新增的兩行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31408 (cache hit 31360) ｜ completion tokens 1444 ｜ PR #11</sub>