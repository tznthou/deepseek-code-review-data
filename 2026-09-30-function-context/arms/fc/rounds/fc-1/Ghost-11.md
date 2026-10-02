<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 Analytics 篩選器的 UI 與互動行為，包括新增 autoCloseOnSelect、調整樣式、修改 i18n 預設值，以及變更部分圖示與版面。整體風險中等，最需要注意的是 DEFAULT_I18N 中 addFilter 與 addFilterTitle 被改為空字串，可能導致按鈕無文字；另外 autoCloseOnSelect 的實作在 inline 模式與 popover 模式行為不一致，且未處理 maxSelections 限制下的關閉時機。建議先修正 i18n 空字串問題，並統一 autoCloseOnSelect 的行為。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | DEFAULT_I18N 的 addFilter 與 addFilterTitle 被改為空字串 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1105` | autoCloseOnSelect 在 inline 模式未呼叫 onClose | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1180` | autoCloseOnSelect 在達到 maxSelections 時仍可能關閉 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 被設為空字串 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | 使用 var 宣告 newValues | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:499` | className 移除 mt-0.5 可能影響版面 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> DEFAULT_I18N 的 addFilter 與 addFilterTitle 被改為空字串</summary>

`addFilter` 與 `addFilterTitle` 從 'Add filter' 改為空字串，這會導致使用預設 i18n 的按鈕沒有文字（僅顯示圖示），且 title 屬性為空。若未在其他地方覆寫，使用者將看不到新增篩選器的文字標籤，影響可用性。建議保留預設文字，或確認所有使用處都有提供自訂文字。

**判斷依據**：diff 中 `-    addFilter: 'Add filter',` 改為 `+    addFilter: '',`，以及 `-    addFilterTitle: 'Add filter',` 改為 `+    addFilterTitle: '',`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1105</code> autoCloseOnSelect 在 inline 模式未呼叫 onClose</summary>

在 inline 模式（`inline={true}`）的 `SelectOptionsPopover` 中，當 `field.autoCloseOnSelect` 為 true 且為 multiselect 時，程式碼呼叫了 `onClose?.()`，但 `onClose` 是從 props 傳入的，在 `Filters` 元件中 inline 模式的 `onClose` 會設定 `setAddFilterOpen(false)` 並清除 `selectedFieldKeyForOptions`。然而，在 `SelectOptionsPopover` 的 inline 分支中，`onClose` 被呼叫後，外層的 `Popover` 可能不會正確關閉，因為 inline 模式沒有自己的 `open` state 控制。這可能導致 popover 無法關閉或狀態不同步。建議確認 inline 模式下 autoCloseOnSelect 的關閉邏輯是否正確。

**判斷依據**：diff 中新增的 `+                                                    // Auto-close if configured` 與 `+                                                    if (field.autoCloseOnSelect) {` 區塊，位於 inline 模式的 multiselect 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1180</code> autoCloseOnSelect 在達到 maxSelections 時仍可能關閉</summary>

在非 inline 模式的 multiselect 分支中，當 `field.maxSelections` 已達上限時，程式碼會 `return` 而不新增選項，但 `autoCloseOnSelect` 的檢查在 `return` 之後，因此不會執行。這表示當使用者嘗試超過上限時，popover 不會關閉，可能造成困惑。建議在 `return` 前也考慮是否要關閉，或明確不關閉並提供提示。

**判斷依據**：diff 中新增的 autoCloseOnSelect 區塊位於 maxSelections 檢查之後，若觸發 return 則不會執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 被設為空字串</summary>

在 `StatsFilter` 中，`addButtonText` 被改為 `filters.length ? '' : ''`，這永遠是空字串，導致按鈕沒有文字。雖然圖示已改為 `FunnelPlus`，但可能仍需要文字標籤以提升可讀性。建議確認是否刻意移除文字，或改為有意義的文字。

**判斷依據**：diff 中 `-            addButtonText={filters.length ? 'Add filter' : 'Filter'}` 改為 `+            addButtonText={filters.length ? '' : ''}`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> 使用 var 宣告 newValues</summary>

在 inline 模式的 multiselect 分支中，`newValues` 使用 `var` 宣告，而其他類似處使用 `const`。這可能是筆誤，建議改為 `const` 以維持一致性並避免潛在的變數提升問題。

**判斷依據**：diff 中 `-                                                    const newValues = [...effectiveValues, option.value] as T[];` 改為 `+                                                    var newValues = [...effectiveValues, option.value] as T[];`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:499</code> className 移除 mt-0.5 可能影響版面</summary>

原本的 `className='mb-6 mt-0.5 [&>button]:order-last'` 改為 `className='mb-6 [&>button]:order-last'`，移除了 `mt-0.5`。這可能導致篩選器與上方元素的間距改變，若是有意調整則可忽略，但需確認視覺效果。

**判斷依據**：diff 中 `-            className='mb-6 mt-0.5 [&>button]:order-last'` 改為 `+            className='mb-6 [&>button]:order-last'`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18261 (cache hit 1536) ｜ completion tokens 1689 ｜ PR #11</sub>