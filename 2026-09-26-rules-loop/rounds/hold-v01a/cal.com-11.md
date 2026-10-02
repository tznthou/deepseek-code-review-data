<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在統一 BOOKING_CANCELLED webhook 的 payload，新增 requestReschedule 欄位，並在取消流程中傳遞相關資料。主要風險在於直接存取 process.env 違反 R07，以及 requestReschedule 預設值不一致可能導致下游行為差異。建議先修正環境變數存取方式，並確認預設值邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | [R07] 直接存取 process.env 判斷 webhook 是否啟用 | 0.90 |
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.85 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:416` | webhooksEnabled 判斷可能影響既有行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> [R07] 直接存取 process.env 判斷 webhook 是否啟用</summary>

在 handleCancelBooking.ts 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反 R07（環境變數不應在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致行為不一致。建議將此判斷移至設定模組或透過依賴注入傳入。

**判斷依據**：diff 中新增的這一行直接讀取 process.env，且位於業務邏輯 handler 中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 BookingPayloadBuilder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 BookingWebhookFactory 中則使用 `params.requestReschedule ?? false`。這兩個地方對同一欄位的預設值不同，可能導致不同路徑產生的 webhook payload 不一致，進而影響下游系統的判斷。建議統一預設值，並明確其語意。

**判斷依據**：diff 中新增的這一行，與 BookingWebhookFactory.ts 中的 `requestReschedule: params.requestReschedule ?? false` 形成對比。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:416</code> webhooksEnabled 判斷可能影響既有行為</summary>

新增的 `webhooksEnabled` 判斷會在環境變數為 "false" 時跳過所有 webhook 發送。若此環境變數未設定，行為不變；但若設定為 "false"，則會完全停用 webhook，可能影響依賴 webhook 的功能。建議確認此變更是否為預期行為，並考慮提供更明確的設定方式。

**判斷依據**：diff 中將原本的 `webhooks.map` 改為條件式，新增了環境變數判斷。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7997 (cache hit 6528) ｜ completion tokens 782 ｜ PR #11</sub>