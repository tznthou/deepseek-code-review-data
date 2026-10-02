<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 sortHosts 函式在移動時被意外修改了排序邏輯（priority 比較方向反轉），可能導致主持人排序錯誤。此外，部分 import 路徑改為相對路徑，增加未來重構的耦合度。建議先修正 sortHosts 的邏輯，再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時被意外修改，priority 比較方向反轉 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑 import 跨 package 的模組，增加耦合 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52` | 動態 import 路徑改為相對路徑，可能導致建置或執行時錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時被意外修改，priority 比較方向反轉</summary>

在 `isRRWeightsEnabled` 為 true 且 weight 相同時，原本的排序是 `priorityB - priorityA`（降冪），但移動後變成 `priorityA - priorityB`（升冪）。這會導致主持人排序結果相反，可能影響 round-robin 權重分配。請改回 `priorityB - priorityA`。

**判斷依據**：diff 中新增的 sortHosts 函式內，該行與原 HostEditDialogs.tsx 中的 `return priorityB - priorityA;` 不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑 import 跨 package 的模組，增加耦合</summary>

此檔案從 `packages/platform/atoms` 移至 `apps/web/components/apps` 後，改用相對路徑 `../../../../packages/platform/atoms/...` 來 import。這會讓 apps/web 直接依賴 packages/platform 的內部結構，未來若 packages/platform 調整路徑，此處容易斷裂。建議改用 package alias（如 `@calcom/atoms/...`）或將相依模組一併移至 apps/web。

**判斷依據**：diff 顯示 import 路徑從 `../../src/components/atoms-wrapper` 改為 `../../../../packages/platform/atoms/src/components/atoms-wrapper`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52</code> 動態 import 路徑改為相對路徑，可能導致建置或執行時錯誤</summary>

多個 dynamic import 從絕對 alias 改為相對路徑（如 `./tabs/setup/EventSetupTabWebWrapper`）。若目標檔案不存在或路徑錯誤，會在執行時才拋出錯誤。請確認所有相對路徑皆正確，並考慮保留 alias 以利維護。

**判斷依據**：diff 中多處 dynamic import 路徑由 `@calcom/web/modules/...` 改為 `./...`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12132 (cache hit 12032) ｜ completion tokens 871 ｜ PR #9</sub>