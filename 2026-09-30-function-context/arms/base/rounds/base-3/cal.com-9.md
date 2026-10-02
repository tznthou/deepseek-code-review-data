<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 sortHosts 函式在移動時邏輯被意外變更（priority 排序方向反轉），可能導致主持人排序錯誤。此外，部分 import 路徑改為相對路徑，增加未來維護成本，且部分檔案缺少結尾換行。整體而言，重構方向合理，但需修正排序邏輯並確認所有 import 路徑正確。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時 priority 排序方向被反轉 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑 import 跨 package 的模組，增加耦合與維護成本 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:27` | import 路徑混用相對路徑與 package alias，不一致 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | 檔案缺少結尾換行 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | 檔案缺少結尾換行 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時 priority 排序方向被反轉</summary>

在 `isRRWeightsEnabled` 為 true 且權重相同時，原本的程式碼回傳 `priorityB - priorityA`（降冪），但移動後變成 `priorityA - priorityB`（升冪）。這會導致主持人排序結果相反，可能影響輪流主持（round-robin）的權重分配。請改回 `priorityB - priorityA`。

**判斷依據**：diff 中 `packages/lib/bookings/hostGroupUtils.ts` 新增的 `sortHosts` 函式，在 `weightA === weightB` 分支回傳 `priorityA - priorityB`，而原始 `apps/web/modules/event-types/components/HostEditDialogs.tsx` 中對應的程式碼為 `priorityB - priorityA`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑 import 跨 package 的模組，增加耦合與維護成本</summary>

此檔案從 `packages/platform/atoms` 移至 `apps/web/components/apps` 後，改用相對路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar` 來 import。這會讓 apps/web 直接依賴 packages/platform 的內部檔案結構，未來若 packages/platform 調整路徑，此處容易斷裂。建議改用 package exports 或 alias。

**判斷依據**：diff 中 `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx` 的 import 路徑改為相對路徑，跨越多層目錄指向 packages/platform。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:27</code> import 路徑混用相對路徑與 package alias，不一致</summary>

此檔案中部分 import 使用相對路徑（如 `./ChildrenEventTypeSelect`、`./EventType`），但 hooks 仍使用 `@calcom/atoms/event-types/hooks/...`。雖然功能上可能正常，但風格不一致，建議統一使用 alias 或相對路徑。

**判斷依據**：diff 中 `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx` 的 import 區塊同時出現相對路徑與 `@calcom/atoms` alias。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> 檔案缺少結尾換行</summary>

檔案最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

**判斷依據**：diff 中 `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx` 的最後一行顯示 `\ No newline at end of file`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> 檔案缺少結尾換行</summary>

檔案最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

**判斷依據**：diff 中 `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx` 的最後一行顯示 `\ No newline at end of file`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12132 (cache hit 12032) ｜ completion tokens 1393 ｜ PR #9</sub>