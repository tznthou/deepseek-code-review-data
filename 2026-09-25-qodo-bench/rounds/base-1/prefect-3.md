<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema form 的陣列欄位新增拖曳排序功能，使用 @dnd-kit 套件。主要風險在於拖曳排序的索引計算可能因 prefixItems 的存在而錯位，導致資料順序錯誤；此外，SortableContext 的 items 包含不可拖曳的 prefix items，可能造成拖曳行為異常。建議先修正索引計算邏輯，並確保 SortableContext 僅包含可排序的項目。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134` | 拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134</code> 拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤</summary>

在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

**判斷依據**：diff 中新增的 `handleDragEnd` 函式直接使用 `localKeyedValues` 的索引，而 `moveItem` 的實作（未在 diff 中顯示）預期是基於可移動項目的索引。從 `getCanMoveForIndex` 的邏輯可推測 prefixItems 不可移動，因此索引會錯位。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常</summary>

`sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

**判斷依據**：diff 中新增的 `sortableKeys` 直接映射所有項目，而 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled: !canMove` 表示 prefixItems 不可拖曳。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16766 (cache hit 1536) ｜ completion tokens 952 ｜ PR #3</sub>