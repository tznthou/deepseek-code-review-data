<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI，包含新增 autoCloseOnSelect 屬性、調整樣式與圖示，並修改部分預設文字為空字串。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字而影響可用性；另外在 multiselect 中新增的 autoCloseOnSelect 邏輯可能與既有行為衝突，且使用 var 宣告變數違反專案規範。建議優先修正空字串問題與 var 宣告，並確認 autoCloseOnSelect 的互動是否符合預期。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數，違反專案規範 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設的 addFilter 文字被設為空字串，可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:122` | 預設的 addFilterTitle 文字被設為空字串，可能導致工具提示或標題消失 | 0.90 |
| ⚠️ | Major | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 被設為空字串，導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中可能導致非預期關閉 | 0.80 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 在另一處 multiselect 處理中可能導致非預期關閉 | 0.80 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:499` | className 中移除了 mt-0.5，可能影響版面間距 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:455` | Audience 欄位新增 autoCloseOnSelect: true，可能影響多選體驗 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:93` | UTM 選項的 icon 樣式變更，可能影響視覺一致性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數，違反專案規範</summary>

在 SelectOptionsPopover 的 onSelect 處理中，將原本的 const newValues 改為 var newValues。這違反了專案規範 R20（必須使用 let 或 const），且 var 有函數作用域與提升問題，可能導致非預期行為。建議改回 const（若變數不會重新賦值）或使用 let。

**判斷依據**：diff 中明確將 const 改為 var，且專案規範 R20 禁止 var。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設的 addFilter 文字被設為空字串，可能導致按鈕無文字</summary>

DEFAULT_I18N 中的 addFilter 從 'Add filter' 改為空字串，這會讓使用預設 i18n 的 Filters 元件在未提供自訂文字時，按鈕上沒有任何文字，僅顯示圖示（若有的話）。這可能造成使用者無法理解按鈕用途，尤其當圖示不明顯或未設定時。建議保留預設文字，或確保所有使用處都有提供自訂文字。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且此為 DEFAULT_I18N 的預設值，會影響所有未覆寫的實例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設的 addFilterTitle 文字被設為空字串，可能導致工具提示或標題消失</summary>

DEFAULT_I18N 中的 addFilterTitle 從 'Add filter' 改為空字串，這可能影響按鈕的 title 屬性或 aria-label，導致無障礙性問題。建議保留預設文字或確保所有使用處都有提供自訂文字。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且此為 DEFAULT_I18N 的預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 被設為空字串，導致按鈕無文字</summary>

在 StatsFilter 中，將 addButtonText 從條件式文字改為空字串（filters.length ? '' : ''），這使得按鈕永遠沒有文字，僅顯示圖示。若圖示不足以傳達意圖，可能造成可用性問題。建議保留有意義的文字，或確保圖示具有足夠的語意。

**判斷依據**：diff 中將原本的 'Add filter' / 'Filter' 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中可能導致非預期關閉</summary>

在 multiselect 的 onSelect 中新增了 autoCloseOnSelect 的處理，若設定為 true，會在每次選取後呼叫 onClose?.()。這可能與 multiselect 的預期行為（允許連續選取多個項目）衝突，且 onClose 可能觸發父元件的狀態重置，導致使用者無法連續選取。建議確認此屬性的使用情境，或改為僅在達到 maxSelections 時才自動關閉。

**判斷依據**：diff 中新增此邏輯，且 onClose 會呼叫 setOpen(false) 與 setSearchInput('')，可能中斷選取流程。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 在另一處 multiselect 處理中可能導致非預期關閉</summary>

在另一個 multiselect 的 onSelect 處理中，同樣新增了 autoCloseOnSelect 的邏輯，呼叫 handleClose()。這可能與 multiselect 的連續選取行為衝突，且 handleClose 會清空搜尋輸入並關閉 popover。建議確認此屬性的使用情境，或改為僅在達到 maxSelections 時才自動關閉。

**判斷依據**：diff 中新增此邏輯，且 handleClose 會執行 setOpen(false) 與 setSearchInput('')。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:499</code> className 中移除了 mt-0.5，可能影響版面間距</summary>

原本的 className 包含 'mb-6 mt-0.5 [&>button]:order-last'，現在改為 'mb-6 [&>button]:order-last'，移除了 mt-0.5。這可能導致篩選器與上方元素的間距變小，影響視覺排版。若是有意調整，請確認設計意圖；否則建議保留原本的 margin。

**判斷依據**：diff 中移除了 mt-0.5。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:455</code> Audience 欄位新增 autoCloseOnSelect: true，可能影響多選體驗</summary>

在 Audience 的 multiselect 欄位中新增了 autoCloseOnSelect: true，這會讓使用者在每次選取一個受眾後 popover 自動關閉，無法連續選取多個受眾。若這是預期行為（例如選完一個就關閉），則可接受；但若使用者需要選取多個受眾，這會造成不便。建議確認產品需求。

**判斷依據**：diff 中在 audience 欄位新增此屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:93</code> UTM 選項的 icon 樣式變更，可能影響視覺一致性</summary>

將原本的圓形徽章樣式改為單純的文字樣式（order-2 font-mono text-xs text-muted-foreground），這可能改變選項中計數的呈現方式，使其不再醒目。若是有意簡化，請確認設計意圖；否則可能影響使用者對計數的感知。

**判斷依據**：diff 中修改了 icon 的 className。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7304 (cache hit 7296) ｜ completion tokens 2087 ｜ PR #11</sub>