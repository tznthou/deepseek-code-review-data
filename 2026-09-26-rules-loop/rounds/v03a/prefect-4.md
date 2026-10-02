<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了區塊文件（block document）的選取與建立元件，並整合進 schema form 中。主要風險在於 `block-document-combobox.tsx` 中同時使用後端過濾與前端過濾，可能導致選取項目被過濾掉而無法顯示；此外，`block-document-create-dialog.tsx` 中表單驗證與提交的錯誤處理有缺陷，可能造成使用者困惑或提交無效資料。整體架構合理，但需修正上述問題後再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾可能導致已選取的區塊文件無法顯示 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理不完整，可能提交無效資料 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立區塊文件失敗時僅顯示通用錯誤，缺乏詳細資訊 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:48` | 搜尋輸入未防抖，可能導致過多 API 請求 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:63` | 查詢參數 `limit: 50` 可能不足以顯示所有區塊文件 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | 未處理 `blockTypeSlug` 非字串的情況 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾可能導致已選取的區塊文件無法顯示</summary>

在 `BlockDocumentComboboxImplementation` 中，`filteredData` 是根據 `deferredSearch` 對 `data` 進行前端過濾的結果，而 `selectedBlockDocument` 是從 `filteredData` 中尋找。當使用者選取一個區塊文件後，若輸入搜尋字串，`filteredData` 可能不包含已選取的項目，導致 `selectedBlockDocument` 為 `undefined`，觸發器顯示「Select a block...」而非已選取的名稱。這會造成使用者困惑，且可能誤以為選取已失效。

建議：
- 移除前端過濾，完全依賴後端查詢（`deferredSearch` 已傳入 query），或
- 在計算 `selectedBlockDocument` 時，若 `filteredData` 中找不到，則從 `data` 中尋找，確保已選取項目始終可顯示。

**判斷依據**：diff 中新增的 `filteredData` 與 `selectedBlockDocument` 邏輯，以及 `ComboboxTrigger` 使用 `selectedBlockDocument?.name` 顯示。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理不完整，可能提交無效資料</summary>

在 `onSave` 中，呼叫 `validateForm({ schema: values })` 後，僅檢查 `errors.length > 0` 就返回，但未將錯誤顯示給使用者。此外，`validateForm` 可能拋出例外，但 catch 區塊只顯示通用錯誤訊息，未提供具體驗證失敗原因。這可能導致使用者無法得知哪些欄位有誤，或誤以為提交成功。

建議：
- 在 `validateForm` 失敗時，將錯誤訊息顯示在對應的 schema form 欄位旁。
- 在 catch 區塊中，若錯誤來自驗證，應顯示具體的驗證錯誤而非通用訊息。

**判斷依據**：diff 中 `onSave` 函式的實作，未處理 `errors` 的顯示。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立區塊文件失敗時僅顯示通用錯誤，缺乏詳細資訊</summary>

在 `createBlockDocument` 的 `onError` 回呼中，僅顯示「Unknown error while creating block.」並將錯誤記錄到 console。這對使用者除錯幫助有限，且可能隱藏重要錯誤細節（如伺服器回傳的驗證錯誤）。

建議：
- 從 `err` 中提取可讀的錯誤訊息（例如 `err.message` 或伺服器回傳的錯誤內容）並顯示在 toast 中。

**判斷依據**：diff 中 `onError` 的實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:48</code> 搜尋輸入未防抖，可能導致過多 API 請求</summary>

`deferredSearch` 使用 `useDeferredValue`，但 `useDeferredValue` 僅延遲渲染，不會減少 API 請求頻率。每次輸入變化都會觸發新的 query，可能導致大量請求。建議使用 debounce（例如 `useDebounce`）來限制請求頻率。

**判斷依據**：diff 中 `useDeferredValue` 的使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:63</code> 查詢參數 `limit: 50` 可能不足以顯示所有區塊文件</summary>

查詢限制為 50 筆，若區塊文件超過 50 個，使用者可能無法選取到後面的項目。建議實作分頁或增加 limit，或提供載入更多功能。

**判斷依據**：diff 中 query 的 `limit` 設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> 未處理 `blockTypeSlug` 非字串的情況</summary>

程式碼檢查 `typeof blockTypeSlug === "string"`，但若 `blockTypeSlug` 為其他型別（例如陣列或物件），則不會渲染任何內容，且沒有錯誤提示。這可能導致表單欄位靜默消失。建議加入 fallback 或拋出錯誤。

**判斷依據**：diff 中新增的條件判斷。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12838 (cache hit 11264) ｜ completion tokens 1707 ｜ PR #4</sub>