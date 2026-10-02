<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 調整了篩選器元件的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式、以及修改統計頁面的篩選器設定。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字；另外 autoCloseOnSelect 的關閉邏輯在多選情境下可能與 maxSelections 限制衝突，造成狀態不一致。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/shade/src/components/ui/filters.tsx:105` | 預設的 addFilter 文字被設為空字串，導致按鈕無文字 | 0.95 |
| 🛑 | Blocker | `apps/shade/src/components/ui/filters.tsx:122` | 預設的 addFilterTitle 文字被設為空字串，導致提示文字消失 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在多選時直接呼叫 onClose，可能繞過 maxSelections 限制 | 0.80 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 在另一處多選分支中呼叫 handleClose，可能導致狀態不一致 | 0.80 |
| ⚠️ | Major | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 被設為空字串，導致按鈕無文字 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設的 addFilter 文字被設為空字串，導致按鈕無文字</summary>

DEFAULT_I18N 中的 addFilter 從 'Add filter' 改為空字串。這會讓所有未自訂 i18n 的篩選器按鈕顯示為空白，嚴重影響可用性。建議保留預設文字，或在使用端明確提供替代文字。

**判斷依據**：diff 中第 105 行將原本的 'Add filter' 改為空字串。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設的 addFilterTitle 文字被設為空字串，導致提示文字消失</summary>

DEFAULT_I18N 中的 addFilterTitle 從 'Add filter' 改為空字串。這會讓按鈕的 title 屬性（hover 提示）消失，影響無障礙性與使用者體驗。建議保留預設文字。

**判斷依據**：diff 中第 122 行將原本的 'Add filter' 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在多選時直接呼叫 onClose，可能繞過 maxSelections 限制</summary>

在多選分支中，當選取後若 field.autoCloseOnSelect 為 true，會直接呼叫 onClose?.()。但 onClose 通常會關閉 popover 並可能重置狀態，若使用者已達 maxSelections 上限，前面的 return 會阻止 onChange，但 autoCloseOnSelect 仍會執行，導致 popover 關閉但值未更新，造成狀態不一致。建議將 autoCloseOnSelect 的處理放在 onChange 成功之後，並確認 maxSelections 限制已正確處理。

**判斷依據**：diff 中第 1134-1136 行新增了 autoCloseOnSelect 的處理，但未考慮 maxSelections 的 return 情境。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 在另一處多選分支中呼叫 handleClose，可能導致狀態不一致</summary>

在另一個多選分支中，當 autoCloseOnSelect 為 true 時呼叫 handleClose()，但 handleClose 會 setOpen(false) 並清空搜尋輸入。若使用者已達 maxSelections 上限，前面的 return 會阻止 onChange，但 handleClose 仍會執行，導致 popover 關閉但值未更新。建議將 handleClose 的呼叫放在 onChange 成功之後。

**判斷依據**：diff 中第 1271-1273 行新增了 autoCloseOnSelect 的處理，但未考慮 maxSelections 的 return 情境。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 被設為空字串，導致按鈕無文字</summary>

在 StatsFilter 中，addButtonText 從原本的條件式文字改為空字串。這會讓篩選器按鈕完全沒有文字，僅顯示圖示，可能造成使用者困惑。建議保留原本的 'Add filter' 或 'Filter' 文字，或提供明確的 aria-label。

**判斷依據**：diff 中第 500 行將原本的條件式文字改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5035 (cache hit 1408) ｜ completion tokens 1197 ｜ PR #11</sub>