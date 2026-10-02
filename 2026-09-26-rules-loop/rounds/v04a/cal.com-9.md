<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 import 路徑的正確性與模組解析，尤其是 DestinationCalendarSettingsWebWrapper 使用了相對路徑指向 packages/platform，可能造成架構反向依賴。此外，sortHosts 函式在移動時邏輯被意外修改，可能影響排序行為。建議優先修正 sortHosts 的邏輯差異，並確認所有 import 路徑在實際建置中可解析。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式邏輯在移動時被修改 | 0.90 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑 import packages/platform 可能造成反向依賴 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:28` | import 路徑混用相對與絕對路徑，可能造成混淆 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | 檔案結尾缺少換行符號 | 0.60 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | 檔案結尾缺少換行符號 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式邏輯在移動時被修改</summary>

在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，當 `isRRWeightsEnabled` 為 true 且權重相同時，回傳值從 `priorityB - priorityA` 改為 `priorityA - priorityB`，導致排序方向相反。這會影響依賴此函式的排序結果（例如主持人清單的顯示順序）。請確認此變更是否為預期，若非預期請修正為原始邏輯。

**判斷依據**：diff 中原始程式碼為 `return priorityB - priorityA;`，新程式碼為 `return priorityA - priorityB;`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑 import packages/platform 可能造成反向依賴</summary>

此檔案從 `packages/platform/atoms` 移至 `apps/web/components/apps` 後，import 路徑改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar`。這代表 `apps/web` 直接依賴 `packages/platform` 的內部檔案，可能違反架構分層（apps 應依賴 packages 的公開 API，而非內部路徑）。建議改為使用 `@calcom/atoms` 套件的公開 export，或將相關元件一併移至 `apps/web`。

**判斷依據**：diff 顯示 import 路徑從 `../../src/components/atoms-wrapper` 改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:28</code> import 路徑混用相對與絕對路徑，可能造成混淆</summary>

此檔案中同時使用相對路徑（如 `./EventType`）與絕對路徑（如 `@calcom/atoms/event-types/hooks/useEventTypeForm`）來 import 鄰近模組。雖然功能上可能正常，但風格不一致可能增加維護困難。建議統一使用相對路徑或絕對路徑（視專案慣例）。

**判斷依據**：diff 顯示新增了 `./EventType` 的相對 import，同時保留了 `@calcom/atoms/...` 的絕對 import。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> 檔案結尾缺少換行符號</summary>

檔案最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號，可能導致某些工具或 diff 顯示異常。建議在檔案結尾加上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> 檔案結尾缺少換行符號</summary>

檔案最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號，可能導致某些工具或 diff 顯示異常。建議在檔案結尾加上換行。

**判斷依據**：diff 顯示 `\ No newline at end of file`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12756 (cache hit 12032) ｜ completion tokens 1288 ｜ PR #9</sub>