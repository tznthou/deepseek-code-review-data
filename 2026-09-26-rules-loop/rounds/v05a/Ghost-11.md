<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI，包含新增 autoCloseOnSelect 屬性、調整樣式與圖示，並修改預設 i18n 字串為空。整體風險中等，需注意：1) 將預設 i18n 的 addFilter 與 addFilterTitle 改為空字串可能導致按鈕無文字；2) 使用 var 宣告變數違反專案規範；3) 部分 Tailwind 類別順序可能不符合標準；4) 新增的 autoCloseOnSelect 在多選情境下呼叫 onClose 但未清除搜尋輸入，可能造成狀態不一致。建議修正上述問題後再合併。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反專案規範 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字 | 0.90 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 觸發 onClose 但未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 觸發 handleClose 但未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:946` | [R15] Tailwind 類別順序可能不符合標準 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:93` | [R15] Tailwind 類別順序可能不符合標準 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:159` | [R15] Tailwind 類別順序可能不符合標準 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串可能導致按鈕無文字 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/layout/stats-header.tsx:67` | [R15] Tailwind 類別順序可能不符合標準 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反專案規範</summary>

在 `SelectOptionsPopover` 中，將原本的 `const newValues` 改為 `var newValues`，違反專案規範 R20（必須使用 let 或 const）。此變數在函式內並未重新賦值，應使用 `const`。

**判斷依據**：diff 中明確將 `const` 改為 `var`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，則新增篩選器的按鈕將沒有文字，影響可用性。建議保留非空預設值，或確保所有使用處都有提供自訂文字。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且未見其他替代文字來源。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 觸發 onClose 但未清除搜尋輸入</summary>

在多選情境下，當 `autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但 `onClose` 的實作（如 `handleClose`）會清除搜尋輸入。然而此處直接呼叫 `onClose`，若父層的 `onClose` 未包含清除邏輯，可能導致搜尋文字殘留。建議統一使用 `handleClose` 或確保 `onClose` 有清除搜尋。

**判斷依據**：diff 中新增此段，但未呼叫 `setSearchInput('')`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 觸發 handleClose 但未清除搜尋輸入</summary>

在另一處多選情境中，當 `autoCloseOnSelect` 為 true 時呼叫 `handleClose()`，但 `handleClose` 會清除搜尋輸入。然而此處的 `handleClose` 定義在元件內，應會清除，但需確認此處的 `handleClose` 是否與上方相同。若相同則無問題，但建議檢查一致性。

**判斷依據**：diff 中新增此段。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:946</code> [R15] Tailwind 類別順序可能不符合標準</summary>

在 `FilterOperatorDropdown` 中，className 從 `flex items-center border-x px-3 text-sm text-muted-foreground` 改為 `flex items-center self-stretch border border-r-[0px] px-3 text-sm text-muted-foreground`。新增的 `self-stretch` 與 `border` 等類別順序可能不符合 Tailwind 標準排序（R15）。建議使用工具自動排序。

**判斷依據**：diff 中新增類別，但未依標準順序排列。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:93</code> [R15] Tailwind 類別順序可能不符合標準</summary>

在 `useUtmOptionsForField` 中，icon 的 className 從原本的 `flex items-center justify-center rounded-full bg-grey-200 px-2 py-0.5 text-xs font-medium text-grey-900 dark:bg-grey-800 dark:text-grey-100` 改為 `order-2 font-mono text-xs text-muted-foreground`。新類別順序可能不符合 Tailwind 標準排序（R15）。

**判斷依據**：diff 中替換了 className。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:159</code> [R15] Tailwind 類別順序可能不符合標準</summary>

在 `useSourceOptions` 中，icon 的 className 同樣改為 `order-2 font-mono text-xs text-muted-foreground`，可能不符合 Tailwind 標準排序（R15）。

**判斷依據**：diff 中替換了 className。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串可能導致按鈕無文字</summary>

在 `StatsFilter` 中，`addButtonText` 從條件式改為固定空字串 `''`，且 `addButtonIcon` 改為 `FunnelPlus` 圖示。若按鈕僅依賴文字，則可能無法辨識。建議確認設計意圖，或保留文字。

**判斷依據**：diff 中將原本的條件文字改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/layout/stats-header.tsx:67</code> [R15] Tailwind 類別順序可能不符合標準</summary>

在 `StatsHeader` 中，Navbar 的 className 從 `py-8` 改為 `pb-6 pt-9`，可能不符合 Tailwind 標準排序（R15）。

**判斷依據**：diff 中修改了 padding 類別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7304 (cache hit 4992) ｜ completion tokens 2001 ｜ PR #11</sub>