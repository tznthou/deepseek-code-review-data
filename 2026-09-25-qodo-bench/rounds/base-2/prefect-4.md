<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了區塊文件（block document）的選取器與建立對話框，並整合到 schema form 中。主要風險在於建立對話框的錯誤處理不完整、驗證邏輯有缺陷，以及選取器的搜尋功能可能失效。建議先修正建立對話框的錯誤處理與驗證流程，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 驗證錯誤時仍會建立區塊文件 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立失敗時錯誤訊息不明確 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋功能可能失效 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾可能造成效能問題 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 驗證錯誤時未顯示錯誤訊息 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 驗證錯誤時仍會建立區塊文件</summary>

在 `onSave` 中，呼叫 `validateForm` 後，即使 `errors.length > 0`，程式碼只是 `return`，但 `createBlockDocument` 仍會被呼叫。這會導致驗證失敗時仍建立區塊文件，造成資料不一致。

建議：在 `validateForm` 失敗時直接 return，不要繼續執行建立邏輯。

**判斷依據**：diff 中第 176-180 行顯示驗證後僅檢查 errors 並 return，但未阻止後續的 createBlockDocument 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立失敗時錯誤訊息不明確</summary>

在 `onError` 回呼中，錯誤訊息固定為 "Unknown error while creating block."，未使用 API 回傳的錯誤訊息。這會讓使用者無法得知失敗原因。

建議：從 `err` 中提取可讀的錯誤訊息，或至少記錄完整的錯誤物件。

**判斷依據**：diff 中第 190-194 行顯示 onError 處理，訊息固定且未利用 err 的內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋功能可能失效</summary>

`filteredData` 使用 `deferredSearch` 進行前端過濾，但 `useSuspenseQuery` 的查詢參數中也使用了 `deferredSearch` 進行後端過濾。這可能導致前端過濾與後端過濾不一致，或前端過濾重複執行。

建議：移除前端過濾，完全依賴後端查詢；或移除後端過濾，只在前端過濾。

**判斷依據**：diff 中第 63-67 行顯示前端過濾，而第 50-58 行的查詢參數中也包含 `deferredSearch`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾可能造成效能問題</summary>

當 `data` 很大時，每次 `deferredSearch` 變化都會重新過濾整個陣列。雖然有 `useMemo`，但若資料量龐大，仍可能造成效能瓶頸。

建議：考慮使用後端分頁或虛擬化列表。

**判斷依據**：diff 中第 63-67 行顯示前端過濾邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 驗證錯誤時未顯示錯誤訊息</summary>

當 `validateForm` 回傳錯誤時，程式碼僅 `return`，未向使用者顯示任何錯誤訊息。使用者可能不知道表單驗證失敗。

建議：在驗證失敗時顯示錯誤訊息，例如使用 toast 或表單錯誤提示。

**判斷依據**：diff 中第 176-179 行顯示驗證失敗時僅 return，未處理錯誤顯示。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11333 (cache hit 11264) ｜ completion tokens 1285 ｜ PR #4</sub>