<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示，並修改預設 i18n 字串為空。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字；另外使用 var 宣告違反專案規範，以及 autoCloseOnSelect 的關閉邏輯可能與既有流程不一致。建議先修正空字串問題與 var 宣告。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串設為空可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 關閉邏輯可能與既有流程不一致 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1276` | select 類型關閉時未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 條件表達式無效 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數</summary>

在 multiselect 的 onSelect 處理中，將原本的 `const newValues` 改為 `var newValues`，違反專案規範 R20（應使用 let 或 const）。var 可能導致作用域問題，建議改回 const。

**判斷依據**：diff 中第 1125 行將 const 改為 var。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串設為空可能導致按鈕無文字</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，按鈕將沒有可讀文字，影響可用性。建議保留非空預設值，或確認所有使用處都有提供自訂文字。

**判斷依據**：diff 中第 105 行將原本的 'Add filter' 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 關閉邏輯可能與既有流程不一致</summary>

在 multiselect 的 onSelect 中新增 autoCloseOnSelect 時直接呼叫 `onClose?.()`，但未呼叫 `setOpen(false)` 或 `setSearchInput('')`，可能導致 popover 狀態未完全重置。建議統一使用 `handleClose()` 來關閉，以確保狀態一致。

**判斷依據**：diff 中第 1134-1136 行新增的關閉邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1276</code> select 類型關閉時未清除搜尋輸入</summary>

在 select 類型的 onSelect 中，原本呼叫 `handleClose()` 會清除搜尋輸入，但修改後改為直接 `setOpen(false)`，未清除搜尋輸入。若使用者再次開啟 popover，搜尋文字可能殘留。建議改回呼叫 `handleClose()`。

**判斷依據**：diff 中第 1271-1272 行移除了 handleClose() 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 條件表達式無效</summary>

`addButtonText={filters.length ? '' : ''}` 無論 filters.length 為何都回傳空字串，等同於永遠空字串。若意圖是根據是否有 filters 顯示不同文字，此寫法有誤；若確定要空字串，可直接寫 `addButtonText=''`。

**判斷依據**：diff 中第 497 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7390 (cache hit 4992) ｜ completion tokens 1073 ｜ PR #11</sub>