<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema 表單的陣列項目加入拖曳排序功能，使用 @dnd-kit 套件。主要風險在於拖曳排序的索引計算可能因 prefixItems 的存在而錯位，導致資料順序錯誤；此外，SortableContext 的 items 包含不可拖曳的 prefix 項目，可能造成拖曳行為異常。建議先修正索引計算邏輯，並考慮僅將可拖曳項目納入 SortableContext。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134` | 拖曳排序的索引計算未考慮 prefixItems，可能導致資料錯位 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖曳的 prefix 項目，可能導致拖曳行為異常 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134</code> 拖曳排序的索引計算未考慮 prefixItems，可能導致資料錯位</summary>

在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 預期的索引是相對於可移動項目（即排除 prefixItems 後）的索引。當陣列包含 prefixItems 時，拖曳非 prefix 項目會導致移動到錯誤的位置，造成資料順序錯誤。

例如：prefixItems 有 2 項，可移動項目從索引 2 開始。若將索引 2 的項目拖到索引 3，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會將項目移到可移動項目中的索引 3，實際上可能超出範圍或錯位。

建議：在計算索引時減去 `prefixItemsCount`，或改用可移動項目的相對索引。

**判斷依據**：diff 中 `handleDragEnd` 函式直接使用 `localKeyedValues` 的索引，而 `moveItem` 的實作（未在 diff 中顯示）可能假設索引是相對於可移動項目。同時，`prefixItemsCount` 已計算但未用於此處。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖曳的 prefix 項目，可能導致拖曳行為異常</summary>

`sortableKeys` 是 `localKeyedValues` 的所有 key，包括 prefixItems 對應的項目。但這些項目在 `SchemaFormInputArrayItem` 中因 `canMove` 為 false 而停用拖曳（`useSortable` 的 `disabled` 設為 true）。將停用的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過停用項目或碰撞偵測錯誤。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => index >= prefixItemsCount).map(item => item.key)`。

**判斷依據**：diff 中 `sortableKeys` 直接映射所有項目，而 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled: !canMove` 會讓 prefix 項目無法拖曳，但 SortableContext 仍包含它們。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16766 (cache hit 16640) ｜ completion tokens 930 ｜ PR #3</sub>