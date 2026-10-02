<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要目的是讓 BOOKING_CANCELLED webhook payload 在一般取消與要求重新排程流程中保持一致，新增 requestReschedule 欄位，並在 BookingRepository 查詢中補上 title、length、iCalSequence 欄位。整體改動範圍明確，但發現兩處違反 repo 規範：在 handleCancelBooking.ts 中直接存取 process.env.ENABLE_WEBHOOKS，違反 R07；以及多處格式化不符合 Biome 標準（R03），例如 import 陳述式、物件縮排、空行等。建議先修正這些問題再合併。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/bookings/lib/handleCancelBooking.ts:413` | [R07] 在業務邏輯中直接存取 process.env | 0.95 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:57` | [R03] import 陳述式格式不符合 Biome 標準 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:110` | [R03] 物件屬性縮排不一致 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:154` | [R03] log.warn 參數格式化不符合 Biome 標準 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:374` | [R03] 物件展開縮排不一致 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:416` | [R03] 條件運算子換行格式不符合 Biome 標準 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/lib/handleCancelBooking.ts:734` | [R03] 建構子格式不符合 Biome 標準 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:142` | [R03] 物件縮排不一致 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:328` | [R03] 建構子格式不符合 Biome 標準 | 0.90 |
| 🔸 | Minor | `packages/features/bookings/repositories/BookingRepository.ts:659` | [R03] 查詢物件縮排不一致 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:413</code> [R07] 在業務邏輯中直接存取 process.env</summary>

在 `handleCancelBooking.ts` 的 handler 函式中，直接讀取 `process.env.ENABLE_WEBHOOKS` 來決定是否發送 webhook，這違反了 R07 規範：環境變數不應在非設定程式碼中直接存取。

**失敗情境**：
- 測試時無法輕易模擬此環境變數，導致測試不穩定。
- 若未來需要動態調整此設定，必須修改業務邏輯。

**建議修法**：
- 將此設定透過依賴注入或 centralized configuration 模組傳入。
- 例如在 `BookingCancelService` 的 dependencies 中加入 `webhooksEnabled` 布林值，由呼叫端從設定中取得。

**判斷依據**：diff 中新增的兩行：
```
+  // Only send webhooks if enabled in environment
+  const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";
```
此處直接使用 process.env，違反 R07。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:57</code> [R03] import 陳述式格式不符合 Biome 標準</summary>

import 陳述式被重新格式化為多行，但縮排與換行方式可能不符合 Biome 的 110 字元行寬與 2 空格縮排規則。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中將原本的單行 import 改為多行，但縮排為 2 空格，可能超過行寬限制或不符合 Biome 的格式規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:110</code> [R03] 物件屬性縮排不一致</summary>

在 `getAuditActor` 函式中，`buildActorEmail` 的參數物件縮排從原本的 4 空格改為 6 空格，與其他程式碼不一致。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段縮排由 4 空格改為 6 空格，可能不符合 Biome 的 2 空格縮排規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:154</code> [R03] log.warn 參數格式化不符合 Biome 標準</summary>

`log.warn` 的參數被重新格式化為多行，但縮排與換行方式可能不符合 Biome 規則。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段被重新格式化，但縮排為 6 空格，可能不符合 Biome 的 2 空格縮排規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:374</code> [R03] 物件展開縮排不一致</summary>

在 `evt` 物件中，`team` 屬性的縮排從原本的 4 空格改為 8 空格，與其他屬性不一致。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段縮排由 4 空格改為 8 空格，可能不符合 Biome 的 2 空格縮排規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:416</code> [R03] 條件運算子換行格式不符合 Biome 標準</summary>

`webhooksEnabled ? webhooks.map(...) : []` 的換行方式可能不符合 Biome 的格式規則。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段被重新格式化，但換行與縮排可能不符合 Biome 規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/lib/handleCancelBooking.ts:734</code> [R03] 建構子格式不符合 Biome 標準</summary>

`constructor(private readonly deps: BookingCancelServiceDependencies) {}` 中的空格可能不符合 Biome 規則。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中將 `{ }` 改為 `{}`，但可能不符合 Biome 的空格規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:142</code> [R03] 物件縮排不一致</summary>

在 `buildWhereClauseForActiveBookings` 函式中，多處物件縮排從原本的 4 空格改為 8 空格，與其他程式碼不一致。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段縮排由 4 空格改為 8 空格，可能不符合 Biome 的 2 空格縮排規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:328</code> [R03] 建構子格式不符合 Biome 標準</summary>

`constructor(private prismaClient: PrismaClient) {}` 中的空格可能不符合 Biome 規則。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中將 `{ }` 改為 `{}`，但可能不符合 Biome 的空格規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/bookings/repositories/BookingRepository.ts:659</code> [R03] 查詢物件縮排不一致</summary>

在 `currentBookingsAllUsersQueryThree` 查詢中，物件縮排從原本的 4 空格改為 8 空格，與其他程式碼不一致。

**建議修法**：
- 執行 `biome format` 自動修正。

**判斷依據**：diff 中此段縮排由 4 空格改為 8 空格，可能不符合 Biome 的 2 空格縮排規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8034 (cache hit 7936) ｜ completion tokens 2577 ｜ PR #11</sub>