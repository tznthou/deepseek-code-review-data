<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了分析篩選器的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式、以及修改 stats-filter 的欄位設定。主要風險在於將預設 i18n 字串改為空字串，可能導致按鈕無文字；以及使用 var 宣告變數違反專案規範。此外，部分樣式變更可能影響版面，需確認視覺效果。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串設為空字串 | 0.90 |
| ⚠️ | Major | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串 | 0.85 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 後未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1276` | select 類型關閉時未呼叫 handleClose | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數</summary>

在 SelectOptionsPopover 的 onSelect 處理中，將 `const newValues` 改為 `var newValues`，違反專案規範 R20（必須使用 let 或 const）。var 可能導致變數提升與作用域問題，應改回 const。

**判斷依據**：diff 中將原本的 const 改為 var，違反 R20。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串設為空字串</summary>

DEFAULT_I18N 中的 `addFilter` 和 `addFilterTitle` 被改為空字串，這會導致使用預設 i18n 的按鈕沒有文字，影響可用性。若有意圖，應提供替代方案或確保所有使用處都有覆寫。

**判斷依據**：diff 中將 'Add filter' 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串</summary>

在 StatsFilter 中，`addButtonText={filters.length ? '' : ''}` 永遠是空字串，導致按鈕沒有文字。可能意圖是只顯示圖示，但應確認設計。若需隱藏文字，應使用適當的 prop 或 CSS。

**判斷依據**：diff 中原本根據 filters.length 顯示不同文字，現在改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 後未清除搜尋輸入</summary>

在 multiselect 的 onSelect 中，若 autoCloseOnSelect 為 true，呼叫 onClose?.() 但未清除搜尋輸入。這可能導致下次開啟時仍顯示舊的搜尋字串。建議在關閉時一併清除搜尋輸入。

**判斷依據**：diff 中新增 autoCloseOnSelect 處理，但未呼叫 setSearchInput('')。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1276</code> select 類型關閉時未呼叫 handleClose</summary>

在 select 類型的 onSelect 中，原本呼叫 setOpen(false) 和 handleClose()，現在只呼叫 setOpen(false)，移除了 handleClose()。這可能導致 onClose 回呼未被觸發，影響父元件狀態。

**判斷依據**：diff 中移除了 handleClose() 呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7380 (cache hit 7296) ｜ completion tokens 1008 ｜ PR #11</sub>