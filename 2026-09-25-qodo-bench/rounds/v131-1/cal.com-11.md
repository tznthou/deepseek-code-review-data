<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在讓 BOOKING_CANCELLED webhook 在一般取消與要求重新排程流程中提供一致的 payload，新增 requestReschedule 欄位，並補上 eventTypeId、length、iCalSequence、eventTitle 等資訊。主要風險在於 requestReschedule 的預設值不一致：v2021-10-20 的 builder 預設為 true，而 BookingWebhookFactory 預設為 false，可能導致下游系統誤判。此外，新增的 ENABLE_WEBHOOKS 環境變數開關若未正確設定，可能意外停用所有 webhook。建議先統一預設值並確認環境變數的部署設定。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | 新增 ENABLE_WEBHOOKS 環境變數開關可能意外停用所有 webhook | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:416` | webhooksEnabled 為 false 時仍會建立空陣列並呼叫 Promise.all | 0.60 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276` | iCalSequence 計算可能不正確 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 true。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 false。這兩個地方處理同一事件，但預設值相反，可能導致下游系統在未明確提供此欄位時收到不同的值，造成邏輯錯誤。建議統一預設值，或明確在 DTO 中要求此欄位。

**判斷依據**：diff 中新增行 `requestReschedule: dto.requestReschedule ?? true,`，而 `BookingWebhookFactory.ts` 中新增 `requestReschedule: params.requestReschedule ?? false,`，兩者預設值不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> 新增 ENABLE_WEBHOOKS 環境變數開關可能意外停用所有 webhook</summary>

此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，webhooks 會正常發送；但若設定為 "false"，則所有 webhook 都會被停用。這可能影響所有依賴 webhook 的功能，且此變更未在 PR 描述中提及。建議確認此環境變數的部署設定，並考慮使用更明確的名稱或預設值。

**判斷依據**：diff 中新增此環境變數檢查，並用於條件式發送 webhook。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:416</code> webhooksEnabled 為 false 時仍會建立空陣列並呼叫 Promise.all</summary>

當 `webhooksEnabled` 為 false 時，`promises` 為空陣列，但仍會執行 `await Promise.all(promises)`。雖然功能上無影響，但可讀性較差，且可能讓讀者誤以為仍有非同步操作。建議直接 return 或使用 if 條件包住整個 webhook 發送區塊。

**判斷依據**：diff 中新增條件式，但後續仍呼叫 `await Promise.all(promises)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276</code> iCalSequence 計算可能不正確</summary>

在 requestReschedule handler 中，`iCalSequence: (bookingToReschedule.iCalSequence ?? 0) + 1`。若 `bookingToReschedule.iCalSequence` 為 null，則會得到 1，但若原本為 0，也會得到 1。這可能導致 iCalSequence 重複，影響行事曆同步。建議確認 iCalSequence 的起始值與遞增邏輯。

**判斷依據**：diff 中新增此行，直接對可能為 null 的值加 1。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6522 (cache hit 1408) ｜ completion tokens 1137 ｜ PR #11</sub>