<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式、以及修改 UTM 選項的顯示方式。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字或無障礙標籤缺失；另外 autoCloseOnSelect 的實作在 multiselect 情境下呼叫 onClose 但未同步關閉 Popover 的 open 狀態，可能造成 UI 狀態不一致。建議優先修正這兩個問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 文字設為空字串可能導致按鈕無文字或無障礙標籤缺失 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中呼叫 onClose 但未關閉 Popover 的 open 狀態 | 0.85 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反規範 | 0.95 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 條件表達式永遠為空字串 | 0.80 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:93` | UTM 選項的 icon 樣式變更可能影響視覺一致性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 文字設為空字串可能導致按鈕無文字或無障礙標籤缺失</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，按鈕將沒有可見文字，且可能缺少無障礙標籤（aria-label）。這會影響所有使用預設 i18n 的元件。建議保留非空預設值，或確保所有使用處都提供自訂文字。

**判斷依據**：diff 中 `-    addFilter: 'Add filter',` 改為 `+    addFilter: '',`，以及 `-    addFilterTitle: 'Add filter',` 改為 `+    addFilterTitle: '',`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中呼叫 onClose 但未關閉 Popover 的 open 狀態</summary>

在 multiselect 分支中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但未呼叫 `setOpen(false)`。`onClose` 可能只觸發父層的狀態更新，而 Popover 的 `open` 狀態仍由內部控制，導致 Popover 不會關閉。建議同時呼叫 `setOpen(false)` 或確保 `onClose` 會觸發關閉。

**判斷依據**：diff 中新增的程式碼片段，位於 multiselect 的 onSelect 處理中，未見 setOpen(false) 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反規範</summary>

將 `const newValues` 改為 `var newValues`，違反 R20 規範（應使用 let 或 const）。此變數未重新賦值，應使用 const。

**判斷依據**：diff 中 `- const newValues = ...` 改為 `+ var newValues = ...`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 條件表達式永遠為空字串</summary>

`addButtonText={filters.length ? '' : ''}` 無論 filters 是否有值，結果都是空字串，等同於 `addButtonText=''`。這可能不是預期行為，且與先前邏輯（有 filters 時顯示 'Add filter'，否則顯示 'Filter'）不同。建議確認是否應保留原邏輯或直接設為空字串。

**判斷依據**：diff 中 `- addButtonText={filters.length ? 'Add filter' : 'Filter'}` 改為 `+ addButtonText={filters.length ? '' : ''}`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:93</code> UTM 選項的 icon 樣式變更可能影響視覺一致性</summary>

將原本的 badge 樣式改為 `order-2 font-mono text-xs text-muted-foreground`，移除了背景與圓角，可能使計數顯示不明顯。若這是刻意簡化，建議確認設計意圖。

**判斷依據**：diff 中兩處 icon 的 className 從 badge 樣式改為此樣式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7370 (cache hit 7296) ｜ completion tokens 1241 ｜ PR #11</sub>