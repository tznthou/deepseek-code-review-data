<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web 下的對應模組，並更新所有匯入路徑。主要風險在於 sortHosts 函式在移動時被意外修改了排序邏輯（priority 比較方向反轉），可能導致主機排序錯誤。此外，部分匯入路徑改為相對路徑，增加未來重構的耦合度，但尚不構成阻擋。整體而言，重構方向合理，但需修正 sortHosts 的邏輯回歸。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式在移動時被意外修改，priority 比較方向反轉 | 0.95 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑匯入跨 package 的模組，增加耦合 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式在移動時被意外修改，priority 比較方向反轉</summary>

在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，原本的 `return priorityB - priorityA;` 被改成了 `return priorityA - priorityB;`（在 `isRRWeightsEnabled` 為 true 且權重相等時）。這會反轉優先權排序，可能導致主機選擇錯誤。

**失敗情境**：當啟用 RR 權重且兩個主機權重相同時，優先權較低（數值較大）的主機會被排在前面，違反預期。

**建議**：將該行改回 `return priorityB - priorityA;`，與原始邏輯一致。

**判斷依據**：diff 中新增的 sortHosts 函式內，`if (weightA === weightB) { return priorityA - priorityB; }`，而原始程式碼（HostEditDialogs.tsx 中被刪除的版本）為 `return priorityB - priorityA;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑匯入跨 package 的模組，增加耦合</summary>

此檔案從 `packages/platform/atoms` 移至 `apps/web/components/apps` 後，匯入 `AtomsWrapper` 和 `DestinationCalendarSettings` 改為相對路徑 `../../../../packages/platform/atoms/...`。這會讓 apps/web 直接依賴 packages/platform 的內部檔案結構，未來若 packages/platform 調整路徑，此處需同步修改。建議考慮使用 package exports 或 alias 來維持模組邊界。

**判斷依據**：diff 中將原本的 `@calcom/atoms` 匯入改為相對路徑，跨越了 package 邊界。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12132 (cache hit 1536) ｜ completion tokens 748 ｜ PR #9</sub>