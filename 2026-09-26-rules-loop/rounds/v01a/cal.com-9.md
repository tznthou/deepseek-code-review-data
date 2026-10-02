<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web 下的對應模組，並更新所有匯入路徑。主要風險在於移動後可能造成循環依賴（apps/web 與 packages/platform/atoms 之間）、違反預設匯出規範（R04），以及 sortHosts 函式移動後排序邏輯的變更。建議優先確認循環依賴與排序行為，並修正預設匯出問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 潛在循環依賴：apps/web 匯入 packages/platform/atoms | 0.80 |
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 排序邏輯變更可能影響行為 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R04] 非 page/layout 檔案使用 default export | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R04] 非 page/layout 檔案使用 default export | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:235` | 縮排不一致可能違反格式化規範 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 潛在循環依賴：apps/web 匯入 packages/platform/atoms</summary>

此檔案從 `packages/platform/atoms` 匯入 `AtomsWrapper` 與 `DestinationCalendarSettings`，但該檔案本身位於 `apps/web`。若 `packages/platform/atoms` 反向依賴 `apps/web`（例如透過其他元件），將形成循環依賴，可能導致建置失敗或執行時期錯誤。建議確認依賴方向，或將共用元件移至更低層的套件。

**判斷依據**：diff 顯示此檔案從 packages/platform/atoms 移至 apps/web/components/apps，但保留對 packages/platform/atoms 的匯入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 排序邏輯變更可能影響行為</summary>

在 `isRRWeightsEnabled` 且權重相同時，原本回傳 `priorityB - priorityA`（降冪），現在改為 `priorityA - priorityB`（升冪）。這會反轉優先權排序，可能導致指派主機的順序錯誤。請確認此變更是否為預期，並更新相關測試。

**判斷依據**：diff 顯示原本在 HostEditDialogs.tsx 中的 sortHosts 回傳 priorityB - priorityA，移動後改為 priorityA - priorityB。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R04] 非 page/layout 檔案使用 default export</summary>

此檔案使用 `export default EventLimitsTabWebWrapper;`，但位於 `apps/web/modules/...`，不符合 R04 規範（僅 Next.js page/layout 檔案可使用 default export）。請改為 named export 並更新匯入。

**判斷依據**：diff 顯示此檔案結尾為 default export，且路徑不符合允許 default export 的 pattern。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R04] 非 page/layout 檔案使用 default export</summary>

此檔案使用 `export default EventRecurringWebWrapper;`，但位於 `apps/web/modules/...`，不符合 R04 規範。請改為 named export 並更新匯入。

**判斷依據**：diff 顯示此檔案結尾為 default export，且路徑不符合允許 default export 的 pattern。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:235</code> 縮排不一致可能違反格式化規範</summary>

在 `tabMap` 物件中，`setup` 與 `availability` 的 JSX 縮排從原本的 6 空格改為 8 空格，與其他 tab 不一致。這可能違反 R03 的格式化規範，建議執行 Biome 格式化。

**判斷依據**：diff 顯示縮排從 6 空格改為 8 空格，且其他 tab 仍維持 6 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13571 (cache hit 12032) ｜ completion tokens 1215 ｜ PR #9</sub>