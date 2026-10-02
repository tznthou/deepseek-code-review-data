<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選取與建立對話框元件，並整合到 schema form 中。主要風險在於 `BlockDocumentCombobox` 的搜尋邏輯：後端查詢已使用 `like_` 過濾，前端又重複進行 `toLowerCase().includes()` 過濾，可能導致結果不一致或遺漏。此外，`BlockDocumentCreateDialog` 的錯誤處理與表單驗證流程有改進空間。整體結構清晰，測試涵蓋主要情境，但建議修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端重複過濾可能導致結果不一致 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69` | 搜尋時可能遺漏大小寫不同的結果 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理可能不完整 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤訊息未提供具體原因 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | 未處理 blockTypeSlug 非字串的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端重複過濾可能導致結果不一致</summary>

後端查詢已使用 `name: { like_: deferredSearch }` 進行過濾，但前端又用 `filteredData` 再次以 `toLowerCase().includes()` 過濾。這可能導致：
1. 後端過濾與前端過濾邏輯不一致（例如大小寫處理、萬用字元），造成使用者看到的結果與預期不同。
2. 若後端 `like_` 是大小寫敏感，而前端 `toLowerCase()` 是大小寫不敏感，則可能出現後端已排除但前端仍顯示的項目，或反之。
建議移除前端重複過濾，直接使用 `data`，或確保前後端過濾邏輯完全一致。

**判斷依據**：diff 中新增的 `filteredData` 邏輯與 `buildListFilterBlockDocumentsQuery` 中的 `like_` 條件重複。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69</code> 搜尋時可能遺漏大小寫不同的結果</summary>

後端查詢使用 `like_` 可能為大小寫敏感，但前端 `toLowerCase()` 假設大小寫不敏感。若後端為大小寫敏感，使用者輸入大寫字母時，後端可能回傳空陣列，但前端仍會嘗試過濾，導致無結果。建議確認後端 `like_` 的大小寫行為，並調整前端邏輯或後端查詢以保持一致。

**判斷依據**：前端使用 `toLowerCase()` 進行大小寫不敏感比較，但後端 `like_` 可能大小寫敏感。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理可能不完整</summary>

`onSave` 中呼叫 `validateForm` 後，若 `errors.length > 0` 則直接 return，但未將錯誤顯示給使用者。使用者可能不知道驗證失敗的原因。建議將 `errors` 傳遞給 `LazySchemaForm` 或顯示錯誤訊息。

**判斷依據**：diff 中 `onSave` 函式在驗證失敗時僅 return，未處理錯誤顯示。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤訊息未提供具體原因</summary>

`onError` 回呼中僅顯示通用錯誤訊息「Unknown error while creating block.」，未包含伺服器回傳的錯誤細節。這可能讓使用者難以理解失敗原因。建議將 `err` 的訊息（若存在）顯示給使用者。

**判斷依據**：diff 中 `onError` 使用固定錯誤訊息，未利用 `err` 物件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> 未處理 blockTypeSlug 非字串的情況</summary>

程式碼檢查 `typeof blockTypeSlug === "string"`，但若 `blockTypeSlug` 存在但非字串（例如數字），則不會渲染任何內容，且不會有錯誤提示。這可能導致表單欄位靜默消失。建議在非字串時拋出錯誤或顯示警告。

**判斷依據**：diff 中僅在 `blockTypeSlug` 為字串時渲染元件，未處理其他型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12035 (cache hit 11264) ｜ completion tokens 1416 ｜ PR #4</sub>