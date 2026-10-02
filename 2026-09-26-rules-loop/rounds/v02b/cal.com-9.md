<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並將 sortHosts 函式移至 lib 套件。主要風險在於 import 路徑變更可能造成循環依賴（R02），以及 sortHosts 邏輯在移動時被意外修改（priority 排序方向反轉）。此外，部分檔案缺少結尾換行、縮排不一致，違反格式化規範（R03）。建議先修正 sortHosts 的邏輯變更與循環依賴問題，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時邏輯被意外修改 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | [R02] 可能造成循環依賴：apps/web 元件直接 import packages/platform/atoms 內部路徑 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | [R03] 縮排不一致：JSX 屬性縮排從 2 空格變成 4 空格 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:245` | [R03] 縮排不一致：JSX 屬性縮排從 2 空格變成 4 空格 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時邏輯被意外修改</summary>

在 `HostEditDialogs.tsx` 中原本的 `sortHosts` 函式，當 `isRRWeightsEnabled` 為 true 且權重相同時，回傳 `priorityB - priorityA`（降冪排序）。但移動到 `hostGroupUtils.ts` 後，該分支變成 `priorityA - priorityB`（升冪排序）。這會導致在啟用 RR 權重且權重相同時，主機的排序順序反轉，可能影響路由決策。請確認此變更是否為預期，若不是，請修正回原本的邏輯。

**判斷依據**：diff 中 `packages/lib/bookings/hostGroupUtils.ts` 新增的 `sortHosts` 函式，在 `weightA === weightB` 時回傳 `priorityA - priorityB`；而原始 `apps/web/modules/event-types/components/HostEditDialogs.tsx` 中刪除的函式在相同條件下回傳 `priorityB - priorityA`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> [R02] 可能造成循環依賴：apps/web 元件直接 import packages/platform/atoms 內部路徑</summary>

此檔案從 `packages/platform/atoms/src/components/atoms-wrapper` 和 `packages/platform/atoms/destination-calendar/DestinationCalendar` 匯入，但該檔案位於 `apps/web/components/apps`。根據 R02，`apps/web` 不應直接依賴 `packages/platform/atoms` 的內部實作路徑，應透過公開的 package exports 匯入。這可能導致循環依賴或破壞架構邊界。建議改為從 `@calcom/atoms` 的公開 API 匯入，或將這些依賴移至適當的套件。

**判斷依據**：diff 顯示此檔案從 `packages/platform/atoms` 的深層路徑匯入，違反 R02 的依賴方向限制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> [R03] 縮排不一致：JSX 屬性縮排從 2 空格變成 4 空格</summary>

在 `tabMap` 的 `setup` 和 `availability` 區塊中，JSX 屬性的縮排從原本的 2 空格變成 4 空格，與專案標準（2 空格縮排）不一致。請執行 Biome 格式化以修正。

**判斷依據**：diff 中 `EventTypeWebWrapper.tsx` 的 `tabMap` 區塊顯示縮排從 2 空格改為 4 空格。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾的 `export default EventLimitsTabWebWrapper;` 後方沒有換行符，違反格式化規範。請確保檔案以換行符結尾。

**判斷依據**：diff 顯示此檔案最後一行沒有換行符（`\ No newline at end of file`）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾的 `export default EventRecurringWebWrapper;` 後方沒有換行符，違反格式化規範。請確保檔案以換行符結尾。

**判斷依據**：diff 顯示此檔案最後一行沒有換行符（`\ No newline at end of file`）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:245</code> [R03] 縮排不一致：JSX 屬性縮排從 2 空格變成 4 空格</summary>

在 `tabMap` 的 `availability` 區塊中，JSX 屬性的縮排從原本的 2 空格變成 4 空格，與專案標準（2 空格縮排）不一致。請執行 Biome 格式化以修正。

**判斷依據**：diff 中 `EventTypeWebWrapper.tsx` 的 `tabMap` 區塊顯示縮排從 2 空格改為 4 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13571 (cache hit 13568) ｜ completion tokens 1608 ｜ PR #9</sub>