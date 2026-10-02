<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema form 的陣列欄位加入拖曳排序功能，使用 @dnd-kit 套件。主要風險在於拖曳後資料順序更新的正確性，以及 prefixItems 與一般 items 混用時的可拖曳項目判斷。目前實作中，handleDragEnd 使用 moveItem(newIndex, oldIndex) 的參數順序可能導致移動方向錯誤；此外，SortableContext 的 items 包含所有項目（含不可拖曳的 prefix items），可能造成拖曳時索引計算錯誤。建議修正 moveItem 呼叫參數，並確保 SortableContext 只包含可拖曳的項目。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142` | handleDragEnd 中 moveItem 參數順序錯誤導致拖曳方向相反 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖曳的 prefix items，可能導致拖曳索引錯亂 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142</code> handleDragEnd 中 moveItem 參數順序錯誤導致拖曳方向相反</summary>

在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能與 `moveItem` 的預期相反。從既有程式碼 `moveUp={() => moveItem(index, index - 1)}` 和 `moveDown={() => moveItem(index, index + 1)}` 推測，`moveItem` 的第一個參數是來源索引，第二個是目標索引。但拖曳時，`oldIndex` 是來源，`newIndex` 是目標，因此應呼叫 `moveItem(oldIndex, newIndex)`。目前寫法會導致拖曳後項目移動到錯誤位置，甚至可能超出陣列範圍。

**判斷依據**：diff 中新增的 `handleDragEnd` 函式內，`moveItem(newIndex, oldIndex)` 與既有 `moveUp`/`moveDown` 的呼叫方式不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖曳的 prefix items，可能導致拖曳索引錯亂</summary>

`sortableKeys` 由 `localKeyedValues.map((item) => item.key)` 產生，包含所有項目，但實際上只有非 prefix items 可拖曳（`canMove` 為 true）。當存在 prefix items 時，拖曳一般項目時，`over.id` 可能指向不可拖曳的 prefix item，導致 `newIndex` 計算錯誤，或拖曳行為不符合預期。建議 `sortableKeys` 只包含可拖曳項目的 key，例如先 filter `getCanMoveForIndex(index)` 為 true 的項目。

**判斷依據**：diff 中新增的 `sortableKeys` 定義，以及 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled: !canMove`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16730 (cache hit 1408) ｜ completion tokens 751 ｜ PR #3</sub>