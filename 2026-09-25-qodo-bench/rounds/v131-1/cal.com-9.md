<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 sortHosts 函式被移動至共用函式庫時，其排序邏輯在權重相等時被意外反轉（priorityA - priorityB 改為 priorityB - priorityA），可能導致主機排序錯誤。此外，部分 import 路徑改為相對路徑，增加未來重構的耦合度，但尚不構成立即問題。建議修正 sortHosts 的邏輯反轉後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式在權重相等時排序邏輯反轉 | 0.95 |
| 🔸 | Minor | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑導入跨 package 的模組 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式在權重相等時排序邏輯反轉</summary>

在 `isRRWeightsEnabled` 為 true 且 `weightA === weightB` 時，原本的實作回傳 `priorityB - priorityA`（優先權高者在前），但移動後的版本回傳 `priorityA - priorityB`，導致排序方向相反。這會影響依賴此函式的主機排序（例如 EventTeamAssignmentTab），可能造成優先權較低的主機被排在前面的錯誤。

建議修正為：
```ts
if (weightA === weightB) {
  return priorityB - priorityA;
}
```

**判斷依據**：diff 中新增的 sortHosts 函式，在 `weightA === weightB` 分支回傳 `priorityA - priorityB`，而原始檔案（HostEditDialogs.tsx）中相同分支回傳 `priorityB - priorityA`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑導入跨 package 的模組</summary>

此檔案從 `packages/platform/atoms` 移動到 `apps/web/components/apps` 後，使用相對路徑 `../../../../packages/platform/atoms/...` 導入 AtomsWrapper 和 DestinationCalendarSettings。這會增加與特定目錄結構的耦合，未來若調整目錄層級容易出錯。建議改用 alias（如 `@calcom/atoms/...`）以維持一致性。

**判斷依據**：diff 中顯示 import 路徑從原本的 alias 改為相對路徑。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12096 (cache hit 1408) ｜ completion tokens 719 ｜ PR #9</sub>