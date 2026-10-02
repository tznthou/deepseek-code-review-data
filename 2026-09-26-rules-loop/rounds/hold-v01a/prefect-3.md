<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 schema form 的陣列輸入加入拖放排序功能，使用 @dnd-kit 套件。主要風險在於拖放邏輯與既有移動邏輯的整合，以及可排序項目清單未排除不可移動的前綴項目，可能導致拖放時索引計算錯誤。此外，新增的測試僅涵蓋快照，未驗證拖放行為本身。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | sortableKeys 包含不可移動的 prefix items，可能導致拖放索引錯亂 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:133` | handleDragEnd 未驗證 over 項目是否可移動 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-array-item.tsx:52` | useSortable 的 id 使用 itemKey，但 itemKey 可能重複 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | sortableKeys 未使用 useMemo，可能導致不必要的重新渲染 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> sortableKeys 包含不可移動的 prefix items，可能導致拖放索引錯亂</summary>

`sortableKeys` 直接使用所有 `localKeyedValues` 的 key，但 `canMove` 對 prefix items 回傳 false，這些項目不應參與排序。若使用者拖曳可移動項目到 prefix item 上，`handleDragEnd` 會計算出新索引並呼叫 `moveItem`，但 `moveItem` 內部可能未考慮 prefix items 不可移動的限制，導致陣列順序錯誤或 prefix items 被移動。

建議：`sortableKeys` 應只包含 `canMove` 為 true 的項目 key，並在 `handleDragEnd` 中檢查 `over` 是否為可移動項目。

**判斷依據**：diff 中新增的 `sortableKeys` 定義未過濾不可移動項目，而 `SchemaFormInputArrayItem` 的 `canMove` prop 控制拖曳把手顯示，但 SortableContext 仍將所有項目視為可排序。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:133</code> handleDragEnd 未驗證 over 項目是否可移動</summary>

在 `handleDragEnd` 中，僅檢查 `over` 存在且 id 不同，未確認 `over` 對應的項目是否可移動（即非 prefix item）。若使用者將可移動項目拖到 prefix item 上，會執行 `moveItem`，可能導致 prefix item 被移動或陣列順序錯誤。

建議：在執行移動前，檢查 `over` 對應的 index 是否滿足 `getCanMoveForIndex(newIndex)`。

**判斷依據**：diff 中 `handleDragEnd` 的實作未使用 `getCanMoveForIndex` 進行檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-item.tsx:52</code> useSortable 的 id 使用 itemKey，但 itemKey 可能重複</summary>

`itemKey` 來自父層的 `key`，而 `key` 是透過 `uuidv4()` 產生的，應該唯一。但若未來改用其他方式產生 key，可能導致拖放衝突。目前風險低，但建議在註解中說明 key 的唯一性假設。

**判斷依據**：diff 中 `itemKey` 直接作為 `useSortable` 的 id，未見唯一性保證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> sortableKeys 未使用 useMemo，可能導致不必要的重新渲染</summary>

`sortableKeys` 在每次 render 時重新建立陣列，若 `localKeyedValues` 未變，仍會產生新陣列參考，可能觸發 `SortableContext` 的重新渲染。建議使用 `useMemo` 包裹。

**判斷依據**：diff 中直接計算，未使用 `useMemo`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18261 (cache hit 16640) ｜ completion tokens 1171 ｜ PR #3</sub>