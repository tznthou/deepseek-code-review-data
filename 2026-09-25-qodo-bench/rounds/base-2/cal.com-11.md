<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與 request-reschedule 流程中保持一致，新增 requestReschedule 欄位並補充 eventType 相關資訊。主要風險在於 requestReschedule 的預設值不一致（v2021-10-20 builder 預設 true，而 BookingWebhookFactory 預設 false），可能導致下游系統誤判；此外，新增的 ENABLE_WEBHOOKS 環境變數開關若未設定，可能意外停用所有 webhook。建議先統一預設值並確認環境變數的部署設定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.80 |
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook | 0.70 |
| 🔸 | Minor | `packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276` | iCalSequence 計算可能不正確 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 `BookingWebhookFactory` 中則使用 `params.requestReschedule ?? false`。這表示當呼叫端未明確傳入此欄位時，不同版本的 webhook payload 會得到相反的布林值。若下游系統依賴此欄位判斷是否為 reschedule 流程，可能造成行為不一致。建議統一預設值（例如皆為 false），或在所有呼叫點明確傳入。

**判斷依據**：diff 中新增行 `requestReschedule: dto.requestReschedule ?? true,`，而另一檔案 `BookingWebhookFactory.ts` 新增行 `requestReschedule: params.requestReschedule ?? false,`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> 新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook</summary>

此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 來決定是否發送 webhook。若部署環境未設定此變數，則 `webhooksEnabled` 為 true，行為不變；但若設定為 "false"，則所有取消相關的 webhook 都會被靜默停用，且沒有 log 記錄。這可能導致生產環境中 webhook 意外失效。建議確認此環境變數的用途與部署設定，並考慮在停用時輸出警告 log。

**判斷依據**：diff 中新增行 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，且後續 `promises` 改為條件式產生。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/trpc/server/routers/viewer/bookings/requestReschedule.handler.ts:276</code> iCalSequence 計算可能不正確</summary>

在 requestReschedule 流程中，`iCalSequence` 被設為 `(bookingToReschedule.iCalSequence ?? 0) + 1`。若原始 booking 的 iCalSequence 為 null，則會得到 1；但若原始值為 0，也會得到 1。這可能導致序列號重複或跳號，影響行事曆同步。建議確認 iCalSequence 的起始值慣例，或考慮使用 `(bookingToReschedule.iCalSequence ?? -1) + 1` 等方式。

**判斷依據**：diff 中新增行 `iCalSequence: (bookingToReschedule.iCalSequence ?? 0) + 1,`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6558 (cache hit 6528) ｜ completion tokens 978 ｜ PR #11</sub>