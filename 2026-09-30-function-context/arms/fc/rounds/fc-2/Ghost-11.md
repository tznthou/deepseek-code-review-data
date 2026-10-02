<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整分析頁面的篩選器 UI 與互動行為，包括新增 autoCloseOnSelect、調整樣式、修改 i18n 預設值等。整體風險中等，主要問題在於將預設 i18n 字串改為空字串可能導致按鈕無文字，以及 autoCloseOnSelect 在 inline 模式下的關閉邏輯可能造成狀態不同步。建議修正後再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串被改為空字串，可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:122` | 預設 i18n 字串被改為空字串，可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1100` | inline 模式下 autoCloseOnSelect 未正確關閉 popover | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | 使用 var 宣告變數，應改為 const | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1100` | autoCloseOnSelect 在 inline 模式下可能造成狀態不同步 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 被設為空字串，可能導致按鈕無文字 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:499` | className 變更可能影響版面配置 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/layout/stats-header.tsx:67` | Navbar 的 padding 調整可能影響版面 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串被改為空字串，可能導致按鈕無文字</summary>

`addFilter` 和 `addFilterTitle` 的預設值從 'Add filter' 改為空字串。這會影響所有未提供自訂 i18n 的 Filters 使用情境，導致新增篩選器按鈕沒有文字，僅顯示圖示。若設計上希望按鈕只顯示圖示，應在呼叫端明確傳入空字串，而非修改全域預設值。

**判斷依據**：diff 中將 `addFilter: 'Add filter'` 改為 `addFilter: ''`，且 `addFilterTitle` 也有相同變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設 i18n 字串被改為空字串，可能導致按鈕無文字</summary>

`addFilterTitle` 的預設值從 'Add filter' 改為空字串，這會影響按鈕的 title 屬性，導致滑鼠懸停時沒有提示文字。

**判斷依據**：diff 中將 `addFilterTitle: 'Add filter'` 改為 `addFilterTitle: ''`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1100</code> inline 模式下 autoCloseOnSelect 未正確關閉 popover</summary>

在 inline 模式的 `SelectOptionsPopover` 中，當 `autoCloseOnSelect` 為 true 且為多選時，呼叫了 `onClose?.()`，但 `onClose` 在 inline 模式下是由父元件傳入的函式，其行為是設定 `addFilterOpen` 為 false 並清除 `selectedFieldKeyForOptions`。然而，inline 模式本身沒有自己的 open state，關閉與否完全由父元件控制。若父元件的 `onClose` 未正確處理，可能導致 popover 無法關閉或狀態不同步。建議確認父元件 `Filters` 中的 `onClose` 實作是否完整。

**判斷依據**：diff 中新增了 `autoCloseOnSelect` 的處理，但 inline 模式的關閉邏輯依賴外部傳入的 `onClose`，需檢查父元件實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> 使用 var 宣告變數，應改為 const</summary>

在 inline 模式的 `onSelect` 中，將 `const newValues` 改為 `var newValues`。這可能是無意的變更，且 `var` 有函式作用域，可能導致非預期的行為。建議改回 `const`。

**判斷依據**：diff 中將 `const newValues` 改為 `var newValues`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1100</code> autoCloseOnSelect 在 inline 模式下可能造成狀態不同步</summary>

在 inline 模式下，當 `autoCloseOnSelect` 為 true 時，呼叫 `onClose?.()` 後，父元件會關閉 popover 並清除 `selectedFieldKeyForOptions`。但此時 `tempSelectedValues` 可能尚未更新，導致下次開啟時顯示舊值。建議在關閉前先更新 tempSelectedValues 或確保父元件正確處理。

**判斷依據**：diff 中新增了 autoCloseOnSelect 的處理，但未見對 tempSelectedValues 的同步更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 被設為空字串，可能導致按鈕無文字</summary>

在 `StatsFilter` 中，`addButtonText` 被設為 `filters.length ? '' : ''`，這永遠是空字串。這可能是有意為之（只顯示圖示），但建議確認設計意圖。若確實要隱藏文字，可考慮直接不傳 `addButtonText` 或使用 CSS 隱藏。

**判斷依據**：diff 中將原本的條件文字改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:499</code> className 變更可能影響版面配置</summary>

移除了 `mt-0.5`，並將 `mb-6 mt-0.5` 改為 `mb-6`。這可能導致篩選器與上方元素的間距改變，需確認視覺效果是否符合預期。

**判斷依據**：diff 中移除了 `mt-0.5`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/layout/stats-header.tsx:67</code> Navbar 的 padding 調整可能影響版面</summary>

將 `py-8` 改為 `pb-6 pt-9`，這會改變 Navbar 的垂直 padding，可能影響整體版面配置。需確認此變更是否為預期的設計調整。

**判斷依據**：diff 中將 `py-8` 改為 `pb-6 pt-9`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18261 (cache hit 18176) ｜ completion tokens 1794 ｜ PR #11</sub>