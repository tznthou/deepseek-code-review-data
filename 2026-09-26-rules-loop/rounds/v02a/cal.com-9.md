<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於移動後可能違反 R02 的依賴方向（apps/web 反向依賴 packages/platform/atoms），以及 sortHosts 函式移動後邏輯變更（priority 排序方向反轉）可能造成行為差異。此外，部分檔案缺少結尾換行、import 路徑使用相對路徑可能影響可維護性。建議優先確認 sortHosts 的排序邏輯是否為預期變更，並檢查所有移動後的 import 是否正確。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式移動後 priority 排序方向反轉 | 0.80 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | [R02] 移動後 import 路徑違反依賴方向 | 0.75 |
| ⚠️ | Major | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29` | [R02] 移動後 import 路徑違反依賴方向 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案缺少結尾換行 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案缺少結尾換行 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | 縮排不一致可能違反格式化規則 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式移動後 priority 排序方向反轉</summary>

在 HostEditDialogs.tsx 中的原始 sortHosts 函式，當 isRRWeightsEnabled 為 false 時回傳 `priorityB - priorityA`（降冪排序）。移動到 hostGroupUtils.ts 後，相同分支改為回傳 `priorityA - priorityB`（升冪排序）。這會改變排序結果，可能影響依賴此排序的 UI 或邏輯。請確認此變更是否為預期，若非預期請修正為原始行為。

**判斷依據**：diff 中 packages/lib/bookings/hostGroupUtils.ts 新增的 sortHosts 函式，在 else 分支回傳 priorityA - priorityB，而原始 HostEditDialogs.tsx 中相同分支回傳 priorityB - priorityA。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> [R02] 移動後 import 路徑違反依賴方向</summary>

此檔案從 packages/platform/atoms 移至 apps/web/components/apps 後，import 路徑改為相對路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`。這表示 apps/web 直接依賴 packages/platform/atoms 的內部檔案，可能違反 R02 的依賴階層（apps/web 不應直接依賴 packages/platform/atoms 的內部實作）。建議改為使用公開的 package export 或將相依元件一併移動。

**判斷依據**：diff 中此檔案的 import 路徑從原本的 package alias 改為相對路徑，指向 packages/platform/atoms 內部。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:29</code> [R02] 移動後 import 路徑違反依賴方向</summary>

此檔案從 packages/platform/atoms 移至 apps/web/modules/event-types/components 後，仍從 `@calcom/atoms/event-types/hooks/...` import hooks。這表示 apps/web 依賴 packages/platform/atoms 的 hooks，可能違反 R02 的依賴階層。建議將這些 hooks 一併移動至 apps/web 或確認此依賴是否被允許。

**判斷依據**：diff 中此檔案的 import 路徑仍使用 @calcom/atoms 的 hooks。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案缺少結尾換行</summary>

此檔案在最後一行 `export default EventLimitsTabWebWrapper;` 後缺少換行符號（`\ No newline at end of file`）。這可能違反 Biome 的格式化規則，建議補上換行。

**判斷依據**：diff 中此檔案最後一行顯示 `\ No newline at end of file`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案缺少結尾換行</summary>

此檔案在最後一行 `export default EventRecurringWebWrapper;` 後缺少換行符號（`\ No newline at end of file`）。這可能違反 Biome 的格式化規則，建議補上換行。

**判斷依據**：diff 中此檔案最後一行顯示 `\ No newline at end of file`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> 縮排不一致可能違反格式化規則</summary>

在 tabMap 的 setup 和 availability 區塊中，JSX 元素的縮排從原本的 6 空格改為 8 空格，與其他 tab 的縮排不一致。這可能違反 Biome 的格式化規則，建議統一縮排。

**判斷依據**：diff 中此區塊的縮排從 6 空格改為 8 空格，而其他 tab 仍為 6 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13571 (cache hit 1536) ｜ completion tokens 1600 ｜ PR #9</sub>