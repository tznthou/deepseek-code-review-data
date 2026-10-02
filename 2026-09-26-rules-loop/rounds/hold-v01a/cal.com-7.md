<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、匯入、資源日曆）的功能，透過在查詢中加入 NOT endsWith 條件來排除這些日曆。主要風險在於 `getGenericCalendarSuffixes` 方法會將所有 provider 的後綴合併，但呼叫端未區分 provider，可能導致跨 provider 的錯誤過濾；此外，`office365_calendar` 目前沒有定義任何後綴，未來若新增後綴可能影響現有邏輯。整體而言，變更範圍小且測試有更新，但需確認跨 provider 的行為是否符合預期。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:67` | getGenericCalendarSuffixes 合併所有 provider 的後綴，可能導致跨 provider 錯誤過濾 | 0.80 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | AND 條件在 genericCalendarSuffixes 為空陣列時會產生空 AND，可能影響查詢結果 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:67</code> getGenericCalendarSuffixes 合併所有 provider 的後綴，可能導致跨 provider 錯誤過濾</summary>

`getGenericCalendarSuffixes` 方法將所有 provider 的後綴合併成一個陣列，但呼叫端 `CalendarSubscriptionService` 在查詢時並未區分 provider，而是將所有後綴套用到所有 provider 的日曆上。這可能導致例如未來為 office365 定義後綴時，Google 日曆也被錯誤過濾。建議改為依 provider 分別取得後綴，或在查詢中依 provider 條件分開處理。

**判斷依據**：diff 中新增的 `getGenericCalendarSuffixes` 方法使用 `flatMap` 合併所有 provider 的後綴，而 `CalendarSubscriptionService` 呼叫時未傳入 provider 資訊，直接將結果用於所有查詢。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> AND 條件在 genericCalendarSuffixes 為空陣列時會產生空 AND，可能影響查詢結果</summary>

當 `genericCalendarSuffixes` 為空陣列時，`genericCalendarSuffixes?.length` 為 0，因此 `AND` 會被設為 `undefined`，這與未提供該參數時的行為一致。但若未來有其他條件需要加入 `AND`，此處的邏輯可能需要調整。目前影響不大，但建議考慮使用更明確的條件判斷。

**判斷依據**：diff 中新增的 `AND` 條件使用 `genericCalendarSuffixes?.length` 來決定是否加入，若為空陣列則設為 `undefined`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5709 (cache hit 4224) ｜ completion tokens 777 ｜ PR #7</sub>