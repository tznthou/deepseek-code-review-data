<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與 request-reschedule 流程中保持一致，新增 requestReschedule 欄位，並補充 eventTypeId、length、iCalSequence、eventTitle 等資訊。主要風險在於 requestReschedule 的預設值不一致（v2021-10-20 builder 預設 true，而 BookingWebhookFactory 預設 false），可能造成下游系統誤判；此外，新增的 ENABLE_WEBHOOKS 環境變數開關若未設定，可能意外停用所有取消 webhook。建議先修正預設值不一致問題，並確認環境變數的預設行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有取消 webhook | 0.70 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:423` | requestReschedule 硬編碼為 false，可能與實際情境不符 | 0.60 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276` | iCalSequence 計算可能不正確 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 v2021-10-20 的 payload builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這兩個建構路徑的預設值相反，可能導致同一事件在不同 webhook 版本或路徑下產生不一致的 payload，下游系統若依此欄位判斷是否為 reschedule 請求，將可能誤判。

建議統一預設值，或明確在 DTO 層級設定，避免隱含預設。

**判斷依據**：diff 中新增的這一行使用 `?? true`，而 `BookingWebhookFactory.ts` 中新增的 `requestReschedule: params.requestReschedule ?? false` 使用 `?? false`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有取消 webhook</summary>

此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，`webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），將導致所有取消 webhook 停止發送，且無任何 log 提示。建議確認此環境變數是否為新引入，並考慮使用更特定的名稱（如 `ENABLE_CANCELLATION_WEBHOOKS`）或增加 log 警告。

**判斷依據**：diff 中新增的這一行，且後續 `webhooks.map` 被包在 `webhooksEnabled ? ... : []` 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:423</code> requestReschedule 硬編碼為 false，可能與實際情境不符</summary>

在一般取消流程中，`requestReschedule` 被硬編碼為 `false`。但若此函式也可能被用於 reschedule 請求的取消（例如從 request-reschedule 流程呼叫），則此值可能不正確。建議確認所有呼叫路徑，或改由呼叫端傳入。

**判斷依據**：diff 中新增的這一行，且未從 input 或 context 取得。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276</code> iCalSequence 計算可能不正確</summary>

此處將 `iCalSequence` 設為 `(bookingToReschedule.iCalSequence ?? 0) + 1`，但若 `bookingToReschedule.iCalSequence` 為 null，則會得到 1。這可能與實際 iCal 序列不符，因為原始序列可能未知。建議確認此邏輯是否符合預期，或考慮保留 null 而非遞增。

**判斷依據**：diff 中新增的這一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6558 (cache hit 6528) ｜ completion tokens 1148 ｜ PR #11</sub>