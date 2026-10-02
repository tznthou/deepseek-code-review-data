<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移動到 apps/web 下的對應模組，並更新所有匯入路徑。整體而言，重構方向合理，但存在一個關鍵的邏輯變更：sortHosts 函式在移動到 packages/lib 時，其優先權比較邏輯被意外反轉（priorityA - priorityB 改為 priorityB - priorityA），這可能導致主機排序錯誤。此外，部分檔案缺少結尾換行、匯入路徑使用相對路徑可能違反專案慣例，以及刪除的公開匯出可能影響外部使用者。建議先修正 sortHosts 的邏輯錯誤，再處理其他次要問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:53` | sortHosts 函式優先權比較邏輯被反轉 | 0.95 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8` | [R03] 檔案結尾缺少換行符 | 0.80 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑匯入跨套件模組 | 0.60 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除公開匯出可能造成 breaking change | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:53</code> sortHosts 函式優先權比較邏輯被反轉</summary>

在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，原本的 `return priorityB - priorityA;` 被改成了 `return priorityA - priorityB;`。這會導致當權重相同時，主機的排序順序完全相反，可能影響依賴此排序的功能（例如指派主機的優先順序）。請將該行改回 `return priorityB - priorityA;`。

**判斷依據**：diff 中新增的 sortHosts 函式內，在 isRRWeightsEnabled 且 weightA === weightB 的分支中，回傳值由原本的 priorityB - priorityA 變為 priorityA - priorityB。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾缺少換行符（newline at end of file），這可能違反專案的格式化規範（Biome 通常會要求）。建議在最後一行後加上換行。

**判斷依據**：diff 顯示該行結尾沒有換行符號（\ No newline at end of file）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8</code> [R03] 檔案結尾缺少換行符</summary>

檔案結尾缺少換行符（newline at end of file），這可能違反專案的格式化規範（Biome 通常會要求）。建議在最後一行後加上換行。

**判斷依據**：diff 顯示該行結尾沒有換行符號（\ No newline at end of file）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑匯入跨套件模組</summary>

此檔案使用相對路徑 `../../../../packages/platform/atoms/...` 匯入其他套件的模組，這可能違反專案對匯入路徑的慣例（通常使用別名如 `@calcom/...`）。建議改用套件別名以維持一致性與可維護性。

**判斷依據**：diff 中新增的匯入使用相對路徑，而其他匯入多使用 `@calcom/` 別名。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除公開匯出可能造成 breaking change</summary>

從 `package.json` 的 exports 中移除了多個路徑（如 `./add-members-switch/AddMembersWithSwitchWebWrapper`、`./booker` 等），這可能導致依賴這些路徑的外部套件無法再匯入。若這些路徑是公開 API，應考慮保留或提供替代方案。

**判斷依據**：diff 顯示多個 exports 條目被刪除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12756 (cache hit 12672) ｜ completion tokens 1191 ｜ PR #9</sub>