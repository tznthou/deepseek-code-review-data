<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema 表單的陣列欄位加入拖放排序功能，使用 @dnd-kit 套件。主要風險在於拖放後資料順序更新可能不正確，以及可排序項目包含不可移動的 prefix items，可能導致拖放時索引錯亂。建議先修正排序邏輯並確保僅可移動項目參與排序。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142` | 拖放後資料順序更新錯誤 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可移動的 prefix items | 0.85 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142</code> 拖放後資料順序更新錯誤</summary>

在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能導致陣列順序更新錯誤。`moveItem` 的簽名為 `(fromIndex, toIndex)`，但此處傳入 `(newIndex, oldIndex)`，會將項目移到錯誤的位置。例如，將第一個項目拖到第三個位置時，`oldIndex=0`、`newIndex=2`，呼叫 `moveItem(2, 0)` 會將索引 2 的項目移到索引 0，而非將索引 0 的項目移到索引 2。應改為 `moveItem(oldIndex, newIndex)`。

**判斷依據**：diff 中新增的 `handleDragEnd` 函式內，呼叫 `moveItem(newIndex, oldIndex)`，但 `moveItem` 的參數順序為 `(fromIndex, toIndex)`，因此參數順序顛倒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可移動的 prefix items</summary>

`sortableKeys` 包含所有項目的 key，包括 prefix items（不可移動）。這可能導致拖放時將 prefix item 視為可排序項目，造成索引計算錯誤或拖放行為異常。應僅將可移動項目的 key 傳入 `SortableContext`，例如使用 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

**判斷依據**：diff 中新增 `sortableKeys` 的計算，未過濾不可移動的 prefix items，而 `SortableContext` 使用此陣列。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16730 (cache hit 16640) ｜ completion tokens 642 ｜ PR #3</sub>