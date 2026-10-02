<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 BlockDocumentCombobox、BlockDocumentCreateDialog 以及 SchemaFormInputBlockDocument 元件，並在 SchemaFormInput 中實作 blockTypeSlug 的支援。整體結構清晰，測試涵蓋主要互動。主要風險在於 block-document-combobox.tsx 中同時使用後端過濾與前端過濾，可能導致選項不一致；此外，block-document-create-dialog.tsx 的錯誤處理與驗證流程有改進空間。建議先修正 combobox 的過濾邏輯，並確認錯誤處理與表單驗證的完整性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾與後端過濾並存可能導致選項不一致 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 驗證錯誤處理不完整，可能導致錯誤被忽略 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤訊息未提供具體錯誤細節 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | catch 區塊的錯誤處理可能導致重複提示 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:77` | blockTypeSlug 非字串時未處理，可能導致元件未渲染 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾與後端過濾並存可能導致選項不一致</summary>

查詢參數中已使用 `deferredSearch` 進行後端過濾（`name: { like_: deferredSearch }`），但又在 `filteredData` 中對 `data` 進行前端過濾。這會造成兩次過濾，且前端過濾可能與後端過濾不一致（例如後端使用不同的大小寫處理或模糊匹配）。此外，前端過濾會使 `selectedBlockDocument` 可能找不到已選取的項目（如果該項目不在目前搜尋結果中），導致顯示 fallback 文字。建議移除前端過濾，完全依賴後端過濾，或僅使用前端過濾並移除後端過濾參數。

**判斷依據**：diff 中新增的 `filteredData` 使用 `deferredSearch` 進行前端過濾，而查詢參數中已包含 `deferredSearch` 作為後端過濾條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 驗證錯誤處理不完整，可能導致錯誤被忽略</summary>

`validateForm` 回傳後，程式碼檢查 `errors.length > 0` 並直接 return，但 `errors` 是從 `useSchemaForm` 取得的狀態，可能不是最新的（因為 `validateForm` 是非同步的，且 `errors` 狀態更新可能尚未反映）。此外，`validateForm` 可能拋出錯誤，但 catch 區塊僅顯示 toast 並記錄錯誤，沒有阻止後續的 `createBlockDocument` 呼叫（因為 return 在 try 區塊內，但 catch 後會繼續執行）。建議將 `createBlockDocument` 放在 `validateForm` 成功且無錯誤後才執行，並確保錯誤狀態正確更新。

**判斷依據**：diff 中 `onSave` 函式先呼叫 `validateForm`，然後檢查 `errors.length`，但 `errors` 可能不是最新的，且 catch 區塊沒有阻止後續執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤訊息未提供具體錯誤細節</summary>

在 `onError` 回呼中，錯誤訊息固定為 "Unknown error while creating block."，沒有包含實際的錯誤訊息。這會讓使用者難以理解失敗原因，也增加除錯困難。建議從 `err` 中提取可讀的錯誤訊息（例如 `err.message`）並顯示在 toast 中。

**判斷依據**：diff 中 `onError` 回呼使用固定字串，未使用 `err` 的內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> catch 區塊的錯誤處理可能導致重複提示</summary>

`validateForm` 拋出錯誤時，catch 區塊顯示 toast 並記錄錯誤，但之後程式碼會繼續執行（因為沒有 return 或 throw），可能導致後續的 `createBlockDocument` 也被呼叫，造成重複的錯誤提示或非預期行為。建議在 catch 區塊中 return 或 throw，以阻止後續執行。

**判斷依據**：diff 中 catch 區塊沒有 return 或 throw，可能導致後續程式碼繼續執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:77</code> blockTypeSlug 非字串時未處理，可能導致元件未渲染</summary>

當 `property.blockTypeSlug` 存在但不是字串時（例如是陣列或其他型別），程式碼不會渲染任何內容，也不會拋出錯誤。這可能導致表單欄位靜默消失，使用者無法輸入。建議在非字串時拋出錯誤或提供 fallback 渲染。

**判斷依據**：diff 中新增的條件判斷僅處理字串型別，未處理其他型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12783 (cache hit 11264) ｜ completion tokens 1600 ｜ PR #4</sub>