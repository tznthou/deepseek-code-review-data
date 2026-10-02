<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要調整分析篩選器（filters）的 UI 與互動行為，包括新增 autoCloseOnSelect 屬性、調整樣式、修改圖示與文字，以及修正關閉行為。主要風險在於將預設 i18n 文字改為空字串，可能導致按鈕無文字；另外使用 var 宣告變數違反專案規範，且 autoCloseOnSelect 的實作在部分路徑未呼叫 handleClose，可能造成狀態不一致。建議優先修正 var 與 i18n 空字串問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/shade/src/components/ui/filters.tsx:1125` | [R20] 使用 var 宣告變數 | 0.95 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:105` | 預設 i18n 文字設為空字串 | 0.90 |
| ⚠️ | Major | `apps/shade/src/components/ui/filters.tsx:1134` | autoCloseOnSelect 未呼叫 handleClose | 0.85 |
| ⚠️ | Major | `apps/stats/src/views/Stats/components/stats-filter.tsx:498` | addButtonText 設為空字串 | 0.85 |
| 🔸 | Minor | `apps/shade/src/components/ui/filters.tsx:1201` | PopoverContent className 條件邏輯可能改變寬度 | 0.70 |
| 🔸 | Minor | `apps/stats/src/views/Stats/components/stats-filter.tsx:93` | 圖示樣式變更可能影響對齊 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/shade/src/components/ui/filters.tsx:1125</code> [R20] 使用 var 宣告變數</summary>

在 multiselect 的 onSelect 處理中，將原本的 const 改為 var 宣告 newValues。這違反專案規範 R20（必須使用 let 或 const），且 var 有函式作用域與 hoisting 問題，可能導致非預期行為。

建議改回 const 或 let。

**判斷依據**：diff 中新增行：`+                                                    var newValues = [...effectiveValues, option.value] as T[];`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:105</code> 預設 i18n 文字設為空字串</summary>

DEFAULT_I18N 中的 addFilter 與 addFilterTitle 被改為空字串。這會導致使用預設 i18n 的按鈕沒有文字，影響可用性。若是有意為之，應提供替代方案或說明。

**判斷依據**：diff 中：`-    addFilter: 'Add filter',` 改為 `+    addFilter: '',`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/shade/src/components/ui/filters.tsx:1134</code> autoCloseOnSelect 未呼叫 handleClose</summary>

在 multiselect 的 onSelect 中，當 autoCloseOnSelect 為 true 時，直接呼叫 onClose?.()，但未呼叫 handleClose。handleClose 會 setOpen(false) 並清空搜尋輸入，若未呼叫可能導致 popover 未關閉或搜尋文字殘留。

建議改為呼叫 handleClose()。

**判斷依據**：diff 中新增：`+                                                    // Auto-close if configured` 與 `+                                                    if (field.autoCloseOnSelect) {` 與 `+                                                        onClose?.();`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:498</code> addButtonText 設為空字串</summary>

addButtonText 被改為 `filters.length ? '' : ''`，這永遠是空字串，導致按鈕沒有文字。若是有意隱藏文字，應考慮使用 icon-only 按鈕或提供 aria-label。

**判斷依據**：diff 中：`-            addButtonText={filters.length ? 'Add filter' : 'Filter'}` 改為 `+            addButtonText={filters.length ? '' : ''}`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/shade/src/components/ui/filters.tsx:1201</code> PopoverContent className 條件邏輯可能改變寬度</summary>

原本 className 為 `'w-[200px] p-0'`，現在改為 `'p-0 data-[state=closed]:!animation-none data-[state=closed]:!duration-0'` 並在 cn 中條件加入 `field.className || 'w-[200px]'`。若 field.className 存在，則不會套用預設寬度，可能導致 popover 寬度不符合預期。請確認所有使用處都有提供適當的 className。

**判斷依據**：diff 中：`-            <PopoverContent align="start" className={cn('w-[200px] p-0', field.className)}>` 改為多行 className 設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/stats/src/views/Stats/components/stats-filter.tsx:93</code> 圖示樣式變更可能影響對齊</summary>

utm 選項的 icon 從原本的 badge 樣式改為 `order-2 font-mono text-xs text-muted-foreground`，可能影響選項的視覺對齊。請確認此變更符合設計預期。

**判斷依據**：diff 中：`-                    <span className="flex items-center justify-center rounded-full bg-grey-200 px-2 py-0.5 text-xs font-medium text-grey-900 dark:bg-grey-800 dark:text-grey-100">` 改為 `+                    <span className="order-2 font-mono text-xs text-muted-foreground">`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7380 (cache hit 1536) ｜ completion tokens 1472 ｜ PR #11</sub>