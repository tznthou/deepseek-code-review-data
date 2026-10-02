<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示、以及修正關閉時重置搜尋輸入。整體風險中等，主要問題在於將預設 i18n 文字改為空字串可能導致無障礙與可用性問題，以及 autoCloseOnSelect 在 multiselect 情境下可能造成非預期的關閉行為。建議先修正這兩個問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 文字改為空字串可能導致按鈕無文字 | 0.80 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:122` | 預設 i18n 文字改為空字串可能導致按鈕無文字 | 0.80 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中可能造成非預期關閉 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1271` | autoCloseOnSelect 在 multiselect 中可能造成非預期關閉 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 改為空字串可能導致按鈕無文字 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 文字改為空字串可能導致按鈕無文字</summary>

將 `addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，可能導致使用預設 i18n 的應用程式顯示空白按鈕或缺少無障礙標籤。若某些使用情境未提供自訂 i18n，使用者將看不到任何文字，影響可用性與可訪問性。建議保留非空預設值，或確認所有使用此元件的應用程式都會提供自訂 i18n。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且未見其他補償措施。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設 i18n 文字改為空字串可能導致按鈕無文字</summary>

將 `addFilterTitle` 的預設值從 'Add filter' 改為空字串，可能導致使用預設 i18n 的應用程式顯示空白按鈕或缺少無障礙標籤。若某些使用情境未提供自訂 i18n，使用者將看不到任何文字，影響可用性與可訪問性。建議保留非空預設值，或確認所有使用此元件的應用程式都會提供自訂 i18n。

**判斷依據**：diff 中將原本的 'Add filter' 改為空字串，且未見其他補償措施。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中可能造成非預期關閉</summary>

在 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { onClose?.(); }`，但此處呼叫的 `onClose` 可能只關閉 popover 而不會重置選取狀態，且與下方註解「For multiselect, don't close the popover to allow multiple selections」矛盾。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

**判斷依據**：diff 中新增的 autoCloseOnSelect 處理與既有註解衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1271</code> autoCloseOnSelect 在 multiselect 中可能造成非預期關閉</summary>

在另一個 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { handleClose(); }`，但此處呼叫的 `handleClose` 會同時重置搜尋輸入並呼叫 `onClose`，可能導致 popover 關閉且搜尋被清空。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

**判斷依據**：diff 中新增的 autoCloseOnSelect 處理與既有註解衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 改為空字串可能導致按鈕無文字</summary>

將 `addButtonText` 從條件式文字改為空字串，可能導致按鈕只顯示圖示而無文字，影響可用性。若設計上希望只顯示圖示，建議使用 `aria-label` 提供無障礙標籤。

**判斷依據**：diff 中將原本的 'Add filter' 或 'Filter' 改為空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5071 (cache hit 1536) ｜ completion tokens 1320 ｜ PR #11</sub>