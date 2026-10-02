<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了過濾通用日曆（如 Google 群組、資源日曆）的功能，避免訂閱到非個人日曆。主要變更包括：在 AdaptersFactory 中定義通用日曆後綴、在 SelectedCalendarRepository 的查詢中加入 NOT 條件、以及在 CalendarSubscriptionService 中傳遞後綴列表。整體設計合理，但存在幾個需要修正的問題：`getProviders()` 未包含 office365_calendar，導致 Office 365 日曆永遠不會被處理；`getGenericCalendarSuffixes()` 使用 `Object.keys` 迭代，可能因型別斷言而產生型別安全疑慮；Prisma 查詢中 `AND: undefined` 可能導致不必要的查詢條件；此外，測試中對 `AND: undefined` 的斷言可能不穩定。建議優先修正 `getProviders()` 的 provider 列表，並考慮使用更型別安全的方式取得後綴。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:56` | getProviders() 未包含 office365_calendar，導致 Office 365 日曆永遠不會被處理 | 0.95 |
| ⚠️ | Major | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:67` | getGenericCalendarSuffixes() 使用 Object.keys 迭代可能導致型別不安全 | 0.80 |
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | Prisma 查詢中 AND: undefined 可能導致不必要的查詢條件 | 0.75 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:130` | 測試中斷言 AND: undefined 可能不穩定 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:56</code> getProviders() 未包含 office365_calendar，導致 Office 365 日曆永遠不會被處理</summary>

`getProviders()` 回傳的陣列只包含 `google_calendar`，但 `CalendarSubscriptionProvider` 型別包含 `office365_calendar`。這會導致 `checkForNewSubscriptions()` 在呼叫 `findNextSubscriptionBatch` 時，`integrations` 參數只會是 `['google_calendar']`，因此 Office 365 的日曆永遠不會被選取來訂閱。這是一個功能性回歸，因為原本的程式碼可能預期處理所有 provider。

**失敗情境**：當使用者有 Office 365 日曆且需要訂閱時，`checkForNewSubscriptions` 不會將它們納入批次，導致這些日曆永遠不會被同步。

**建議修法**：將 `office365_calendar` 加入回傳陣列，或明確說明為何只支援 Google Calendar。

**判斷依據**：diff 中 `getProviders()` 的實作只回傳 `['google_calendar']`，但型別 `CalendarSubscriptionProvider` 定義為 `"google_calendar" | "office365_calendar"`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:67</code> getGenericCalendarSuffixes() 使用 Object.keys 迭代可能導致型別不安全</summary>

`getGenericCalendarSuffixes()` 使用 `Object.keys(GENERIC_CALENDAR_SUFFIXES)` 取得 provider 鍵，然後用 `as CalendarSubscriptionProvider` 斷言型別。這在執行時期是安全的，因為 `GENERIC_CALENDAR_SUFFIXES` 的鍵確實是 provider 名稱，但型別系統無法保證。如果未來新增 provider 但忘記更新 `GENERIC_CALENDAR_SUFFIXES`，此處會產生 undefined 的後綴陣列，導致執行時期錯誤。

**建議修法**：使用 `Object.entries` 並直接迭代值，或使用型別安全的輔助函式，例如 `(Object.keys(GENERIC_CALENDAR_SUFFIXES) as CalendarSubscriptionProvider[]).flatMap(...)` 但需確保鍵的完整性。

**判斷依據**：diff 中 `getGenericCalendarSuffixes` 的實作使用 `Object.keys` 和型別斷言。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> Prisma 查詢中 AND: undefined 可能導致不必要的查詢條件</summary>

在 `findNextSubscriptionBatch` 中，當 `genericCalendarSuffixes` 為空或未提供時，`AND` 會被設為 `undefined`。Prisma 在處理 `undefined` 時通常會忽略該條件，但這可能導致查詢產生不必要的 `AND` 子句，影響效能或產生非預期的行為。此外，測試中明確斷言了 `AND: undefined`，這可能依賴於 Prisma 的內部行為，未來升級可能導致測試失敗。

**建議修法**：僅在 `genericCalendarSuffixes` 有值時才加入 `AND` 條件，例如使用條件展開：`...(genericCalendarSuffixes?.length ? { AND: ... } : {})`。

**判斷依據**：diff 中 `AND` 條件在 `genericCalendarSuffixes` 為空時被設為 `undefined`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:130</code> 測試中斷言 AND: undefined 可能不穩定</summary>

在 `findNextSubscriptionBatch` 的測試中，當未提供 `genericCalendarSuffixes` 時，斷言 `AND: undefined`。這依賴於 Prisma 的內部行為，未來 Prisma 版本可能改變處理 `undefined` 的方式，導致測試失敗。建議改為斷言 `AND` 不存在，或使用更寬鬆的匹配。

**判斷依據**：diff 中測試斷言 `AND: undefined`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13815 (cache hit 13696) ｜ completion tokens 1525 ｜ PR #7</sub>