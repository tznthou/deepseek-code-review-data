<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web 下的對應模組，並更新所有匯入路徑。整體重構方向合理，但存在一個明確的邏輯錯誤：sortHosts 函式在移動至共用函式庫時，其優先權比較邏輯被意外反轉，可能導致主機排序結果錯誤。此外，部分檔案缺少結尾換行、匯入路徑使用相對路徑可能影響可維護性，以及刪除的套件匯出可能造成外部相依性中斷。建議修正 sortHosts 邏輯後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時反轉了優先權比較邏輯 | 0.95 |
| ⚠️ | Major | `packages/platform/atoms/package.json:57` | 移除套件匯出可能造成外部相依性中斷 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | 檔案結尾缺少換行符 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | 檔案結尾缺少換行符 | 0.80 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑匯入跨套件模組，降低可維護性 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時反轉了優先權比較邏輯</summary>

在 `isRRWeightsEnabled` 為 true 且權重相同時，原本的排序邏輯是 `return priorityB - priorityA`（優先權較高者在前），但移動後的程式碼變成 `return priorityA - priorityB`，導致排序結果相反。這會影響依賴此排序的所有功能（例如主機選擇、輪詢分配），可能造成錯誤的優先權順序。

**失敗情境**：當啟用 RR 權重且兩個主機權重相同時，優先權較低的主機可能被排到前面，導致分配不符合預期。

**建議修法**：將該行改回 `return priorityB - priorityA;`，並考慮為此函式新增單元測試以鎖定行為。

**判斷依據**：diff 中新增的 sortHosts 函式內，在 `if (weightA === weightB)` 分支中，回傳值從原本的 `priorityB - priorityA` 變成了 `priorityA - priorityB`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:57</code> 移除套件匯出可能造成外部相依性中斷</summary>

此 PR 從 `packages/platform/atoms` 的 `package.json` 中移除了多個匯出路徑，包括 `./add-members-switch/AddMembersWithSwitchWebWrapper`、`./connect/conferencing-apps/ConferencingAppsViewWebWrapper`、`./destination-calendar/wrappers/DestinationCalendarSettingsWebWrapper`、`./event-types/wrappers/EventTypeWebWrapper` 和 `./selected-calendars/wrappers/SelectedCalendarsSettingsWebWrapper`。如果其他套件或外部消費者仍依賴這些路徑，將導致建置失敗或執行時期錯誤。

**失敗情境**：任何未在此 PR 中更新的程式碼若仍從 `@calcom/atoms/...` 匯入這些元件，會在建置時出現模組找不到的錯誤。

**建議修法**：確認所有內部使用都已更新，並考慮保留暫時的相容性匯出（deprecated re-export）或提供遷移指南。

**判斷依據**：diff 顯示多個 exports 條目被刪除，且未在 PR 中看到對應的相容性處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> 檔案結尾缺少換行符</summary>

檔案最後一行 `export default EventLimitsTabWebWrapper;` 之後沒有換行符（`\ No newline at end of file`）。這可能違反專案的格式化規範（R03），並可能導致某些工具或 diff 顯示異常。

**建議修法**：在檔案結尾加上換行符。

**判斷依據**：diff 顯示 `\ No newline at end of file`，且新檔案內容與舊檔案僅差在結尾換行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> 檔案結尾缺少換行符</summary>

檔案最後一行 `export default EventRecurringWebWrapper;` 之後沒有換行符（`\ No newline at end of file`）。這可能違反專案的格式化規範（R03），並可能導致某些工具或 diff 顯示異常。

**建議修法**：在檔案結尾加上換行符。

**判斷依據**：diff 顯示 `\ No newline at end of file`，且新檔案內容與舊檔案僅差在結尾換行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑匯入跨套件模組，降低可維護性</summary>

此檔案從 `apps/web/components/apps` 使用相對路徑 `../../../../packages/platform/atoms/...` 匯入套件內的模組。這種跨套件的相對路徑容易在檔案移動時斷裂，且不利於重構。專案中其他匯入多使用 `@calcom/...` 別名。

**建議修法**：改用套件別名匯入，例如 `@calcom/atoms/destination-calendar/DestinationCalendar` 或類似路徑（若該套件有匯出）。

**判斷依據**：diff 中新增的匯入使用多層相對路徑，而其他檔案多使用 `@calcom/...` 別名。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13581 (cache hit 13568) ｜ completion tokens 1807 ｜ PR #9</sub>