<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema form 的陣列欄位加入拖放排序功能，使用 @dnd-kit 套件。主要風險在於拖放邏輯的索引計算可能錯誤（handleDragEnd 中 moveItem 參數順序疑似顛倒），以及 prefixItems 與可拖動項目混用時可能導致排序錯亂。此外，sortableKeys 包含不可拖動的 prefix items，可能造成拖放目標錯誤。建議修正索引計算並確保 SortableContext 僅包含可拖動項目。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142` | 拖放排序索引參數順序錯誤 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖動的 prefix items | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142</code> 拖放排序索引參數順序錯誤</summary>

在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能導致排序方向相反。`moveItem` 的實作是 `newValues.splice(to, 0, newValues.splice(from, 1)[0])`，其中 `from` 是來源索引，`to` 是目標索引。但呼叫時傳入 `newIndex` 作為 `from`，`oldIndex` 作為 `to`，會將項目從新位置移回舊位置，造成拖放後順序不變或錯亂。應改為 `moveItem(oldIndex, newIndex)`。

**判斷依據**：diff 中 `handleDragEnd` 函式內：`moveItem(newIndex, oldIndex);`，而 `moveItem` 定義為 `function moveItem(from: number, to: number) { const newValues = [...localKeyedValues]; newValues.splice(to, 0, newValues.splice(from, 1)[0]); ... }`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖動的 prefix items</summary>

`sortableKeys` 是從所有 `localKeyedValues` 取得，包含 prefix items（不可拖動）。這可能導致拖放時將項目移動到 prefix 區域，或將 prefix 項目當作拖放目標，造成排序混亂。應僅將可拖動項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除。

**判斷依據**：diff 中 `const sortableKeys = localKeyedValues.map((item) => item.key);`，但 `getCanMoveForIndex` 會對 prefix items 回傳 false，且 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 設為 `!canMove`，但 SortableContext 仍包含所有項目。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 20862 (cache hit 6272) ｜ completion tokens 734 ｜ PR #3</sub>