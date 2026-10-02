<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選取與建立對話框元件，並整合進 schema form 中。主要風險在於 `block-document-combobox.tsx` 中重複的客戶端過濾邏輯可能導致選取項目無法正確顯示，以及 `block-document-create-dialog.tsx` 中表單驗證與錯誤處理的潛在問題。建議優先修正 combobox 的過濾邏輯，並補強建立對話框的錯誤處理與測試。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 重複的客戶端過濾可能導致選取項目無法顯示 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理不完整 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤訊息未提供具體原因 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | catch 區塊的錯誤訊息同樣未提供具體原因 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 客戶端過濾可能導致效能問題 | 0.50 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 缺少對 `validateForm` 拋出錯誤的處理 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 重複的客戶端過濾可能導致選取項目無法顯示</summary>

`useSuspenseQuery` 已經使用 `deferredSearch` 進行伺服器端過濾，但 `filteredData` 又對 `data` 進行一次客戶端過濾。這可能導致當 `selectedBlockDocumentId` 對應的項目不在目前搜尋結果中時，`selectedBlockDocument` 會是 `undefined`，使得 combobox 顯示 placeholder 而非已選取的名稱。建議移除客戶端過濾，直接使用 `data`，或將 `selectedBlockDocument` 的搜尋範圍改為 `data` 而非 `filteredData`。

**判斷依據**：diff 中新增的 `filteredData` 邏輯與 `useSuspenseQuery` 的 `deferredSearch` 參數重複，且 `selectedBlockDocument` 使用 `filteredData` 進行查找。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理不完整</summary>

`validateForm` 被呼叫後，若 `errors.length > 0` 則直接 return，但沒有將錯誤顯示給使用者。使用者可能無法得知驗證失敗的原因。建議在 UI 中顯示 `errors` 的內容，或使用 react-hook-form 的錯誤處理機制。

**判斷依據**：diff 中 `onSave` 函式在 `errors.length > 0` 時僅 return，沒有顯示錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤訊息未提供具體原因</summary>

`onError` 回呼中僅顯示 'Unknown error while creating block.'，沒有使用 `err` 中的訊息。這會讓使用者難以除錯。建議從 `err` 中提取可讀的錯誤訊息並顯示。

**判斷依據**：diff 中 `onError` 回呼的錯誤訊息固定，未使用 `err` 參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> catch 區塊的錯誤訊息同樣未提供具體原因</summary>

`catch` 區塊顯示 'Unknown error while validating block data.'，沒有使用 `err` 中的訊息。建議從 `err` 中提取可讀的錯誤訊息並顯示。

**判斷依據**：diff 中 `catch` 區塊的錯誤訊息固定，未使用 `err` 參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 客戶端過濾可能導致效能問題</summary>

`filteredData` 在每次 `data` 或 `deferredSearch` 變化時重新計算，但 `data` 可能包含大量項目（最多 50 個），影響不大。然而，若未來限制提高，可能造成不必要的計算。建議直接使用伺服器端過濾結果。

**判斷依據**：diff 中新增的 `filteredData` 邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 缺少對 `validateForm` 拋出錯誤的處理</summary>

`validateForm` 可能拋出錯誤，但 `onSave` 中沒有 try-catch 包圍，錯誤會直接拋出到全域。建議將 `validateForm` 呼叫包在 try-catch 中，或使用 `.catch` 處理。

**判斷依據**：diff 中 `onSave` 函式沒有 try-catch 包圍 `validateForm`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12838 (cache hit 12800) ｜ completion tokens 1541 ｜ PR #4</sub>