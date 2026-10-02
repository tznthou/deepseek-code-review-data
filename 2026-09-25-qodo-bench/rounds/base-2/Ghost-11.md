<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了篩選器元件的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式、以及修改 Stats 頁面的篩選器設定。主要風險在於將預設的 addFilter 與 addFilterTitle 設為空字串，可能導致按鈕無文字；另外 autoCloseOnSelect 的實作在關閉時未清除搜尋輸入，可能造成狀態不一致。整體變更多為 UI 微調，但需確認空字串是否為預期行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設的 addFilter 文字被設為空字串 | 0.80 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:122` | 預設的 addFilterTitle 文字被設為空字串 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 關閉時未清除搜尋輸入 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 條件判斷無效 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設的 addFilter 文字被設為空字串</summary>

DEFAULT_I18N 中的 `addFilter` 從 'Add filter' 改為空字串，這會讓所有未自訂 i18n 的篩選器按鈕顯示為空白，影響可用性。若這是為了讓呼叫端自行提供文字，應確認所有使用處都有覆寫，否則建議保留預設值。

**判斷依據**：diff 中第 105 行將原本的 'Add filter' 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:122</code> 預設的 addFilterTitle 文字被設為空字串</summary>

DEFAULT_I18N 中的 `addFilterTitle` 從 'Add filter' 改為空字串，可能導致 tooltip 或 aria-label 缺失，影響無障礙性。建議保留預設文字或確認所有使用處都有提供替代文字。

**判斷依據**：diff 中第 122 行將原本的 'Add filter' 改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 關閉時未清除搜尋輸入</summary>

在 multiselect 的 onSelect 中，當 `autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但 `onClose` 的實作（handleClose）會清除搜尋輸入（setSearchInput('')），然而此處直接呼叫 onClose 而非 handleClose，可能導致搜尋輸入未清除。建議統一使用 handleClose 或確保 onClose 有清除邏輯。

**判斷依據**：diff 中新增的 autoCloseOnSelect 區塊呼叫 onClose，但未呼叫 setSearchInput('')。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 條件判斷無效</summary>

`addButtonText={filters.length ? '' : ''}` 無論 filters.length 為何都傳入空字串，條件判斷沒有作用。若意圖是根據是否有 filters 顯示不同文字，應提供實際文字；若不需要文字，可直接傳入空字串或省略。

**判斷依據**：diff 中將原本的條件文字改為兩個空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5071 (cache hit 4992) ｜ completion tokens 908 ｜ PR #11</sub>