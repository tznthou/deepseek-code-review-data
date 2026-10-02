<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了區塊文件（block document）的選取與建立對話框元件，並整合到 schema form 中。主要風險在於 `BlockDocumentCombobox` 的搜尋過濾邏輯可能導致選取項目消失、`BlockDocumentCreateDialog` 的錯誤處理與表單驗證有缺陷，以及部分程式碼違反了專案的 TypeScript 縮排規範。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋過濾邏輯可能導致已選取的項目消失 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理不完整，可能導致建立失敗但使用者未察覺 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | [R09] 縮排不一致：使用空格而非 Tab | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤處理中使用了不明確的錯誤訊息 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:77` | 未處理 blockTypeSlug 為非字串的情況 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋過濾邏輯可能導致已選取的項目消失</summary>

在 `BlockDocumentComboboxImplementation` 中，`filteredData` 是根據 `deferredSearch` 對 `data` 進行前端過濾的結果。然而，`data` 本身是透過 `useSuspenseQuery` 從後端取得的，其查詢條件已經包含了 `deferredSearch` 的 `like_` 過濾。這會造成雙重過濾，而且當使用者輸入搜尋字串時，後端回傳的資料已經被過濾，前端再過濾一次可能導致結果不一致。更嚴重的問題是，如果目前選取的 `selectedBlockDocumentId` 對應的項目不在 `filteredData` 中（例如使用者先選取了某個項目，然後輸入搜尋字串，而該項目不符合新的搜尋條件），則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」，但實際上仍有一個已選取的值。這會造成 UI 狀態與實際選取值不一致，使用者可能誤以為選取已被清除。

建議：移除前端的 `filteredData` 過濾，直接使用 `data` 作為顯示清單，因為後端已經處理了搜尋過濾。或者，如果必須保留前端過濾，則應確保 `selectedBlockDocument` 的計算不依賴於 `filteredData`，而是從完整的 `data` 中查找，以避免選取項目消失。

**判斷依據**：diff 中新增的 `filteredData` 邏輯（第 63-67 行）與 `selectedBlockDocument` 的計算（第 69-73 行）顯示了這個問題。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理不完整，可能導致建立失敗但使用者未察覺</summary>

在 `onSave` 函式中，呼叫 `validateForm` 後檢查 `errors.length > 0` 來決定是否繼續建立。然而，`validateForm` 是非同步函式，且 `errors` 是從 `useSchemaForm` 取得的狀態。在 `await validateForm` 之後，`errors` 可能尚未更新（因為 React 狀態更新是非同步的），因此 `errors.length` 可能仍然是 0，導致即使驗證失敗，程式仍會繼續執行 `createBlockDocument`。這會造成使用者看到錯誤訊息，但建立請求仍然被送出，可能產生無效的區塊文件。

建議：修改 `validateForm` 使其直接回傳驗證結果（例如 boolean 或錯誤陣列），而不是依賴外部狀態。或者，在 `validateForm` 內部處理錯誤時，直接 throw 或回傳錯誤，讓 `onSave` 可以正確處理。

**判斷依據**：diff 中 `onSave` 函式的實作（第 158-160 行）顯示了這個問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> [R09] 縮排不一致：使用空格而非 Tab</summary>

在 `filteredData` 的 `useMemo` 中，縮排使用了兩個空格，而專案規範要求使用 Tab 縮排（R09）。這會導致程式碼風格不一致，並可能觸發 lint 錯誤。請將縮排改為 Tab。

**判斷依據**：diff 中第 63-67 行的縮排顯示為兩個空格，而其他程式碼使用 Tab。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤處理中使用了不明確的錯誤訊息</summary>

在 `onError` 回呼中，錯誤訊息被硬編碼為 "Unknown error while creating block."，沒有包含實際的錯誤細節。這會讓使用者在遇到問題時無法得知具體原因，增加除錯困難。建議使用 `err.message` 或將錯誤物件傳遞給 toast，以提供更有用的資訊。

**判斷依據**：diff 中 `onError` 的實作（第 172-176 行）顯示了這個問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:77</code> 未處理 blockTypeSlug 為非字串的情況</summary>

在 `SchemaFormInput` 中，當 `property` 包含 `blockTypeSlug` 時，程式檢查 `typeof blockTypeSlug === "string"` 才渲染 `SchemaFormInputBlockDocument`。如果 `blockTypeSlug` 不是字串（例如是陣列或其他型別），則不會渲染任何內容，也不會拋出錯誤。這可能導致表單欄位靜默消失，使用者無法輸入。建議在非字串的情況下拋出錯誤或提供 fallback。

**判斷依據**：diff 中第 78-89 行的程式碼顯示了這個問題。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12035 (cache hit 12032) ｜ completion tokens 1796 ｜ PR #4</sub>