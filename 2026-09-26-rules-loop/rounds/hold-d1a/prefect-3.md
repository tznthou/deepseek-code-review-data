<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 為 schema form 的陣列輸入新增拖曳排序功能，引入 @dnd-kit 相關套件，並在陣列項目中加入拖曳把手。主要風險在於拖曳排序的邏輯可能未正確處理 prefixItems 的不可移動項目，以及新增的測試是否符合專案規範。最需要先確認的是拖曳排序是否會影響 prefixItems 的固定順序，以及測試檔案的位置是否符合 R10。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/schemas/schema-form-input-array-list.tsx:130` | 拖曳排序可能將 prefixItems 移到可移動項目之後 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form.snapshot.test.tsx:489` | [R10] 測試檔案未與元件檔案同目錄 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/schemas/schema-form-input-array-list.tsx:130</code> 拖曳排序可能將 prefixItems 移到可移動項目之後</summary>

在 `handleDragEnd` 中，直接使用 `moveItem(newIndex, oldIndex)` 來交換項目，但未檢查 `oldIndex` 或 `newIndex` 是否對應到 prefixItems。prefixItems 是 schema 中定義的固定前綴項目，不應被拖曳或重新排序。如果使用者將可移動項目拖到 prefixItems 的位置，可能導致 prefixItems 的順序被改變，違反 schema 定義。建議在拖曳結束時，限制可移動的索引範圍，僅允許在 prefixItems 之後的項目之間排序。

**判斷依據**：diff 中新增的 `handleDragEnd` 函式未檢查索引是否落在 prefixItems 範圍內，而 `moveItem` 的實作可能直接交換陣列元素。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form.snapshot.test.tsx:489</code> [R10] 測試檔案未與元件檔案同目錄</summary>

根據 R10，React 元件測試檔案應與元件檔案放在同一目錄。此 PR 新增的測試位於 `ui-v2/src/components/schemas/schema-form.snapshot.test.tsx`，但被測試的元件 `schema-form-input-array-item.tsx` 和 `schema-form-input-array-list.tsx` 位於 `ui-v2/src/components/schemas/` 下，測試檔案與元件檔案同目錄，符合 R10。然而，此測試檔案是 snapshot 測試，且原本就存在，新增的測試案例只是擴充，因此不構成違反。

**判斷依據**：測試檔案路徑為 `ui-v2/src/components/schemas/schema-form.snapshot.test.tsx`，與元件檔案同目錄，符合 R10。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18298 (cache hit 18176) ｜ completion tokens 806 ｜ PR #3</sub>