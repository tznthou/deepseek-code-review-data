<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了區塊文件參考（block document reference）的 UI 元件，包含 Combobox 選擇器、建立對話框，以及整合進 SchemaForm。整體架構合理，但存在幾個需要修正的問題：最嚴重的是 `block-document-combobox.tsx` 中對 `deferredSearch` 的過濾邏輯可能導致選取項目消失；其次是 `block-document-create-dialog.tsx` 中 `validateForm` 的錯誤處理不完整，可能讓使用者誤以為驗證通過；另外有幾個型別安全與程式碼風格的問題。建議先修正 Combobox 的過濾邏輯與驗證流程，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 選取項目可能因過濾邏輯而消失 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 驗證錯誤處理不完整，可能導致使用者誤以為驗證通過 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 前端過濾與後端查詢重複，可能造成不必要的效能負擔 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69` | 使用 `toLowerCase()` 進行大小寫不敏感比較可能與後端不一致 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186` | 錯誤訊息不夠具體，可能難以除錯 | 0.60 |
| 🔹 | Nit | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 縮排不一致：使用空格而非 tab | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 選取項目可能因過濾邏輯而消失</summary>

在 `BlockDocumentComboboxImplementation` 中，`filteredData` 是根據 `deferredSearch` 對 `data` 進行過濾，但 `data` 本身已經由後端查詢參數 `name: { like_: deferredSearch }` 過濾。這導致當使用者輸入搜尋字串時，後端只回傳符合該字串的項目，前端再過濾一次，結果可能因為大小寫或部分匹配的差異而排除掉已選取的項目。例如，使用者選取了名為 `MyBlock` 的項目，然後輸入 `my` 進行搜尋，後端可能回傳 `MyBlock`（因為 `like_` 可能不區分大小寫），但前端 `toLowerCase().includes()` 會將 `MyBlock` 轉為 `myblock`，與 `my` 比較，結果為 `false`，導致該項目從列表中消失，即使它已被選取。這會造成使用者困惑，且可能無法再次選取。

建議：移除前端的 `filteredData` 過濾，直接使用 `data`，因為後端已經處理了搜尋。或者，如果後端搜尋不區分大小寫，前端也應該使用不區分大小寫的比較，但更簡單的做法是信任後端。

**判斷依據**：diff 中新增的 `filteredData` 邏輯與 `buildListFilterBlockDocumentsQuery` 中的 `name: { like_: deferredSearch }` 重複，且前端過濾可能因大小寫處理不一致而排除已選取項目。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 驗證錯誤處理不完整，可能導致使用者誤以為驗證通過</summary>

在 `onSave` 中，呼叫 `await validateForm({ schema: values })` 後，檢查 `errors.length > 0` 來決定是否繼續。但 `validateForm` 可能不會更新 `errors` 狀態，或者 `errors` 是從 `useSchemaForm` 取得的，而 `validateForm` 可能回傳一個 Promise，但錯誤是透過其他方式回報。如果 `validateForm` 拋出例外，會被 `catch` 捕捉並顯示錯誤，但如果它只是設定 `errors` 狀態，而 `errors` 的更新是非同步的，那麼 `errors.length` 可能仍然是 0，導致程式繼續執行 `createBlockDocument`，即使表單資料無效。這可能造成建立無效的區塊文件。

建議：確認 `validateForm` 的回傳值或錯誤處理機制。如果 `validateForm` 會回傳一個布林值或拋出例外，應該使用該結果來決定是否繼續。或者，使用 `useSchemaForm` 提供的驗證狀態來控制提交按鈕的 disabled 狀態。

**判斷依據**：diff 中新增的驗證邏輯依賴 `errors` 狀態，但未確認 `validateForm` 是否會同步更新 `errors`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 前端過濾與後端查詢重複，可能造成不必要的效能負擔</summary>

`filteredData` 對 `data` 進行前端過濾，但 `data` 已經由後端根據 `deferredSearch` 過濾。這導致每次搜尋字串變化時，前端都會對整個 `data` 陣列進行一次過濾，雖然 `data` 的大小受限於 `limit: 50`，但這仍然是不必要的計算。此外，如果後端搜尋邏輯與前端不一致，可能導致結果不一致。建議移除前端過濾，直接使用 `data`。

**判斷依據**：diff 中新增的 `filteredData` 與 `buildListFilterBlockDocumentsQuery` 中的 `name: { like_: deferredSearch }` 重複。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69</code> 使用 `toLowerCase()` 進行大小寫不敏感比較可能與後端不一致</summary>

前端使用 `toLowerCase()` 進行大小寫不敏感比較，但後端的 `like_` 查詢可能使用不同的規則（例如，可能區分大小寫，或使用不同的 collation）。這可能導致前端過濾結果與後端不一致，例如後端回傳了符合的項目，但前端將其過濾掉。建議依賴後端過濾，或確保前後端使用相同的比較規則。

**判斷依據**：diff 中新增的 `toLowerCase()` 呼叫可能與後端查詢不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186</code> 錯誤訊息不夠具體，可能難以除錯</summary>

在 `catch` 區塊中，錯誤訊息固定為 "Unknown error while validating block data."，但實際上可能有多種錯誤原因。建議將 `err` 的訊息包含在錯誤訊息中，或使用更精確的錯誤處理。

**判斷依據**：diff 中新增的 `catch` 區塊使用固定錯誤訊息。

</details>

<details><summary>🔹 <b>Nit</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 縮排不一致：使用空格而非 tab</summary>

在 `filteredData` 的 `useMemo` 中，縮排使用了空格（兩個空格），而專案規範要求使用 tab（R09）。這可能導致 lint 錯誤。建議將縮排改為 tab。

**判斷依據**：diff 中新增的程式碼縮排為空格，違反 R09。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12783 (cache hit 12672) ｜ completion tokens 2022 ｜ PR #4</sub>