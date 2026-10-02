<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要調整 Stats 篩選器的 UI 與互動：新增 autoCloseOnSelect、調整樣式、修改圖示與文字。主要風險在於將預設 i18n 文字改為空字串，可能導致按鈕無文字；以及 autoCloseOnSelect 的關閉邏輯未呼叫 handleClose，可能造成狀態不同步。另有 var 宣告違反規範。建議修正後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 文字改為空字串可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:122` | 預設 i18n 文字改為空字串可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | autoCloseOnSelect 關閉邏輯未呼叫 handleClose，可能導致狀態不同步 | 0.85 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數 | 0.95 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 條件表達式永遠為空字串 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 文字改為空字串可能導致按鈕無文字</summary>

將 `addFilter` 和 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，按鈕將沒有可讀文字，影響可用性。建議保留非空預設值，或確認所有使用處都有提供自訂文字。

**判斷依據**：diff 中 `-    addFilter: 'Add filter',` 改為 `+    addFilter: '',`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設 i18n 文字改為空字串可能導致按鈕無文字</summary>

將 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，按鈕將沒有可讀文字，影響可用性。建議保留非空預設值，或確認所有使用處都有提供自訂文字。

**判斷依據**：diff 中 `-    addFilterTitle: 'Add filter',` 改為 `+    addFilterTitle: '',`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> autoCloseOnSelect 關閉邏輯未呼叫 handleClose，可能導致狀態不同步</summary>

在 multiselect 的 onSelect 中，當 `field.autoCloseOnSelect` 為 true 時，直接呼叫 `onClose?.()` 而非 `handleClose()`。`handleClose` 會執行 `setOpen(false)`、`setSearchInput('')` 並呼叫 `onClose`。若直接呼叫 `onClose`，可能導致 popover 未關閉或搜尋輸入未清空。建議改為呼叫 `handleClose()`。

**判斷依據**：diff 中新增的程式碼，與下方 `handleClose` 的實作對比。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數</summary>

將 `const newValues` 改為 `var newValues`，違反專案規範 R20（應使用 let 或 const）。建議改回 `const`。

**判斷依據**：diff 中 `- const newValues` 改為 `+ var newValues`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 條件表達式永遠為空字串</summary>

`addButtonText={filters.length ? '' : ''}` 無論 filters.length 為何都回傳空字串，可能導致按鈕無文字。若意圖是根據 filters.length 顯示不同文字，應提供實際文字；若不需要文字，可直接設為空字串。

**判斷依據**：diff 中 `- addButtonText={filters.length ? 'Add filter' : 'Filter'}` 改為 `+ addButtonText={filters.length ? '' : ''}`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7390 (cache hit 7296) ｜ completion tokens 1117 ｜ PR #11</sub>