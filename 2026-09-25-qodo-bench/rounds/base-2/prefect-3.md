<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 schema 表單的陣列欄位加入拖放排序功能，使用 @dnd-kit 套件。主要風險在於拖放邏輯與既有移動/刪除功能的互動，以及 prefixItems 的處理。最需要注意的是 handleDragEnd 中索引計算可能因 prefixItems 而錯誤，以及 SortableContext 包含不可拖曳項目的潛在問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134` | 拖放索引計算未考慮 prefixItems，可能導致項目錯位 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148` | SortableContext 包含不可拖曳項目，可能導致拖放行為異常 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-array-item.tsx:52` | useSortable 的 id 使用 itemKey，但 itemKey 可能重複 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134</code> 拖放索引計算未考慮 prefixItems，可能導致項目錯位</summary>

`handleDragEnd` 使用 `localKeyedValues` 的索引來呼叫 `moveItem`，但 `moveItem` 預期的是「可移動項目」的索引（已扣除 prefixItems）。當陣列有 prefixItems 時，`localKeyedValues` 包含所有項目，而 `moveItem` 內部可能使用 `getCanMoveForIndex` 或直接操作索引，導致拖放後項目順序錯誤。

建議：在 `handleDragEnd` 中先計算可移動項目的索引，或修改 `moveItem` 使其接受原始索引並在內部處理 prefixItems 偏移。

**判斷依據**：diff 中新增的 handleDragEnd 直接使用 localKeyedValues 的索引，而 moveItem 的實作（未在 diff 中）可能假設索引是基於可移動項目。同時，prefixItemsCount 被計算但未在此處使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148</code> SortableContext 包含不可拖曳項目，可能導致拖放行為異常</summary>

`sortableKeys` 包含所有項目的 key，包括 prefixItems（不可拖曳）。雖然 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 屬性設為 `!canMove`，但將不可拖曳項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳可移動項目時，不可移動項目仍被視為潛在目標。

建議：僅將可移動項目的 key 傳入 SortableContext，或確認 dnd-kit 對 disabled 項目的處理符合預期。

**判斷依據**：diff 中 sortableKeys 直接映射所有項目，未過濾 prefixItems。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-item.tsx:52</code> useSortable 的 id 使用 itemKey，但 itemKey 可能重複</summary>

`itemKey` 來自父層的 `key`，而 `key` 是使用 `uuidv4()` 生成的，理論上唯一。但若未來改用其他生成方式，可能導致重複。目前風險低，但建議確認 key 的唯一性。

**判斷依據**：diff 中 itemKey 直接作為 useSortable 的 id。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16766 (cache hit 16640) ｜ completion tokens 963 ｜ PR #3</sub>