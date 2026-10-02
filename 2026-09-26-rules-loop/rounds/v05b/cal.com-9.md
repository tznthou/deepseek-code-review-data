<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web 下的對應模組，並更新所有匯入路徑。主要風險在於 sortHosts 函式在移動時邏輯被意外修改（priority 排序方向反轉），可能導致主持人排序錯誤。此外，部分檔案缺少結尾換行、匯入路徑使用相對路徑可能違反專案慣例，以及移除的 exports 可能造成外部依賴中斷。建議先修正 sortHosts 邏輯並確認所有匯入路徑正確。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時 priority 排序方向被反轉 | 0.95 |
| ⚠️ | Major | `packages/platform/atoms/package.json:57` | 移除多個 exports 可能造成外部依賴中斷 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑匯入跨 package 的模組 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | 縮排不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時 priority 排序方向被反轉</summary>

在 `packages/lib/bookings/hostGroupUtils.ts` 新增的 `sortHosts` 函式中，當 `isRRWeightsEnabled` 為 true 且權重相同時，回傳 `priorityA - priorityB`；但原始實作（見 `apps/web/modules/event-types/components/HostEditDialogs.tsx` 刪除的程式碼）是回傳 `priorityB - priorityA`。這會導致主持人排序結果相反，可能影響事件類型的主持人顯示順序或指派邏輯。請改回 `priorityB - priorityA`。

**判斷依據**：diff 中刪除的原始函式：`return priorityB - priorityA;`；新增的函式：`return priorityA - priorityB;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:57</code> 移除多個 exports 可能造成外部依賴中斷</summary>

此 PR 從 `packages/platform/atoms/package.json` 的 `exports` 欄位移除了多個路徑，包括 `./add-members-switch/AddMembersWithSwitchWebWrapper`、`./connect/conferencing-apps/ConferencingAppsViewWebWrapper`、`./destination-calendar/wrappers/DestinationCalendarSettingsWebWrapper`、`./event-types/wrappers/EventTypeWebWrapper` 和 `./selected-calendars/wrappers/SelectedCalendarsSettingsWebWrapper`。如果其他 package 或外部專案仍依賴這些路徑，匯入會失敗。請確認所有使用這些路徑的程式碼都已更新，或考慮保留相容性別名。

**判斷依據**：diff 中刪除的 exports 項目

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾沒有換行符（`\ No newline at end of file`），違反 Biome 格式規範（LF line endings）。請在最後一行加上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾沒有換行符（`\ No newline at end of file`），違反 Biome 格式規範（LF line endings）。請在最後一行加上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑匯入跨 package 的模組</summary>

此檔案從 `apps/web/components/apps` 使用相對路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 匯入 `AtomsWrapper`，以及 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`。這可能違反專案對 package 匯入的慣例（通常使用 `@calcom/...` 別名），且容易在檔案移動時出錯。建議改用 package 的公開匯入路徑。

**判斷依據**：diff 中新增的相對路徑匯入

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> 縮排不一致</summary>

在 `tabMap` 物件中，`setup` 和 `availability` 的 JSX 縮排從 6 格改為 8 格，與其他 tab 的縮排不一致。這可能違反 Biome 格式規範。請統一縮排。

**判斷依據**：diff 中縮排變更

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13540 (cache hit 13440) ｜ completion tokens 1443 ｜ PR #9</sub>