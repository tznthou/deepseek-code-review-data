<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 BlockDocumentCombobox 與 BlockDocumentCreateDialog 元件，並在 SchemaFormInput 中實作 blockTypeSlug 的支援。主要風險在於錯誤處理不完整、缺少載入狀態、以及部分程式碼違反專案規範（如未使用 tab 縮排、未使用 SecretStr）。建議優先修正錯誤處理與型別安全問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:50` | useSuspenseQuery 缺少錯誤處理 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾可能與後端不一致 | 0.75 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | 錯誤處理不完整且可能誤導使用者 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | [R09] 縮排使用空格而非 tab | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-block-document.tsx:1` | [R09] 縮排使用空格而非 tab | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:1` | [R09] 縮排使用空格而非 tab | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:213` | 缺少載入狀態處理 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:82` | 型別斷言可能不安全 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:50</code> useSuspenseQuery 缺少錯誤處理</summary>

使用 useSuspenseQuery 時，若 API 請求失敗，錯誤會向上拋出，但此處沒有 ErrorBoundary 或錯誤處理邏輯，可能導致整個元件樹崩潰。建議加入 ErrorBoundary 或使用 useQuery 並處理 error 狀態。

**判斷依據**：diff 中新增的 useSuspenseQuery 呼叫沒有錯誤處理，且元件未包覆 ErrorBoundary。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾可能與後端不一致</summary>

後端查詢已使用 deferredSearch 進行 like_ 過濾，但前端又用 useMemo 進行另一次過濾，可能導致結果不一致（例如大小寫處理、模糊匹配規則不同）。建議只依賴後端過濾，或確保前後端邏輯一致。

**判斷依據**：diff 中同時存在後端 like_ 過濾與前端 filter，可能造成不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> 錯誤處理不完整且可能誤導使用者</summary>

在 onSave 中，validateForm 可能拋出錯誤，但 catch 區塊僅顯示通用錯誤訊息，未提供具體錯誤細節。此外，createBlockDocument 的 onError 也僅顯示通用訊息，使用者無法得知失敗原因。建議顯示後端回傳的錯誤訊息。

**判斷依據**：diff 中 catch 區塊使用固定錯誤訊息，未利用 err 內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> [R09] 縮排使用空格而非 tab</summary>

此檔案中部分行使用空格縮排，違反專案規範 R09（TypeScript 必須使用 tab 縮排）。請改用 tab。

**判斷依據**：diff 中可見行首為空格而非 tab。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-block-document.tsx:1</code> [R09] 縮排使用空格而非 tab</summary>

此檔案中部分行使用空格縮排，違反專案規範 R09。請改用 tab。

**判斷依據**：diff 中可見行首為空格而非 tab。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:1</code> [R09] 縮排使用空格而非 tab</summary>

此檔案中部分行使用空格縮排，違反專案規範 R09。請改用 tab。

**判斷依據**：diff 中可見行首為空格而非 tab。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:213</code> 缺少載入狀態處理</summary>

在提交表單時，按鈕有 loading 狀態，但 LazySchemaForm 可能也需要載入狀態。此外，若 blockType 或 blockSchemas 查詢失敗，沒有錯誤處理。建議加入對應的錯誤處理與載入指示。

**判斷依據**：diff 中 LazySchemaForm 沒有處理載入或錯誤狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:82</code> 型別斷言可能不安全</summary>

value as { $ref: string } | undefined 的斷言可能隱藏型別錯誤，若 value 不是預期格式，可能導致執行時期錯誤。建議使用型別守衛或更精確的型別。

**判斷依據**：diff 中直接使用 as 斷言，未驗證 value 結構。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12828 (cache hit 12800) ｜ completion tokens 1691 ｜ PR #4</sub>