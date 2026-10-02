<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整統計頁面的篩選器 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式與圖示、以及修改預設 i18n 文字。整體風險中等，需注意幾個可能影響使用者體驗與正確性的問題：預設 i18n 文字被改為空字串可能導致按鈕無文字；autoCloseOnSelect 在 multiselect 情境下可能造成非預期的關閉行為；部分樣式變更需確認視覺一致性。建議優先修正 i18n 空字串與 autoCloseOnSelect 的互動邏輯。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 文字改為空字串可能導致按鈕無文字 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 在 multiselect 中可能導致非預期關閉 | 0.80 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1125` | 使用 var 宣告變數可能導致作用域問題 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 改為空字串可能導致按鈕無文字 | 0.70 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1205` | PopoverContent className 條件邏輯可能導致寬度設定失效 | 0.60 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:93` | 圖示樣式變更可能影響視覺一致性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 文字改為空字串可能導致按鈕無文字</summary>

`addFilter` 與 `addFilterTitle` 的預設值從 'Add filter' 改為空字串。若使用此預設值且未提供自訂 i18n，按鈕將沒有文字，影響可用性。建議保留預設文字或提供明確的視覺替代方案。

**判斷依據**：diff 中第 105 行將 'Add filter' 改為空字串，且第 122 行同樣將 addFilterTitle 改為空字串。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 在 multiselect 中可能導致非預期關閉</summary>

在 multiselect 的 onSelect 中，若設定 autoCloseOnSelect 為 true，會在選取後呼叫 onClose 關閉 popover。這可能與 multiselect 的預期行為（允許連續選取多個選項）衝突，且 onClose 可能觸發父層狀態重置（如清除 selectedFieldKeyForOptions），導致使用者無法連續選取。建議確認此行為是否符合產品需求，或考慮僅在特定條件下關閉。

**判斷依據**：diff 中新增的 autoCloseOnSelect 處理邏輯位於 multiselect 分支內，且 onClose 在父層 Filters 中被設定為同時清除 selectedFieldKeyForOptions。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> 使用 var 宣告變數可能導致作用域問題</summary>

在 multiselect 的 onSelect 中，將 `const newValues` 改為 `var newValues`。雖然在此情境下可能無實際影響，但 var 有函式作用域且可能提升，建議維持 const 以保持一致性與可讀性。

**判斷依據**：diff 中將 const 改為 var。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 改為空字串可能導致按鈕無文字</summary>

在 StatsFilter 中，addButtonText 被設定為 `filters.length ? '' : ''`，無論是否有 filters 都是空字串。這可能使按鈕僅顯示圖示而無文字，若設計上可接受則無問題，但需確認是否為預期行為。

**判斷依據**：diff 中將原本的條件文字改為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1205</code> PopoverContent className 條件邏輯可能導致寬度設定失效</summary>

在 SelectOptionsPopover 中，className 改為 `field.className || 'w-[200px]'`。若 field.className 存在但未包含寬度設定，原本的預設寬度 w-[200px] 將被覆蓋，可能導致 popover 寬度不符合預期。建議確認所有使用此元件的 field 都有明確寬度，或調整邏輯以合併預設寬度。

**判斷依據**：diff 中將原本的 `cn('w-[200px] p-0', field.className)` 改為條件式，可能遺失預設寬度。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:93</code> 圖示樣式變更可能影響視覺一致性</summary>

將原本的圓形背景與內距移除，改為 `order-2 font-mono text-xs text-muted-foreground`。這可能使計數徽章失去原本的視覺強調，需確認是否為設計意圖。

**判斷依據**：diff 中兩處 icon 的 className 被修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5071 (cache hit 4992) ｜ completion tokens 1384 ｜ PR #11</sub>