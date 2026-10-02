<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要調整 Analytics 篩選器的 UI 與互動行為：新增 autoCloseOnSelect 屬性、調整樣式、修改預設 i18n 文案為空字串、以及將部分選項的計數徽章改為純文字。整體風險中等，主要問題在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字或無障礙標籤；另外 var 的使用違反專案規範，且 autoCloseOnSelect 的關閉邏輯可能造成狀態不同步。建議修正後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字或無障礙標籤 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反專案規範 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 觸發 onClose 但未更新 open 狀態，可能造成狀態不同步 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 在另一處使用 handleClose 但未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串可能導致按鈕無文字 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 的 addFilter 與 addFilterTitle 設為空字串可能導致按鈕無文字或無障礙標籤</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串。若使用此預設值且未提供自訂 i18n，則新增篩選器的按鈕將沒有可見文字，且可能缺少無障礙標籤（如 aria-label），影響可用性與可訪問性。建議保留非空預設值，或確保在空字串時有替代的圖示與無障礙標籤。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且未見其他處理空字串的邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反專案規範</summary>

在 `SelectOptionsPopover` 的 `onSelect` 中，將原本的 `const newValues` 改為 `var newValues`。這違反了專案規範 R20（必須使用 let 或 const），且 var 的函數作用域可能導致非預期的變數提升。請改回 `const`。

**判斷依據**：diff 中明確將 const 改為 var，違反 R20。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 觸發 onClose 但未更新 open 狀態，可能造成狀態不同步</summary>

在 multiselect 的 onSelect 中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但未呼叫 `setOpen(false)`。`onClose` 通常由父元件處理，可能只設定父元件的狀態，而此元件的 `open` 狀態仍為 true，導致 Popover 未關閉或後續行為異常。建議同時呼叫 `setOpen(false)` 或確保 `onClose` 會連帶更新此元件的 open 狀態。

**判斷依據**：diff 中新增此段，但未見 setOpen(false) 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 在另一處使用 handleClose 但未清除搜尋輸入</summary>

在 `SelectOptionsPopover` 的另一個 onSelect 分支中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `handleClose()`，但 `handleClose` 會呼叫 `setSearchInput('')`，這可能導致使用者在關閉後重新開啟時搜尋輸入被清空。若這是預期行為則可忽略，否則建議確認。

**判斷依據**：diff 中新增此段，handleClose 定義中包含 setSearchInput('')。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串可能導致按鈕無文字</summary>

將 `addButtonText` 改為 `filters.length ? '' : ''`，這永遠是空字串。若按鈕沒有圖示或圖示無法傳達意義，使用者將無法理解按鈕用途。建議保留有意義的文字或確保圖示具有足夠的無障礙標籤。

**判斷依據**：diff 中將原本的 'Add filter' / 'Filter' 改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6260 (cache hit 4992) ｜ completion tokens 1266 ｜ PR #11</sub>