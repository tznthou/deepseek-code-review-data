<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 BlockDocumentCombobox 與 BlockDocumentCreateDialog 元件，並將 blockTypeSlug 的 schema form 輸入從未實作改為實際的 block document 選擇器。主要風險在於前端資料過濾邏輯可能造成使用者選不到已選取的 block document、錯誤處理不完整，以及部分型別轉換不夠嚴謹。建議優先修正 combobox 的過濾邏輯與錯誤處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾可能導致已選取的 block document 無法顯示 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | 錯誤處理不完整：validateForm 拋出錯誤時未回報使用者 | 0.75 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立 block document 的錯誤處理未提供具體錯誤訊息 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾與後端查詢重複，可能造成不一致 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:129` | 型別轉換 `as unknown as PrefectSchemaObject` 可能隱藏錯誤 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | 未處理 `blockTypeSlug` 非字串的情況 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾可能導致已選取的 block document 無法顯示</summary>

`filteredData` 使用 `deferredSearch` 對 `blockDocument.name` 進行前端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。當使用者已選取某個 block document，然後輸入搜尋字串，若該 block document 的名稱不符合搜尋條件，它會從 `filteredData` 中消失，導致 `selectedBlockDocument` 變成 `undefined`，觸發器顯示「Select a block...」而不是已選取的名稱。這會造成 UI 不一致，使用者可能誤以為選取已被清除。

建議：已選取的 block document 應始終顯示，不受搜尋過濾影響。可以在 `filteredData` 中保留已選取的項目，或將 `selectedBlockDocument` 的搜尋範圍改為原始 `data`。

**判斷依據**：diff 中新增的 `filteredData` 與 `selectedBlockDocument` 邏輯，`selectedBlockDocument` 依賴 `filteredData`，而 `filteredData` 會因搜尋字串而排除不符合的項目。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> 錯誤處理不完整：validateForm 拋出錯誤時未回報使用者</summary>

在 `onSave` 中，`await validateForm({ schema: values })` 若拋出例外，會被 `catch` 捕捉並顯示「Unknown error while validating block data.」的 toast，但沒有提供具體錯誤訊息。使用者無法得知驗證失敗的原因，只能看到通用錯誤，增加除錯困難。

建議：在 catch 中顯示 `err` 的訊息（如果有的話），或將錯誤訊息傳遞給 toast。

**判斷依據**：diff 中 `onSave` 的 catch 區塊只顯示固定訊息。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立 block document 的錯誤處理未提供具體錯誤訊息</summary>

`createBlockDocument` 的 `onError` 回呼中，只顯示「Unknown error while creating block.」的 toast，並將錯誤記錄到 console。使用者無法得知建立失敗的具體原因（例如名稱重複、權限不足等），影響使用者體驗。

建議：從 `err` 中提取可讀的錯誤訊息並顯示在 toast 中。

**判斷依據**：diff 中 `onError` 回呼的實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾與後端查詢重複，可能造成不一致</summary>

後端查詢已使用 `deferredSearch` 進行 `name` 的 `like_` 過濾，但前端又對 `data` 進行一次 `toLowerCase().includes()` 過濾。這可能導致後端已過濾的結果被前端再次過濾，但兩者的比對邏輯可能不同（例如大小寫處理、模糊比對），造成使用者看到的選項與預期不符。此外，前端過濾會增加不必要的計算。

建議：移除前端過濾，完全依賴後端查詢；或移除後端過濾，由前端統一處理。

**判斷依據**：diff 中同時存在後端 `like_` 過濾與前端 `filter`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:129</code> 型別轉換 `as unknown as PrefectSchemaObject` 可能隱藏錯誤</summary>

`blockSchema.fields` 被強制轉型為 `PrefectSchemaObject`，但 `fields` 的實際型別可能與 `PrefectSchemaObject` 不完全相容。這種雙重斷言（`as unknown as`）會跳過 TypeScript 的型別檢查，若 API 回傳的結構不符，可能導致執行時期錯誤。

建議：確認 `blockSchema.fields` 的實際型別，若確實相容，應使用更安全的型別收窄或驗證；否則應修正 API 型別定義。

**判斷依據**：diff 中 `blockSchema.fields as unknown as PrefectSchemaObject` 的型別斷言。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> 未處理 `blockTypeSlug` 非字串的情況</summary>

程式碼檢查 `typeof blockTypeSlug === "string"`，若為其他型別（例如陣列或物件），則不會渲染任何輸入元件，也不會顯示錯誤。這可能導致表單中該欄位靜默消失，使用者無法填寫。

建議：在 `else` 分支中處理非字串情況，例如顯示錯誤訊息或回退到其他輸入元件。

**判斷依據**：diff 中新增的條件判斷，缺少 else 分支。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12828 (cache hit 1536) ｜ completion tokens 1979 ｜ PR #4</sub>