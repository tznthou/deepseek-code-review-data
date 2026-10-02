<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與 request-reschedule 流程中保持一致，新增 requestReschedule 欄位，並在 request-reschedule 流程中傳遞額外事件資訊。主要風險在於直接存取 process.env 違反 R07，以及 requestReschedule 預設值不一致可能導致下游行為差異。建議先修正環境變數存取方式，並統一預設值。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | [R07] 直接存取 process.env 判斷 webhook 是否啟用 | 0.90 |
| ⚠️ | Major | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 預設值不一致可能導致下游誤判 | 0.80 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:414` | webhook 停用時未記錄任何資訊 | 0.70 |
| 🔸 | Minor | `packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48` | requestReschedule 欄位型別未明確 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> [R07] 直接存取 process.env 判斷 webhook 是否啟用</summary>

在 `handleCancelBooking.ts` 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反 R07（環境變數不得在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致 webhook 意外停用。建議將此判斷移至集中式設定模組，或透過依賴注入傳入。

**判斷依據**：diff 中新增的這一行直接讀取 process.env，且位於業務邏輯函式內，非設定檔或環境偵測工具。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 預設值不一致可能導致下游誤判</summary>

在 `BookingPayloadBuilder.ts` 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，但其他建構器（如 `BookingWebhookFactory.ts`）使用 `?? false`。若呼叫端未明確提供此欄位，不同版本或路徑的 webhook payload 會得到不同的預設值，可能導致下游系統誤判取消類型。建議統一預設值，或明確在 DTO 中要求此欄位。

**判斷依據**：diff 中新增的這一行使用 `?? true`，而 `BookingWebhookFactory.ts` 中使用 `?? false`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> webhook 停用時未記錄任何資訊</summary>

當 `ENABLE_WEBHOOKS` 設為 `false` 時，程式直接略過 webhook 發送，且未留下任何 log。這可能導致在除錯時難以判斷 webhook 是否因設定而停用。建議至少記錄一條 debug 或 info 等級的 log，說明 webhook 已停用。

**判斷依據**：diff 中新增的條件判斷，若為 false 則 promises 為空陣列，無任何 log。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48</code> requestReschedule 欄位型別未明確</summary>

`requestReschedule` 在 DTO 和 payload 型別中皆為選用布林值，但未明確其語意。建議在型別定義處加上 JSDoc 說明此欄位代表「是否為 request-reschedule 流程」，以避免未來誤用。

**判斷依據**：多個型別定義中新增此選用欄位，但無任何註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7997 (cache hit 7936) ｜ completion tokens 1018 ｜ PR #11</sub>