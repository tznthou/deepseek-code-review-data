<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件參照支援，包含 Combobox 元件、建立對話框，以及 SchemaForm 的整合。主要風險在於 `BlockDocumentCombobox` 的搜尋邏輯可能因大小寫或特殊字元導致結果不一致，且 `BlockDocumentCreateDialog` 的錯誤處理與表單驗證有改善空間。建議先修正搜尋邏輯與錯誤處理，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋邏輯可能因大小寫或特殊字元導致結果不一致 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:178` | 錯誤處理不完整：validateForm 可能拋出例外但未妥善處理 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:174` | 建立成功後未重置表單狀態 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:77` | blockTypeSlug 非字串時未處理 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋邏輯可能因大小寫或特殊字元導致結果不一致</summary>

在 `BlockDocumentComboboxImplementation` 中，後端查詢使用 `like_` 進行模糊匹配，但前端又用 `toLowerCase()` 進行過濾。若後端比對是 case-sensitive，則輸入大寫字母時，後端可能回傳空陣列，前端再過濾也無結果；反之若後端是 case-insensitive，前端過濾可能因特殊字元（如 regex 字元）而誤刪。建議統一由後端處理搜尋，或在前端使用與後端一致的比對邏輯。

**判斷依據**：diff 中新增的 `filteredData` 使用 `toLowerCase()` 進行前端過濾，但查詢參數 `deferredSearch` 同時傳給後端 `like_`，兩者比對邏輯可能不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:178</code> 錯誤處理不完整：validateForm 可能拋出例外但未妥善處理</summary>

`onSave` 中呼叫 `await validateForm({ schema: values })`，但 `validateForm` 可能拋出例外（例如 schema 格式錯誤），目前僅以 `try/catch` 包住並顯示通用錯誤訊息，未提供具體錯誤細節。建議在 catch 中記錄更詳細的錯誤資訊，或讓 `validateForm` 回傳結構化錯誤。

**判斷依據**：diff 中 `onSave` 的 try 區塊呼叫 `validateForm`，但 catch 區塊僅顯示通用訊息，未包含錯誤細節。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:174</code> 建立成功後未重置表單狀態</summary>

當 `createBlockDocument` 成功後，僅呼叫 `onOpenChange(false)` 和 `onCreated`，但未重置 `values` 或 `form`。若使用者再次開啟對話框，可能殘留上次的輸入。建議在成功後重置表單狀態。

**判斷依據**：diff 中 `onSuccess` 回呼未包含任何重置邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:77</code> blockTypeSlug 非字串時未處理</summary>

在 `SchemaFormInput` 中，若 `property.blockTypeSlug` 存在但型別不是字串（例如陣列或物件），目前程式碼會直接略過，導致該屬性沒有渲染任何輸入元件。建議加入 fallback 或明確處理。

**判斷依據**：diff 中僅處理 `typeof blockTypeSlug === "string"` 的情況，未處理其他型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12828 (cache hit 11264) ｜ completion tokens 1252 ｜ PR #4</sub>