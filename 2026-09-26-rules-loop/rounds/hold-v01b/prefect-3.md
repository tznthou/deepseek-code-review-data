<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema form 的陣列欄位加入拖放排序功能，使用 @dnd-kit 套件，並新增對應的快照測試。整體實作方向合理，但存在一個可能導致拖放後資料順序錯誤的邏輯問題：`handleDragEnd` 中呼叫 `moveItem` 的參數順序可能顛倒，需要確認 `moveItem` 的實作。此外，`sortableKeys` 包含所有項目（包括不可拖曳的 prefix items），可能導致拖放時索引計算錯誤。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142` | 拖放後呼叫 moveItem 的參數順序可能錯誤 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖曳的 prefix items，可能導致索引錯亂 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142</code> 拖放後呼叫 moveItem 的參數順序可能錯誤</summary>

在 `handleDragEnd` 中，取得 `oldIndex` 和 `newIndex` 後呼叫 `moveItem(newIndex, oldIndex)`。但 `moveItem` 的簽名為 `moveItem(index: number, newIndex: number)`（從既有程式碼推測），因此第一個參數應為原始索引，第二個參數為目標索引。目前傳入的順序相反，會導致拖放後項目順序錯誤。請確認 `moveItem` 的實作，並修正為 `moveItem(oldIndex, newIndex)`。

**判斷依據**：diff 中新增的 `handleDragEnd` 函式內，`moveItem(newIndex, oldIndex)` 與既有 `moveItem` 呼叫慣例（如 `moveItem(index, index - 1)`）不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖曳的 prefix items，可能導致索引錯亂</summary>

`sortableKeys` 使用 `localKeyedValues.map((item) => item.key)` 取得所有項目的 key，但其中包含不可拖曳的 prefix items（`canMove` 為 false）。當拖曳一般項目時，dnd-kit 的排序策略會考慮所有項目，可能導致計算出的 `over.id` 對應到 prefix item，進而使 `newIndex` 指向錯誤位置。建議只將可拖曳項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除 prefix items。

**判斷依據**：diff 中新增的 `sortableKeys` 定義，以及 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled: !canMove` 設定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18261 (cache hit 18176) ｜ completion tokens 710 ｜ PR #3</sub>