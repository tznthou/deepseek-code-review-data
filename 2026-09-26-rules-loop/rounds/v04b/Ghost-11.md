<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI，包括新增 autoCloseOnSelect 屬性、調整樣式與 i18n 預設值。主要風險在於將預設 i18n 字串改為空字串可能導致 UI 顯示空白，以及新增的 autoCloseOnSelect 在 multiselect 情境下可能造成非預期的關閉行為。此外，部分程式碼違反了專案規範（如使用 var、JSX props 排序）。建議先修正 i18n 空字串與 var 使用問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串改為空字串可能導致 UI 顯示空白 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反規範 | 0.85 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中可能造成非預期關閉 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1201` | [R12] JSX props 排序不符合規範 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 條件判斷無效 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串改為空字串可能導致 UI 顯示空白</summary>

將 `addFilter` 和 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若未提供自訂 i18n，按鈕或標題將顯示空白，影響使用者體驗。建議保留非空預設值，或確認所有使用處都有提供自訂 i18n。

**判斷依據**：diff 中將 'Add filter' 改為 ''，且未見其他補償邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反規範</summary>

在 multiselect 的 onSelect 處理中，將 `const newValues` 改為 `var newValues`，違反專案規範 R20（必須使用 let 或 const）。var 可能導致作用域問題，建議改回 const。

**判斷依據**：diff 中明確將 const 改為 var。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中可能造成非預期關閉</summary>

新增的 autoCloseOnSelect 屬性在 multiselect 選項被選取時會呼叫 onClose，但此處的 onClose 可能只關閉 popover 而不會清除搜尋輸入或觸發其他清理，可能導致狀態不一致。建議確認 onClose 的實作是否完整，或考慮在關閉前執行必要的清理。

**判斷依據**：diff 中新增此條件呼叫 onClose，但未見對應的狀態重置。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1201</code> [R12] JSX props 排序不符合規範</summary>

PopoverContent 的 props 順序未依照專案規範 R12（reserved props 優先、callbacks 最後）。建議調整為 align、className 等順序。

**判斷依據**：diff 中新增的 PopoverContent 未遵循 props 排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 條件判斷無效</summary>

`addButtonText={filters.length ? '' : ''}` 無論 filters.length 為何都傳入空字串，條件判斷失去意義。若意圖是根據 filters 數量顯示不同文字，應提供實際字串；若不需要文字，可直接省略或設為空字串。

**判斷依據**：diff 中將原本的條件文字改為兩個空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6260 (cache hit 6144) ｜ completion tokens 1100 ｜ PR #11</sub>