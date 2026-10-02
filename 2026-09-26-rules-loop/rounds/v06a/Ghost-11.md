<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了篩選器元件的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示，以及修改 Stats 頁面的篩選器設定。主要風險在於將預設 i18n 字串改為空字串可能導致 UI 顯示空白，以及使用 var 宣告違反程式碼規範。此外，部分樣式變更可能影響可讀性，但整體邏輯變更尚屬合理。建議優先修正空字串與 var 的問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 字串設為空字串可能導致 UI 顯示空白 | 0.90 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數違反程式碼規範 | 0.95 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串可能導致按鈕無文字 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 字串設為空字串可能導致 UI 顯示空白</summary>

將 `addFilter` 和 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，若未提供自訂 i18n 設定，按鈕文字將為空白，影響使用者體驗。建議保留非空預設值，或確保所有使用處都提供自訂文字。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數違反程式碼規範</summary>

此處將 `const` 改為 `var`，違反 R20 規範（應使用 let 或 const）。建議改回 `const` 或使用 `let`。

**判斷依據**：diff 中將原本的 const 改為 var。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串可能導致按鈕無文字</summary>

將 `addButtonText` 改為 `filters.length ? '' : ''`，無論是否有篩選器，按鈕文字皆為空字串，可能使按鈕僅顯示圖示而無文字，影響可讀性。建議保留有意義的文字或確認設計意圖。

**判斷依據**：diff 中原本根據 filters.length 顯示 'Add filter' 或 'Filter'，現改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7370 (cache hit 4992) ｜ completion tokens 684 ｜ PR #11</sub>