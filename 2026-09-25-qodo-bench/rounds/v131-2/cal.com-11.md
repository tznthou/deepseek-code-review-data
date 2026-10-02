<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在統一 BOOKING_CANCELLED webhook 的 payload，新增 requestReschedule 欄位以區分一般取消與請求改期流程，並補齊 eventTypeId、length、iCalSequence、eventTitle 等資訊。主要風險在於 requestReschedule 的預設值不一致（v2021-10-20 builder 預設 true，而 BookingWebhookFactory 預設 false），可能導致下游系統誤判。此外，新增的 ENABLE_WEBHOOKS 環境變數開關若未設定，將意外停用所有取消 webhook，需確認部署環境已正確配置。整體改動方向合理，但需修正預設值不一致與補齊測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.90 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | 新增 ENABLE_WEBHOOKS 環境變數開關可能意外停用所有取消 webhook | 0.85 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:423` | requestReschedule 硬編碼為 false，可能遺漏請求改期情境 | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167` | requestReschedule 硬編碼為 true，可能不適用所有座位取消情境 | 0.70 |
| 🔸 | Minor | `packages/features/webhooks/lib/factory/base/BaseBookingPayloadBuilder.ts:17` | BookingExtraDataMap 中 requestReschedule 為可選，可能導致 payload 缺少欄位 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。然而，在 `BookingWebhookFactory` 中，`requestReschedule` 的預設值為 `false`。這兩個路徑的預設值相反，可能導致同一事件在不同 webhook 版本或呼叫路徑下產生不一致的 payload，使下游系統誤判取消類型。

建議統一預設值，並確認哪一個才是正確的預設行為。若一般取消應為 `false`，則 v2021-10-20 builder 應改為 `?? false`；若請求改期應為 `true`，則需確保所有呼叫點都明確傳入。

**判斷依據**：diff 中新增的這一行，與 BookingWebhookFactory.ts 中的 `requestReschedule: params.requestReschedule ?? false` 形成對比。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> 新增 ENABLE_WEBHOOKS 環境變數開關可能意外停用所有取消 webhook</summary>

此處新增了 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中誤設為 `"false"`（例如用於其他目的），將導致所有取消 webhook 被靜默停用，且沒有 log 記錄。這可能造成下游系統無法收到取消通知，影響資料同步。

建議：
1. 確認此環境變數是否已在所有部署環境中正確設定。
2. 若未設定，應記錄警告 log，或考慮使用更明確的變數名稱（如 `DISABLE_BOOKING_CANCELLED_WEBHOOKS`）。
3. 補充測試涵蓋此開關的行為。

**判斷依據**：diff 中新增的這一行，且後續 `webhooks.map` 改為條件式執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:423</code> requestReschedule 硬編碼為 false，可能遺漏請求改期情境</summary>

在一般取消流程中，`requestReschedule` 被硬編碼為 `false`。若此函式也可能被請求改期流程呼叫（例如透過某些路徑），則會錯誤地標記為一般取消。目前從 diff 來看，請求改期流程似乎走 `cancelAttendeeSeat` 並設定為 `true`，但需確認所有取消路徑都正確設定此欄位。

建議：確認 `handleCancelBooking` 是否只處理一般取消，若是，則可考慮在函式簽名中明確區分，或從輸入參數傳入 `requestReschedule`。

**判斷依據**：diff 中新增的這一行，與 cancelAttendeeSeat.ts 中的 `requestReschedule: true` 形成對比。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167</code> requestReschedule 硬編碼為 true，可能不適用所有座位取消情境</summary>

在 `cancelAttendeeSeat` 中，`requestReschedule` 被硬編碼為 `true`。但此函式可能用於一般取消座位（非請求改期），若如此，則會錯誤地標記為請求改期。需要確認此函式的所有呼叫情境，或將此值改為由呼叫端傳入。

**判斷依據**：diff 中新增的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/webhooks/lib/factory/base/BaseBookingPayloadBuilder.ts:17</code> BookingExtraDataMap 中 requestReschedule 為可選，可能導致 payload 缺少欄位</summary>

在 `BookingExtraDataMap` 中，`requestReschedule` 被定義為可選 (`requestReschedule?: boolean`)。若某些呼叫路徑未提供此欄位，最終 payload 可能缺少該欄位，使下游系統無法判斷。建議確認所有產生 BOOKING_CANCELLED 事件的地方都明確設定此值，或考慮在 builder 中提供預設值。

**判斷依據**：diff 中新增的這一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6522 (cache hit 6400) ｜ completion tokens 1502 ｜ PR #11</sub>