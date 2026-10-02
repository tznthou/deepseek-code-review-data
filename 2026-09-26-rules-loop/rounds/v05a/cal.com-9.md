<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 遷移至 apps/web/modules，並調整相關 import 路徑。主要風險在於 sortHosts 函式在移動時邏輯被意外修改（priority 排序方向反轉），可能導致主持人排序錯誤。此外，部分 import 路徑改為相對路徑，增加未來重構的脆弱性，且未更新相關測試。建議先修正 sortHosts 邏輯並補充測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時 priority 排序方向被反轉 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑跨多層目錄引用 packages/platform 下的模組 | 0.80 |
| ⚠️ | Major | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:27` | import 路徑從 alias 改為相對路徑，降低可維護性 | 0.75 |
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:41` | sortHosts 函式缺少單元測試 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236` | JSX 縮排不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時 priority 排序方向被反轉</summary>

在 `isRRWeightsEnabled` 為 true 且權重相同時，原本的排序是 `priorityB - priorityA`（降冪），但移動後變成 `priorityA - priorityB`（升冪）。這會導致主持人優先級排序完全相反，可能造成錯誤的主持人指派。請改回 `priorityB - priorityA`。

**判斷依據**：diff 中新增的 sortHosts 函式內，該行與刪除的原始碼 `return priorityB - priorityA;` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑跨多層目錄引用 packages/platform 下的模組</summary>

import 路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar` 非常脆弱，一旦檔案移動就容易斷裂。建議改用 alias（如 `@calcom/atoms/...`）或絕對路徑。

**判斷依據**：diff 中新增的相對路徑 import。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:27</code> import 路徑從 alias 改為相對路徑，降低可維護性</summary>

多個原本使用 `@calcom/web/...` 的 import 改為相對路徑（如 `./EventType`、`./ChildrenEventTypeSelect`）。雖然目前可運作，但未來若檔案移動，相對路徑容易失效，且與專案慣用 alias 的風格不一致。建議保留 alias 或使用絕對路徑。

**判斷依據**：diff 中多處將 `@calcom/web/modules/event-types/components/...` 改為 `./...`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:41</code> sortHosts 函式缺少單元測試</summary>

此函式被移動且邏輯有變更，但未見對應的測試更新或新增。建議為 sortHosts 撰寫單元測試，涵蓋不同權重、優先級組合以及 isRRWeightsEnabled 的各種情況。

**判斷依據**：diff 中新增 sortHosts 函式，但未見測試檔案變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:236</code> JSX 縮排不一致</summary>

在 tabMap 的 setup 和 availability 區塊中，JSX 元素的縮排從原本的 6 空格改為 8 空格，與其他 tab 的縮排不一致。建議統一縮排以符合程式碼風格。

**判斷依據**：diff 中顯示縮排由 6 空格改為 8 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13540 (cache hit 12032) ｜ completion tokens 1177 ｜ PR #9</sub>