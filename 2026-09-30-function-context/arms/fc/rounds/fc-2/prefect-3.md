<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 schema form 的陣列輸入加入拖放排序功能，使用 @dnd-kit 套件。主要風險在於拖放時索引計算可能錯誤（moveItem 參數順序疑似顛倒），以及 prefixItems 的排序限制未在拖放邏輯中強制執行，可能導致 prefix 項目被移到非 prefix 區域。建議先修正索引計算並補上拖放邊界檢查。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142` | 拖放排序的索引參數順序錯誤 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:45` | 拖放可能違反 prefixItems 的固定順序 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | sortableKeys 包含不可拖動的 prefix 項目 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142</code> 拖放排序的索引參數順序錯誤</summary>

在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序與 `moveItem` 的定義 `(from, to)` 相反。這會導致拖放後項目被移到錯誤的位置。例如，將第一個項目拖到第三個位置時，`oldIndex=0`、`newIndex=2`，呼叫 `moveItem(2, 0)` 會把第三個項目移到第一個位置，而不是把第一個項目移到第三個位置。

建議改為 `moveItem(oldIndex, newIndex)`。

**判斷依據**：diff 中 `handleDragEnd` 函式內呼叫 `moveItem(newIndex, oldIndex)`，而 `moveItem` 的簽名為 `(from: number, to: number)`，參數順序明顯相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:45</code> 拖放可能違反 prefixItems 的固定順序</summary>

`getCanMoveForIndex` 僅禁止 prefix 項目被拖動，但未限制非 prefix 項目被拖到 prefix 項目的位置。若使用者將非 prefix 項目拖到 prefix 區域，會導致 prefix 項目被擠到後面，破壞 schema 中 prefixItems 的順序。

建議在 `handleDragEnd` 中檢查 `newIndex` 是否小於 `prefixItemsCount`，若是則忽略該拖放操作。

**判斷依據**：diff 中新增了 `prefixItemsCount` 變數，但僅用於計算，未在拖放邏輯中作為邊界檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> sortableKeys 包含不可拖動的 prefix 項目</summary>

`sortableKeys` 直接使用所有項目的 key，包括 prefix 項目。雖然 `useSortable` 的 `disabled` 屬性會阻止 prefix 項目被拖動，但將它們包含在 `SortableContext` 中可能導致排序演算法將它們視為可排序項目，進而影響拖放行為。

建議僅將可拖動項目的 key 傳入 `SortableContext`，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

**判斷依據**：diff 中 `sortableKeys` 的計算未過濾 prefix 項目，而 `getCanMoveForIndex` 已存在可用於過濾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 20862 (cache hit 20736) ｜ completion tokens 923 ｜ PR #3</sub>