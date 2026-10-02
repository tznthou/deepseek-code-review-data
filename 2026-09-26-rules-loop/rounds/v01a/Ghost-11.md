<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要調整統計頁面的篩選器 UI，包含新增 autoCloseOnSelect 屬性、調整樣式與圖示，並修改部分預設文字。整體風險中等：發現一個明確違反 R20 的 var 宣告，以及多個可能影響使用者體驗或可維護性的問題，例如空字串作為按鈕文字、搜尋輸入未在關閉時清空、以及樣式類別可能被覆蓋。建議先修正 var 宣告與空字串問題，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數 | 0.99 |
| ⚠️ | Major | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1051` | 關閉彈窗時未清空搜尋輸入 | 0.85 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在多選時呼叫 onClose 但未關閉 Popover | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1201` | PopoverContent 的 className 可能覆蓋 field.className 的寬度設定 | 0.75 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:105` | DEFAULT_I18N 中的 addFilter 和 addFilterTitle 設為空字串 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數</summary>

在 `SelectOptionsPopover` 的 `onSelect` 處理中，將原本的 `const newValues` 改為 `var newValues`。這違反了專案規範 R20（必須使用 let 或 const），且 `var` 的函數作用域可能導致非預期的變數提升（hoisting）問題。

建議改回 `const newValues = [...effectiveValues, option.value] as T[];`

**判斷依據**：diff 中將原本的 `const newValues` 改為 `var newValues`，違反 R20。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串導致按鈕無文字</summary>

在 `StatsFilter` 元件中，`addButtonText` 被改為 `filters.length ? '' : ''`，這使得無論是否有篩選器，按鈕文字都是空字串。這可能導致按鈕只剩下圖示，若圖示未正確顯示或無障礙標籤缺失，使用者將無法理解按鈕用途。

建議保留原本的條件文字（例如 `filters.length ? 'Add filter' : 'Filter'`），或提供明確的 `aria-label`。

**判斷依據**：diff 中原本的 `addButtonText={filters.length ? 'Add filter' : 'Filter'}` 被改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1051</code> 關閉彈窗時未清空搜尋輸入</summary>

在 `handleClose` 中新增了 `setSearchInput('')`，但 `SelectOptionsPopover` 的 `onClose` 可能不會被呼叫（例如使用者點擊外部關閉時）。這可能導致下次開啟彈窗時，搜尋輸入仍保留上次的內容，造成混淆。

建議確認所有關閉路徑都會觸發 `handleClose`，或將清空邏輯移至 `PopoverContent` 的 `onCloseAutoFocus` 或 `onEscapeKeyDown` 等事件。

**判斷依據**：diff 中在 `handleClose` 內新增 `setSearchInput('')`，但未涵蓋所有關閉情境。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在多選時呼叫 onClose 但未關閉 Popover</summary>

在 `SelectOptionsPopover` 的 `onSelect` 中，當 `isMultiSelect` 為 true 且 `field.autoCloseOnSelect` 為 true 時，呼叫了 `onClose?.()`，但沒有呼叫 `setOpen(false)`。這可能導致 Popover 仍然開啟，但父元件的狀態已變更，造成 UI 不一致。

建議同時呼叫 `setOpen(false)` 或確保 `onClose` 會觸發關閉。

**判斷依據**：diff 中新增了 autoCloseOnSelect 的處理，但未呼叫 setOpen(false)。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1201</code> PopoverContent 的 className 可能覆蓋 field.className 的寬度設定</summary>

在 `SelectOptionsPopover` 中，`PopoverContent` 的 className 改為 `cn('p-0 data-[state=closed]:!animation-none data-[state=closed]:!duration-0', field.className || 'w-[200px]')`。若 `field.className` 包含寬度類別（例如 `w-80`），則原本的 `w-[200px]` 會被覆蓋，但若 `field.className` 未提供，則使用 `w-[200px]`。這可能導致在某些情況下寬度不符合預期。

建議確認此行為是否符合設計，或將寬度類別獨立處理。

**判斷依據**：diff 中將原本的 `w-[200px]` 改為條件式，可能影響寬度。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> DEFAULT_I18N 中的 addFilter 和 addFilterTitle 設為空字串</summary>

將 `addFilter` 和 `addFilterTitle` 的預設值改為空字串，可能導致使用預設 i18n 的元件顯示空白按鈕或標題。若這些值用於無障礙標籤或 tooltip，將影響可用性。

建議保留原本的文字，或確認所有使用處都有提供自訂 i18n。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7380 (cache hit 4992) ｜ completion tokens 1616 ｜ PR #11</sub>