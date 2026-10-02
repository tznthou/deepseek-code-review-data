<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於移動後可能造成循環依賴（apps/web 與 packages/platform/atoms 之間）、路徑錯誤、以及 sortHosts 函式邏輯變更。建議優先確認循環依賴與 sortHosts 行為。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 移動後 import 路徑可能造成循環依賴 | 0.80 |
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式邏輯變更可能影響排序結果 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:61` | 動態 import 路徑可能不正確 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | 縮排不一致 | 0.50 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | 檔案結尾缺少換行符 | 0.50 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | 檔案結尾缺少換行符 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 移動後 import 路徑可能造成循環依賴</summary>

此檔案從 packages/platform/atoms 移至 apps/web/components/apps，但 import 了 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 與 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`。這代表 apps/web 直接依賴 packages/platform/atoms 的內部路徑，而 packages/platform/atoms 可能也依賴 apps/web（例如其他 wrapper），形成循環依賴。建議改為使用公開的 package exports（如 `@calcom/atoms/...`）或將 AtomsWrapper 與 DestinationCalendarSettings 一併移至 apps/web。

**判斷依據**：diff 中新增的 import 路徑指向 packages/platform/atoms 的內部檔案，而非公開 API。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式邏輯變更可能影響排序結果</summary>

原本在 HostEditDialogs.tsx 中的 sortHosts 在 weight 相等時回傳 `priorityB - priorityA`，但移動後改為 `priorityA - priorityB`，排序方向相反。這可能導致 host 優先順序錯誤。請確認此變更是否為預期，並補充測試。

**判斷依據**：diff 顯示 `return priorityB - priorityA;` 被改為 `return priorityA - priorityB;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:61</code> 動態 import 路徑可能不正確</summary>

`EventTeamAssignmentTab` 的動態 import 從 `./EventTeamAssignmentTabWebWrapper` 改為 `./tabs/assignment/EventTeamAssignmentTabWebWrapper`，但該檔案實際位於 `apps/web/modules/event-types/components/tabs/assignment/EventTeamAssignmentTabWebWrapper.tsx`，相對路徑應為 `./tabs/assignment/EventTeamAssignmentTabWebWrapper`，此處正確。但需確認其他動態 import 路徑是否皆正確。

**判斷依據**：diff 中此行的 import 路徑變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> 縮排不一致</summary>

在 tabMap 的 JSX 中，`<EventSetupTab>` 與 `<EventAvailabilityTab>` 的縮排從原本的 6 空格改為 8 空格，與其他 tab 不一致。建議使用 Biome 格式化。

**判斷依據**：diff 顯示縮排變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> 檔案結尾缺少換行符</summary>

檔案結尾的 `export default EventLimitsTabWebWrapper;` 後缺少換行符，可能導致 lint 警告。建議補上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> 檔案結尾缺少換行符</summary>

檔案結尾的 `export default EventRecurringWebWrapper;` 後缺少換行符，可能導致 lint 警告。建議補上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13581 (cache hit 12032) ｜ completion tokens 1354 ｜ PR #9</sub>