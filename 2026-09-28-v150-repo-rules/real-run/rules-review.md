<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在讓 BOOKING_CANCELLED webhook payload 在一般取消與 request-reschedule 流程中保持一致，新增 requestReschedule 欄位，並補上 eventTypeId、length、iCalSequence、eventTitle 等資訊。主要風險在於 handleCancelBooking.ts 中直接存取 process.env.ENABLE_WEBHOOKS，違反 R07，且可能因環境變數未設定而意外停用 webhook。此外，requestReschedule 的預設值在不同路徑不一致（一般取消為 false，request-reschedule 為 true，但 v2021-10-20 builder 預設為 true），可能造成下游混淆。建議先修正環境變數存取方式，並統一 requestReschedule 的預設值邏輯。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:414` | [R07] 直接存取 process.env.ENABLE_WEBHOOKS | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:414</code> [R07] 直接存取 process.env.ENABLE_WEBHOOKS</summary>

在 handleCancelBooking.ts 中直接讀取 `process.env.ENABLE_WEBHOOKS` 來決定是否發送 webhook，違反 R07（環境變數不得在非設定程式碼中直接存取）。這會導致：
1. 測試困難，因為無法注入不同的環境變數值。
2. 若環境變數未設定，`process.env.ENABLE_WEBHOOKS !== "false"` 會是 true，因此 webhook 仍會發送，但若未來有人設定為 "0" 或 "off" 等常見值，將無法停用。
建議：將此設定透過依賴注入或集中式設定模組傳入，例如在建構子或參數中接收 `webhooksEnabled` 布林值。

**判斷依據**：diff 中新增的這一行直接使用了 process.env，且位於業務邏輯函式 handler 內。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7997 (cache hit 7936) ｜ completion tokens 1202 ｜ PR #11</sub>