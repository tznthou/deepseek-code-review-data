<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選取器與建立對話框，並整合至 schema form 中。主要風險在於 `block-document-combobox.tsx` 中客戶端過濾邏輯可能導致選取項目無法顯示，以及 `block-document-create-dialog.tsx` 中表單驗證與錯誤處理的潛在問題。建議優先修正這些問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73` | 客戶端過濾可能導致已選取的區塊文件無法顯示 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理邏輯可能不正確 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤處理中重複的錯誤訊息與不必要的 console.error | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋過濾同時在伺服器端與客戶端進行，可能導致不一致 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73</code> 客戶端過濾可能導致已選取的區塊文件無法顯示</summary>

`filteredData` 使用 `deferredSearch` 進行客戶端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。若使用者選取了一個區塊文件後，輸入的搜尋字串與該文件名稱不符，則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」而非已選取的名稱。

**失敗情境**：使用者選取了名為 `my_block_0` 的區塊文件，然後在搜尋框中輸入 `xyz`，此時 `filteredData` 為空，`selectedBlockDocument` 為 `undefined`，觸發器顯示佔位文字，但實際上仍有選取值。

**建議**：`selectedBlockDocument` 應從原始 `data` 中尋找，而非 `filteredData`。

**判斷依據**：diff 中第 72-76 行顯示 `selectedBlockDocument` 依賴於 `filteredData`，而 `filteredData` 是根據 `deferredSearch` 過濾後的結果。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理邏輯可能不正確</summary>

在 `onSave` 中，呼叫 `await validateForm({ schema: values })` 後，檢查 `errors.length > 0` 來決定是否繼續。但 `errors` 是從 `useSchemaForm` 取得的狀態，可能不會在 `validateForm` 後立即更新，導致檢查到舊的錯誤狀態。

**失敗情境**：使用者提交表單時，`validateForm` 發現錯誤並更新 `errors`，但由於 React 狀態更新是非同步的，`errors.length` 可能仍為 0，導致程式繼續執行 `createBlockDocument`，送出無效資料。

**建議**：`validateForm` 應回傳驗證結果（例如 boolean 或錯誤陣列），並直接使用回傳值來判斷，而不是依賴外部狀態。

**判斷依據**：diff 中第 163-166 行顯示 `validateForm` 被呼叫後立即檢查 `errors.length`，但 `errors` 是狀態變數，可能尚未更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤處理中重複的錯誤訊息與不必要的 console.error</summary>

在 `onError` 回呼中，錯誤訊息被設定為固定的「Unknown error while creating block.」，並使用 `console.error` 記錄。這可能導致使用者看到不明確的錯誤訊息，且開發者難以從日誌中區分錯誤來源。

**建議**：使用 `err.message` 或伺服器回傳的錯誤訊息來提供更具體的錯誤資訊，並考慮使用結構化日誌。

**判斷依據**：diff 中第 175-179 行顯示錯誤處理邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋過濾同時在伺服器端與客戶端進行，可能導致不一致</summary>

查詢參數中已包含 `name: { like_: deferredSearch }`，但又在客戶端使用 `filteredData` 進行過濾。這可能導致不必要的客戶端計算，且若伺服器端過濾邏輯與客戶端不同（例如大小寫處理），可能出現不一致的結果。

**建議**：移除客戶端過濾，完全依賴伺服器端過濾，或確保兩者邏輯一致。

**判斷依據**：diff 中第 64-68 行顯示客戶端過濾邏輯，而查詢參數中已有 `name: { like_: deferredSearch }`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11333 (cache hit 1536) ｜ completion tokens 1422 ｜ PR #4</sub>