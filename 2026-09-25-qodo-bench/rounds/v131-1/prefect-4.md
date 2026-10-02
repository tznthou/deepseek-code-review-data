<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選取與建立對話框元件，並整合至 schema form 中。主要風險在於 `BlockDocumentCombobox` 的搜尋邏輯可能因後端過濾與前端過濾不一致而導致選項遺漏，以及 `BlockDocumentCreateDialog` 中表單驗證與提交的錯誤處理不完整。建議優先修正搜尋邏輯，並補強建立對話框的錯誤處理與測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾可能導致選項遺漏 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理不完整 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立失敗時未關閉對話框或提供重試 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | 驗證失敗時未顯示錯誤 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | 未處理 blockTypeSlug 非字串的情況 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾可能導致選項遺漏</summary>

`filteredData` 使用 `deferredSearch` 進行前端過濾，但後端查詢已使用 `like_` 條件。若後端過濾與前端過濾不一致（例如大小寫敏感度、特殊字元處理），可能導致使用者輸入搜尋字串時，後端已回傳符合的資料，但前端又將其過濾掉，造成選項遺漏。建議移除前端過濾，直接使用後端回傳的 `data`，或確保前後端過濾邏輯完全一致。

**判斷依據**：diff 中新增的 `filteredData` 邏輯與後端查詢條件重複，可能造成不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理不完整</summary>

`onSave` 中呼叫 `validateForm` 後，僅檢查 `errors.length > 0` 便返回，但未將錯誤顯示給使用者。使用者可能無法得知驗證失敗的原因，導致提交看似無反應。建議將 `errors` 傳遞給 `LazySchemaForm` 或顯示錯誤訊息。

**判斷依據**：diff 中 `onSave` 函式僅檢查錯誤但未處理顯示。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立失敗時未關閉對話框或提供重試</summary>

`createBlockDocument` 的 `onError` 僅顯示 toast 錯誤，但對話框仍保持開啟，使用者可能重複提交。建議在錯誤時保持對話框開啟，但提供明確的錯誤訊息，或考慮自動關閉。

**判斷依據**：diff 中 `onError` 處理僅顯示錯誤，未變更對話框狀態。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> 驗證失敗時未顯示錯誤</summary>

`catch` 區塊僅顯示通用錯誤訊息，未提供具體驗證失敗原因。建議將 `err` 的詳細資訊納入錯誤訊息，或使用更精確的錯誤處理。

**判斷依據**：diff 中 `catch` 區塊使用通用錯誤訊息。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> 未處理 blockTypeSlug 非字串的情況</summary>

當 `property.blockTypeSlug` 存在但非字串時，程式碼未回傳任何元件，可能導致渲染中斷。建議加入 fallback 或拋出錯誤。

**判斷依據**：diff 中僅在 `blockTypeSlug` 為字串時回傳元件，否則無回傳值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11297 (cache hit 1408) ｜ completion tokens 1338 ｜ PR #4</sub>