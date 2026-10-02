<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與 request-reschedule 流程中保持一致，新增 requestReschedule 欄位，並補齊 eventTypeId、length、iCalSequence、eventTitle 等欄位。主要風險在於 requestReschedule 的預設值不一致：在 v2021-10-20 的 builder 中預設為 true，但在 BookingWebhookFactory 中預設為 false，可能導致下游 webhook 消費者誤判。此外，新增的 ENABLE_WEBHOOKS 環境變數控制邏輯若未設定，會意外停用所有 webhook，且未見對應測試。建議先修正預設值不一致問題，並確認環境變數的預設行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook | 0.85 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:416` | webhooksEnabled 為 false 時，promises 為空陣列，但後續仍會執行其他取消邏輯 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167` | requestReschedule 在取消座位時固定為 true，可能不準確 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:112` | 新增 select 欄位可能影響效能 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致</summary>

在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，payload 會是 `true`。但在 `BookingWebhookFactory.createCancelledEventPayload` 中，預設值為 `false`。這兩個產生路徑的預設行為不同，可能導致下游 webhook 消費者收到不一致的資料。建議統一預設值，或明確在 DTO 層級提供。

**判斷依據**：diff 中新增的這一行，與 BookingWebhookFactory.ts 中的 `requestReschedule: params.requestReschedule ?? false` 形成對比。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook</summary>

新增的 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 表示只要環境變數未設定或設為任何非 "false" 的值，webhook 都會啟用。但若部署環境中未設定此變數，且程式碼預期預設為停用，則會意外啟用；反之若預期預設為啟用，則此邏輯正確。需確認此環境變數的預設行為，並考慮加入更明確的設定或文件。

**判斷依據**：diff 中新增的這一行，控制 webhook 是否發送，但未見對應的環境變數設定或測試。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:416</code> webhooksEnabled 為 false 時，promises 為空陣列，但後續仍會執行其他取消邏輯</summary>

當 `webhooksEnabled` 為 false 時，`promises` 為空陣列，`await Promise.all(promises)` 會立即完成，但後續的取消流程（如更新資料庫、發送郵件等）仍會執行。這可能符合預期，但需確認停用 webhook 是否也應停用其他副作用。

**判斷依據**：diff 中新增的條件式，僅控制 webhook 發送，但未影響其他取消邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167</code> requestReschedule 在取消座位時固定為 true，可能不準確</summary>

在 `cancelAttendeeSeat` 中，payload 新增 `requestReschedule: true`，但此流程是取消座位，並非 request-reschedule 流程。若此 webhook 被下游用於判斷是否為 reschedule 請求，可能會誤判。建議確認此處的語意。

**判斷依據**：diff 中新增的這一行，位於 cancelAttendeeSeat.ts 的 payload 建構中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:112</code> 新增 select 欄位可能影響效能</summary>

在 `findByUidIncludeEventTypeAndReferences` 中新增了 `title`、`length`、`iCalSequence` 欄位，這些欄位可能不是所有呼叫端都需要，增加不必要的資料傳輸。建議確認所有使用此方法的呼叫端是否都需要這些欄位。

**判斷依據**：diff 中新增的 select 欄位。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 31408 (cache hit 1536) ｜ completion tokens 1297 ｜ PR #11</sub>