<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了分析篩選器的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示、以及修改預設 i18n 字串為空字串。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕或提示文字消失，影響可用性；另外 autoCloseOnSelect 的實作在 multiselect 中呼叫 onClose 但未清除搜尋輸入，可能造成狀態不一致。整體而言，變更方向合理，但需修正上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串設為空字串可能導致 UI 文字消失 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中關閉時未清除搜尋輸入 | 0.80 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串可能導致按鈕無文字 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串設為空字串可能導致 UI 文字消失</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若使用此預設值且未提供自訂 i18n，按鈕或提示文字將變成空白，影響使用者理解與操作。建議保留非空預設值，或確認所有使用情境都有提供自訂 i18n。

**判斷依據**：diff 中第 105 行將原本的 'Add filter' 改為空字串，且第 122 行同樣將 addFilterTitle 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中關閉時未清除搜尋輸入</summary>

在 multiselect 分支中，當 `field.autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但未呼叫 `setSearchInput('')`。若之後重新開啟 popover，搜尋輸入可能殘留上次的關鍵字，導致選項被過濾，使用者需手動清除。建議在關閉時一併清除搜尋輸入，或確認 `handleClose` 有被呼叫。

**判斷依據**：diff 中新增的 autoCloseOnSelect 處理區塊，僅呼叫 onClose，未清除搜尋輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串可能導致按鈕無文字</summary>

將 `addButtonText` 改為 `filters.length ? '' : ''`，無論是否有 filters 都傳入空字串，可能使按鈕只顯示圖示而無文字，影響可讀性。若這是刻意設計，建議確認圖示有足夠的語意或提供 aria-label。

**判斷依據**：diff 中原本根據 filters.length 顯示不同文字，現在改為一律空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5035 (cache hit 4992) ｜ completion tokens 801 ｜ PR #11</sub>