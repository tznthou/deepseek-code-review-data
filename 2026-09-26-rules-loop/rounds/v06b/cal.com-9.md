<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於移動後可能造成循環依賴（apps/web 與 packages/platform 之間）、路徑錯誤、以及 sortHosts 函式移動時邏輯被意外修改。建議優先確認 import 路徑正確性與 sortHosts 的排序邏輯是否與原版一致。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | Import 路徑可能錯誤：使用相對路徑指向 packages/platform | 0.80 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:4` | Import 路徑可能錯誤：使用相對路徑指向 packages/platform | 0.80 |
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式邏輯可能被意外修改 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29` | Import 路徑可能造成循環依賴 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:30` | Import 路徑可能造成循環依賴 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:31` | Import 路徑可能造成循環依賴 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/assignment/EventTeamAssignmentTab.tsx:17` | Import 路徑變更可能造成循環依賴 | 0.60 |
| 🔸 | Minor | `packages/platform/atoms/package.json:57` | 移除 exports 可能導致外部 import 失敗 | 0.50 |
| 🔹 | Nit | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | 縮排不一致 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> Import 路徑可能錯誤：使用相對路徑指向 packages/platform</summary>

此檔案從 packages/platform/atoms 移至 apps/web/components/apps 後，import 路徑改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper`。請確認此相對路徑能正確解析到目標檔案。若路徑錯誤，將導致建置失敗或 runtime 錯誤。建議改用絕對路徑（如 `@calcom/atoms/...`）或確認相對路徑正確。

**判斷依據**：diff 中顯示 import 路徑從 `../../src/components/atoms-wrapper` 改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper`，但檔案位置已從 packages/platform/atoms/destination-calendar/wrappers 移至 apps/web/components/apps，相對路徑的層數可能不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:4</code> Import 路徑可能錯誤：使用相對路徑指向 packages/platform</summary>

此檔案從 packages/platform/atoms 移至 apps/web/components/apps 後，import 路徑改為 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`。請確認此相對路徑能正確解析到目標檔案。若路徑錯誤，將導致建置失敗或 runtime 錯誤。建議改用絕對路徑（如 `@calcom/atoms/...`）或確認相對路徑正確。

**判斷依據**：diff 中顯示 import 路徑從 `../DestinationCalendar` 改為 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`，但檔案位置已從 packages/platform/atoms/destination-calendar/wrappers 移至 apps/web/components/apps，相對路徑的層數可能不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式邏輯可能被意外修改</summary>

在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，權重相等時的回傳值從 `priorityB - priorityA` 改為 `priorityA - priorityB`。這會反轉排序順序，可能導致 host 排序錯誤。請確認此修改是否為預期行為，若非預期請修正。

**判斷依據**：diff 中顯示原本在 HostEditDialogs.tsx 的 sortHosts 函式在 weightA === weightB 時回傳 `priorityB - priorityA`，但移動後變成 `priorityA - priorityB`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29</code> Import 路徑可能造成循環依賴</summary>

此檔案從 `@calcom/atoms/event-types/hooks/useEventTypeForm` 等路徑 import hooks，但該 hooks 檔案仍位於 packages/platform/atoms 中，且可能 import 自此檔案（或相關檔案），形成循環依賴。請確認 import 關係是否會造成循環。

**判斷依據**：diff 中顯示此檔案從 `@calcom/atoms/event-types/hooks/useEventTypeForm` import，而該 hook 檔案可能依賴於此檔案或其他 apps/web 模組，形成循環。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:30</code> Import 路徑可能造成循環依賴</summary>

此檔案從 `@calcom/atoms/event-types/hooks/useHandleRouteChange` 等路徑 import hooks，但該 hooks 檔案仍位於 packages/platform/atoms 中，且可能 import 自此檔案（或相關檔案），形成循環依賴。請確認 import 關係是否會造成循環。

**判斷依據**：diff 中顯示此檔案從 `@calcom/atoms/event-types/hooks/useHandleRouteChange` import，而該 hook 檔案可能依賴於此檔案或其他 apps/web 模組，形成循環。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:31</code> Import 路徑可能造成循環依賴</summary>

此檔案從 `@calcom/atoms/event-types/hooks/useTabsNavigations` 等路徑 import hooks，但該 hooks 檔案仍位於 packages/platform/atoms 中，且可能 import 自此檔案（或相關檔案），形成循環依賴。請確認 import 關係是否會造成循環。

**判斷依據**：diff 中顯示此檔案從 `@calcom/atoms/event-types/hooks/useTabsNavigations` import，而該 hook 檔案可能依賴於此檔案或其他 apps/web 模組，形成循環。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/assignment/EventTeamAssignmentTab.tsx:17</code> Import 路徑變更可能造成循環依賴</summary>

此檔案將 `sortHosts` 的 import 從 `@calcom/web/modules/event-types/components/HostEditDialogs` 改為 `@calcom/lib/bookings/hostGroupUtils`。請確認 `hostGroupUtils` 是否會反向依賴此檔案，造成循環。

**判斷依據**：diff 中顯示 import 路徑變更，但未提供 hostGroupUtils 的內容，無法確認是否會造成循環依賴。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:57</code> 移除 exports 可能導致外部 import 失敗</summary>

此 PR 從 package.json 的 exports 中移除了多個路徑（如 `./add-members-switch/AddMembersWithSwitchWebWrapper`、`./connect/conferencing-apps/ConferencingAppsViewWebWrapper` 等）。若其他套件或應用程式仍使用這些路徑 import，將導致建置失敗。請確認所有使用這些路徑的程式碼都已更新。

**判斷依據**：diff 中顯示多個 exports 被移除，但未提供所有使用這些路徑的程式碼是否已更新。

</details>

<details><summary>🔹 <b>Nit</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> 縮排不一致</summary>

在 tabMap 的 setup 和 availability 區塊中，縮排從原本的 6 空格改為 8 空格，與其他區塊不一致。建議統一縮排以符合程式碼風格。

**判斷依據**：diff 中顯示縮排從 6 空格改為 8 空格，但其他 tab 區塊仍使用 6 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13561 (cache hit 13440) ｜ completion tokens 2298 ｜ PR #9</sub>