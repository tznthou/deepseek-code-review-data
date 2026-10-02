<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件參考的 UI 元件，包含 combobox、建立對話框，並整合到 schema form。主要風險在於前端資料處理與型別安全：`filteredData` 的客戶端過濾可能因大小寫或特殊字元導致結果不一致；`blockSchema.fields` 的型別斷言可能隱藏執行時期錯誤；`validateForm` 的錯誤處理邏輯有缺陷，可能讓無效資料通過。此外，部分測試與 Storybook 的 mock 資料可能與實際 API 回應不符。建議優先修正資料驗證與型別安全問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 客戶端過濾可能導致結果不一致 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:129` | 型別斷言可能隱藏執行時期錯誤 | 0.75 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | validateForm 錯誤處理邏輯有缺陷 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:100` | onSelect 可能收到 undefined | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | blockTypeSlug 非字串時無處理 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 客戶端過濾可能導致結果不一致</summary>

`filteredData` 使用 `toLowerCase()` 進行客戶端過濾，但後端查詢可能使用不同的比對規則（例如區分大小寫或使用 `like_` 的萬用字元）。這可能導致使用者看到的選項與實際查詢結果不一致，特別是在名稱包含大寫字母或特殊字元時。建議移除客戶端過濾，完全依賴後端查詢，或確保前後端使用相同的比對邏輯。

**判斷依據**：diff 中新增的 `filteredData` 使用 `toLowerCase()` 進行過濾，但後端查詢參數 `name: { like_: deferredSearch }` 可能使用不同的比對方式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:129</code> 型別斷言可能隱藏執行時期錯誤</summary>

`blockSchema.fields` 被斷言為 `PrefectSchemaObject`，但實際資料可能不符合該型別。如果 API 回傳的 schema 結構有誤，可能導致 `LazySchemaForm` 渲染失敗或產生難以除錯的錯誤。建議使用 runtime validation（例如 zod）來驗證 schema 結構，而不是直接斷言。

**判斷依據**：diff 中 `blockSchema.fields` 被強制轉型為 `PrefectSchemaObject`，沒有進行任何驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> validateForm 錯誤處理邏輯有缺陷</summary>

`validateForm` 被呼叫後，程式碼檢查 `errors.length > 0` 來決定是否繼續。但 `errors` 是從 `useSchemaForm` 取得的 state，可能不會在 `await validateForm` 後立即更新，導致檢查到舊的錯誤陣列。此外，`validateForm` 可能拋出例外，但 catch 區塊只顯示錯誤訊息，沒有阻止後續的 `createBlockDocument` 呼叫。建議改為讓 `validateForm` 直接回傳驗證結果，或使用更可靠的方式取得驗證狀態。

**判斷依據**：diff 中 `validateForm` 被 await，但 `errors` 是外部 state，可能不會同步更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:100</code> onSelect 可能收到 undefined</summary>

`ComboboxCommandItem` 的 `onSelect` 回呼參數 `value` 的型別可能是 `string | undefined`，但程式碼直接將它傳給 `onSelect`，而 `onSelect` 的型別是 `(blockDocumentId: string | undefined) => void`，所以型別上沒有問題。但若 `value` 為 undefined，會將 undefined 傳給父元件，可能導致非預期的行為。建議明確處理 undefined 的情況。

**判斷依據**：diff 中 `onSelect` 直接傳遞 `value`，沒有檢查是否為 undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> blockTypeSlug 非字串時無處理</summary>

當 `property.blockTypeSlug` 存在但不是字串時（例如是陣列或其他型別），程式碼不會渲染任何內容，也不會拋出錯誤。這可能導致表單欄位靜默消失，使用者無法輸入。建議加入 else 分支處理非字串的情況，或至少記錄警告。

**判斷依據**：diff 中只有 `typeof blockTypeSlug === "string"` 的條件分支，沒有 else 處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12818 (cache hit 12800) ｜ completion tokens 1517 ｜ PR #4</sub>