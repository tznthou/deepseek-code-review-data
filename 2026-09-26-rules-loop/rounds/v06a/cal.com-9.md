<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於移動後可能造成循環依賴（apps/web 與 packages/platform/atoms 之間），以及 sortHosts 函式在移動時邏輯被意外修改（優先權比較方向反轉）。此外，部分檔案缺少結尾換行、import 路徑使用相對路徑可能違反專案慣例。建議先修正 sortHosts 邏輯與循環依賴問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時邏輯被修改，優先權比較方向反轉 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | [R02] 從 apps/web 使用相對路徑 import packages/platform/atoms，可能造成循環依賴 | 0.80 |
| ⚠️ | Major | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29` | [R02] 從 apps/web 使用 @calcom/atoms 路徑 import hooks，可能造成循環依賴 | 0.75 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | [R03] JSX 縮排不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時邏輯被修改，優先權比較方向反轉</summary>

在 `HostEditDialogs.tsx` 中的原始 `sortHosts` 函式，當 `isRRWeightsEnabled` 為 true 且權重相同時，回傳 `priorityB - priorityA`（降冪排序）。移動到 `hostGroupUtils.ts` 後，該分支變成 `priorityA - priorityB`（升冪排序），導致排序結果相反。這會影響依賴此排序的團隊成員指派邏輯，可能造成優先權最高的成員被排到最後。

建議：將該行改回 `return priorityB - priorityA;` 以維持原始行為。

**判斷依據**：diff 中 `packages/lib/bookings/hostGroupUtils.ts` 新增的 `sortHosts` 函式，在 `isRRWeightsEnabled` 且權重相等時回傳 `priorityA - priorityB`，而原始 `HostEditDialogs.tsx` 中對應行為是 `priorityB - priorityA`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> [R02] 從 apps/web 使用相對路徑 import packages/platform/atoms，可能造成循環依賴</summary>

此檔案位於 `apps/web/components/apps/`，卻使用相對路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar` 來 import 平台 atoms 套件。這打破了 apps/web 與 packages/platform/atoms 之間的依賴方向（apps/web 應依賴 atoms，但 atoms 不應依賴 apps/web）。若 atoms 內部也 import apps/web 的模組，將形成循環依賴，可能導致建置失敗或 runtime 錯誤。

建議：改用 package alias（如 `@calcom/atoms/...`）來 import，並確認 atoms 套件沒有反向依賴 apps/web。

**判斷依據**：diff 中 `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx` 的 import 路徑改為相對路徑，指向 `packages/platform/atoms`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29</code> [R02] 從 apps/web 使用 @calcom/atoms 路徑 import hooks，可能造成循環依賴</summary>

此檔案位於 `apps/web/modules/event-types/components/`，卻 import `@calcom/atoms/event-types/hooks/useEventTypeForm`、`useHandleRouteChange`、`useTabsNavigations`。這些 hooks 原本位於 `packages/platform/atoms/event-types/wrappers/` 下，現在被 apps/web 直接引用。若這些 hooks 內部依賴 apps/web 的模組，將形成循環依賴。

建議：確認這些 hooks 沒有反向依賴 apps/web，或考慮將它們移至共享套件（如 `@calcom/features`）。

**判斷依據**：diff 中 `EventTypeWebWrapper.tsx` 新增了從 `@calcom/atoms` 的 hooks import。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾缺少換行符（newline at end of file），違反常見的程式碼風格規範，可能導致某些工具或 diff 顯示異常。

建議：在檔案最後一行加上換行符。

**判斷依據**：diff 顯示 `EventLimitsTabWebWrapper.tsx` 的最後一行沒有換行符（`\ No newline at end of file`）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾缺少換行符（newline at end of file），違反常見的程式碼風格規範，可能導致某些工具或 diff 顯示異常。

建議：在檔案最後一行加上換行符。

**判斷依據**：diff 顯示 `EventRecurringWebWrapper.tsx` 的最後一行沒有換行符（`\ No newline at end of file`）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> [R03] JSX 縮排不一致</summary>

在 `tabMap` 物件中，`setup` 和 `availability` 的 JSX 元素縮排從原本的 6 空格改為 8 空格，但其他 tab 仍維持 6 空格，造成不一致。雖然不影響功能，但違反一致的格式化風格。

建議：統一縮排為 6 空格，或使用 Biome 自動格式化。

**判斷依據**：diff 中 `EventTypeWebWrapper.tsx` 的 `tabMap` 區塊，`setup` 和 `availability` 的縮排被改為 8 空格，而其他 tab 仍為 6 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13561 (cache hit 12032) ｜ completion tokens 1826 ｜ PR #9</sub>