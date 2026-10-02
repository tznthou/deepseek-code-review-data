<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選擇器與建立對話框，並整合至 schema form 中。主要風險在於搜尋邏輯重複、錯誤處理不完整、以及缺少測試涵蓋。建議優先修正搜尋邏輯與錯誤處理，並補充測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋邏輯重複且可能導致不一致 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 錯誤處理不完整：validateForm 可能拋出例外但未正確處理 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | createBlockDocument 呼叫未處理錯誤 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73` | selectedBlockDocument 可能找不到，導致顯示錯誤 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:77` | blockTypeSlug 非字串時未處理 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋邏輯重複且可能導致不一致</summary>

`useSuspenseQuery` 的查詢參數中已使用 `deferredSearch` 進行 `name: { like_: deferredSearch }` 過濾，但又在 `filteredData` 中對 `data` 進行 `toLowerCase().includes()` 過濾。這會造成：
1. 後端過濾與前端過濾邏輯可能不一致（例如後端 like 可能區分大小寫，前端則不區分）。
2. 若後端已正確過濾，前端過濾是多餘的；若後端未正確過濾，前端過濾可能遺漏（例如後端 like 可能匹配子字串，但前端 includes 也匹配子字串，但大小寫處理不同）。
3. 效能浪費：資料已從後端過濾，前端又重複過濾。

建議：移除前端過濾，直接使用 `data`；或移除查詢參數中的 `like_`，只在前端過濾。需確認後端 `like_` 的語意（是否區分大小寫、是否為子字串匹配）。

**判斷依據**：diff 中新增的 `filteredData` 使用 `toLowerCase().includes()`，而查詢參數中已有 `name: { like_: deferredSearch }`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 錯誤處理不完整：validateForm 可能拋出例外但未正確處理</summary>

`onSave` 中呼叫 `await validateForm({ schema: values })`，但 `validateForm` 可能拋出例外（例如 schema 驗證失敗）。目前 try-catch 會捕捉例外並顯示 toast，但 `errors` 狀態可能未更新，導致使用者無法看到具體錯誤。此外，`validateForm` 回傳後檢查 `errors.length > 0`，但 `errors` 是來自 `useSchemaForm` 的狀態，可能非同步更新，導致判斷不準確。

建議：確認 `validateForm` 的行為，若會拋出例外，應在 catch 中處理並顯示具體錯誤；若不會拋出，則應依賴回傳值或狀態更新。

**判斷依據**：diff 中 `onSave` 函式內呼叫 `validateForm` 後檢查 `errors.length`，但 `errors` 可能尚未更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> createBlockDocument 呼叫未處理錯誤</summary>

`createBlockDocument` 的 `onError` 回呼中僅顯示通用錯誤訊息並 `console.error`，未提供具體錯誤細節。使用者無法得知失敗原因（例如名稱重複、權限不足等）。建議在 toast 中顯示後端回傳的錯誤訊息，或至少記錄更詳細的錯誤。

**判斷依據**：diff 中 `onError` 回呼使用固定訊息，未利用 `err` 物件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73</code> selectedBlockDocument 可能找不到，導致顯示錯誤</summary>

`selectedBlockDocument` 是從 `filteredData` 中尋找 `selectedBlockDocumentId`。若 `selectedBlockDocumentId` 存在但不在 `filteredData` 中（例如使用者已選擇但搜尋條件改變），則 `selectedBlockDocument` 為 `undefined`，觸發器會顯示「Select a block...」而非已選名稱。這可能造成使用者困惑。建議：若 `selectedBlockDocumentId` 存在但不在目前過濾結果中，仍應顯示已選名稱（可能需要額外查詢或保留已選項目）。

**判斷依據**：diff 中 `selectedBlockDocument` 依賴 `filteredData`，而 `filteredData` 會因搜尋而改變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:77</code> blockTypeSlug 非字串時未處理</summary>

在 `if ("blockTypeSlug" in property)` 區塊中，僅在 `typeof blockTypeSlug === "string"` 時渲染 `SchemaFormInputBlockDocument`。若 `blockTypeSlug` 存在但非字串（例如陣列或其他型別），則會略過此區塊，繼續執行後續的型別判斷，可能導致錯誤或未預期的行為。建議：若非字串，應拋出錯誤或明確處理。

**判斷依據**：diff 中新增的條件判斷僅處理字串，未處理其他型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12633 (cache hit 12544) ｜ completion tokens 1705 ｜ PR #4</sub>