<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於移動後 import 路徑的正確性、潛在的循環依賴、以及 sortHosts 函式移動時邏輯被意外變更。建議優先修正 sortHosts 的排序邏輯，並確認所有移動後的 import 路徑皆可正確解析。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式移動時排序邏輯被意外變更 | 0.95 |
| ⚠️ | Major | `apps/web/modules/bookings/components/BookerWebWrapper.tsx:42` | 移除 useRouter 後仍使用 router 變數 | 0.80 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 相對 import 路徑可能不正確 | 0.70 |
| ⚠️ | Major | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52` | 動態 import 路徑可能不正確 | 0.70 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | 檔案結尾缺少換行符號 | 0.90 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | 檔案結尾缺少換行符號 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式移動時排序邏輯被意外變更</summary>

在將 sortHosts 從 HostEditDialogs.tsx 移至 hostGroupUtils.ts 的過程中，當 isRRWeightsEnabled 為 true 且 weightA === weightB 時，回傳值從原本的 `priorityB - priorityA` 變成了 `priorityA - priorityB`，這會反轉相同權重下的優先順序，可能導致主機選擇錯誤。請改回 `priorityB - priorityA`。

**判斷依據**：diff 中新增的 sortHosts 函式內，該行與原始 HostEditDialogs.tsx 中刪除的 `return priorityB - priorityA;` 不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/bookings/components/BookerWebWrapper.tsx:42</code> 移除 useRouter 後仍使用 router 變數</summary>

在 BookerWebWrapper.tsx 中，原本的 `const router = useRouter();` 被移除，但後續程式碼仍多次使用 `router.push(...)`（例如 onOverlaySwitchStateChange、onConnectNowInstantMeeting 等）。這會導致執行時 ReferenceError。請確認是否應改用其他導航方式，或重新引入 useRouter。

**判斷依據**：diff 中刪除了 `const router = useRouter();`，但下方多處仍呼叫 `router.push`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 相對 import 路徑可能不正確</summary>

檔案從 packages/platform/atoms/destination-calendar/wrappers/ 移至 apps/web/components/apps/ 後，原本的 `../../src/components/atoms-wrapper` 改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper`。請確認此相對路徑能正確解析到目標檔案，否則會導致建置失敗。

**判斷依據**：diff 中 import 路徑變更，需驗證實際檔案位置。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52</code> 動態 import 路徑可能不正確</summary>

多個動態 import 從絕對路徑改為相對路徑，例如 `./tabs/setup/EventSetupTabWebWrapper`。請確認這些檔案確實存在於對應的相對路徑下，否則會導致 runtime 載入失敗。

**判斷依據**：diff 中多處動態 import 路徑變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> 檔案結尾缺少換行符號</summary>

檔案最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號，可能導致某些工具或 lint 規則發出警告。建議補上換行。

**判斷依據**：diff 中顯示 `\ No newline at end of file`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> 檔案結尾缺少換行符號</summary>

檔案最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號，可能導致某些工具或 lint 規則發出警告。建議補上換行。

**判斷依據**：diff 中顯示 `\ No newline at end of file`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16657 (cache hit 16640) ｜ completion tokens 1272 ｜ PR #9</sub>