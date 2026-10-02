<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web 下的對應模組，並更新所有匯入路徑。整體重構方向合理，但存在一個關鍵邏輯變更：sortHosts 函式在權重相等時，優先權排序方向被反轉（原本 priorityB - priorityA，現在變成 priorityA - priorityB），這可能導致主機排序錯誤。此外，部分檔案缺少結尾換行、匯入路徑使用相對路徑可能違反專案慣例，以及移除的匯出路徑可能造成外部相依性中斷。建議先修正 sortHosts 的排序邏輯，並確認所有匯出路徑的相容性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 在權重相等時優先權排序方向反轉 | 0.95 |
| ⚠️ | Major | `packages/platform/atoms/package.json:57` | 移除公開匯出路徑可能造成外部相依性中斷 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案缺少結尾換行 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案缺少結尾換行 | 0.90 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑匯入跨套件模組 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 在權重相等時優先權排序方向反轉</summary>

在 `isRRWeightsEnabled` 為 true 且 `weightA === weightB` 時，原本的排序是 `priorityB - priorityA`（優先權高者在前），但移動後的程式碼變成 `priorityA - priorityB`，導致排序方向相反。這會影響依賴此函式的主機排序邏輯，可能造成錯誤的主機指派順序。

建議修正為：
```ts
if (weightA === weightB) {
  return priorityB - priorityA;
}
```

**判斷依據**：diff 中新增的 sortHosts 函式，在 weightA === weightB 時回傳 priorityA - priorityB，而原始 HostEditDialogs.tsx 中的實作為 priorityB - priorityA。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:57</code> 移除公開匯出路徑可能造成外部相依性中斷</summary>

從 package.json 的 exports 中移除了多個路徑（如 `./add-members-switch/AddMembersWithSwitchWebWrapper`、`./connect/conferencing-apps/ConferencingAppsViewWebWrapper`、`./destination-calendar/wrappers/DestinationCalendarSettingsWebWrapper`、`./event-types/wrappers/EventTypeWebWrapper`、`./selected-calendars/wrappers/SelectedCalendarsSettingsWebWrapper`）。如果其他套件或外部專案依賴這些路徑，升級後會導致匯入失敗。建議確認這些路徑是否已完全不再被使用，或保留相容性匯出。

**判斷依據**：diff 顯示多個 exports 條目被刪除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案缺少結尾換行</summary>

檔案結尾缺少換行符號，違反 Biome 格式規範（LF line endings）。請在最後一行加上換行。

**判斷依據**：diff 顯示最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案缺少結尾換行</summary>

檔案結尾缺少換行符號，違反 Biome 格式規範（LF line endings）。請在最後一行加上換行。

**判斷依據**：diff 顯示最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑匯入跨套件模組</summary>

此檔案從 apps/web/components/apps 使用相對路徑 `../../../../packages/platform/atoms/...` 匯入套件內的模組，這可能違反專案對匯入路徑的慣例（通常使用別名如 @calcom/...）。建議改用套件匯出路徑或別名，以維持可維護性。

**判斷依據**：diff 中新增的相對路徑匯入，跨越了多個目錄層級。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13571 (cache hit 13568) ｜ completion tokens 1244 ｜ PR #9</sub>