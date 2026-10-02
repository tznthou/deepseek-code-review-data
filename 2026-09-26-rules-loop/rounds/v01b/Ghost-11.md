<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 主要調整了分析頁面的篩選器 UI，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示，以及修改部分 i18n 預設值。整體風險集中在：將預設的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字；將 const 改為 var 違反專案規範；以及 autoCloseOnSelect 的實作在部分路徑可能未正確關閉 popover。建議優先修正空字串問題與 var 宣告，並確認 autoCloseOnSelect 的行為符合預期。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反專案規範 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 分支中呼叫 onClose 但未清除搜尋輸入 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 在另一處 multiselect 分支中呼叫 handleClose 但未清除選取狀態 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串可能導致按鈕無文字 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反專案規範</summary>

在 `SelectOptionsPopover` 的 `onSelect` 中，將原本的 `const newValues` 改為 `var newValues`。專案規範要求使用 `let` 或 `const`，禁止 `var`。請改回 `const`（若需重新賦值則使用 `let`）。

**判斷依據**：diff 中明確將 `const` 改為 `var`，違反 R20。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，則新增篩選器的按鈕將沒有文字，影響可用性。建議保留非空預設值，或確認所有使用處都有提供自訂文字。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且 addFilterTitle 也同樣改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 分支中呼叫 onClose 但未清除搜尋輸入</summary>

在 multiselect 的 `onSelect` 中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但 `onClose` 可能不會清除搜尋輸入（`setSearchInput('')`）。若 popover 重新開啟，搜尋文字可能殘留，造成使用者困惑。建議統一使用 `handleClose` 來關閉，以確保搜尋輸入被重置。

**判斷依據**：diff 中新增的 autoClose 邏輯直接呼叫 onClose，而 handleClose 中有 setSearchInput('')。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 在另一處 multiselect 分支中呼叫 handleClose 但未清除選取狀態</summary>

在另一個 multiselect 的 `onSelect` 中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `handleClose()`，但 `handleClose` 會將 `open` 設為 false 並清除搜尋輸入，但不會清除已選取的值。若使用者重新開啟 popover，可能看到先前的選取狀態，但這可能是預期行為。建議確認此行為是否符合產品需求。

**判斷依據**：diff 中新增的 autoClose 邏輯呼叫 handleClose。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串可能導致按鈕無文字</summary>

將 `addButtonText` 從條件式文字改為空字串，若 `Filters` 元件未提供預設文字，則按鈕可能只顯示圖示。建議確認此為預期設計，或提供有意義的文字。

**判斷依據**：diff 中將原本的 'Add filter' 或 'Filter' 改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7380 (cache hit 7296) ｜ completion tokens 1215 ｜ PR #11</sub>