<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了通用日曆後綴過濾機制，避免訂閱群組、資源等非個人日曆。主要風險在於 `getProviders()` 只回傳 `google_calendar`，導致 `office365_calendar` 的後綴永遠不會被使用；此外 `AND: undefined` 可能造成 Prisma 查詢錯誤，且 `endsWith` 過濾對大小寫敏感，可能漏掉部分日曆。建議先修正 provider 列表與 Prisma 條件建構。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:56` | getProviders() 未包含 office365_calendar，導致通用日曆過濾失效 | 0.95 |
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | Prisma where 條件中 AND: undefined 可能導致查詢錯誤 | 0.80 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43` | endsWith 過濾對大小寫敏感，可能漏掉部分通用日曆 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:56</code> getProviders() 未包含 office365_calendar，導致通用日曆過濾失效</summary>

`getProviders()` 目前只回傳 `['google_calendar']`，但 `GENERIC_CALENDAR_SUFFIXES` 定義了 `office365_calendar` 的後綴（目前為空陣列）。這使得 `checkForNewSubscriptions` 中的 `integrations` 參數只包含 `google_calendar`，因此 `office365_calendar` 的日曆永遠不會被選取，即使未來為其添加後綴也無法生效。

**失敗情境**：當團隊同時使用 Office 365 日曆且需要過濾通用日曆時，這些日曆仍會被訂閱，造成不必要的同步與快取。

**建議**：將 `getProviders()` 改為回傳所有支援的 provider，例如 `['google_calendar', 'office365_calendar']`，或從 `GENERIC_CALENDAR_SUFFIXES` 的鍵動態產生。

**判斷依據**：diff 中 `getProviders()` 的實作僅回傳 `google_calendar`，而 `GENERIC_CALENDAR_SUFFIXES` 包含 `office365_calendar` 鍵。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> Prisma where 條件中 AND: undefined 可能導致查詢錯誤</summary>

當 `genericCalendarSuffixes` 為空或未提供時，`AND` 欄位被設為 `undefined`。Prisma 可能不接受 `undefined` 作為 `AND` 的值，導致查詢拋出錯誤或產生非預期行為。

**失敗情境**：呼叫 `findNextSubscriptionBatch` 時未傳入 `genericCalendarSuffixes`（例如舊程式碼或測試），Prisma 可能回傳錯誤，使批次訂閱流程中斷。

**建議**：僅在 `genericCalendarSuffixes` 存在且長度大於 0 時才加入 `AND` 條件，否則省略該欄位。

**判斷依據**：diff 中新增的 `AND` 條件在建構時可能為 `undefined`，而 Prisma 的 `where` 物件通常不接受 `undefined` 值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43</code> endsWith 過濾對大小寫敏感，可能漏掉部分通用日曆</summary>

`endsWith` 在 Prisma 中通常對大小寫敏感（取決於資料庫 collation）。若日曆 ID 的大小寫與後綴不一致（例如 `@Group.Calendar.Google.com`），則不會被過濾。

**失敗情境**：使用者擁有大小寫不同的通用日曆時，仍會被訂閱，導致不必要的同步。

**建議**：考慮使用不區分大小寫的比對（例如 `mode: 'insensitive'`）或先將 `externalId` 轉為小寫再比對。

**判斷依據**：Prisma 的 `endsWith` 預設可能區分大小寫，且未指定 `mode`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13815 (cache hit 13696) ｜ completion tokens 1135 ｜ PR #7</sub>