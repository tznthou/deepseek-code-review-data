<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件參考（block document reference）的支援，包含 Combobox 元件、建立對話框，以及整合進 SchemaForm。主要風險在於建立對話框中的表單驗證邏輯（validateForm 後未正確檢查錯誤）、錯誤處理不一致（console.error 可能洩漏敏感資訊），以及 Combobox 的搜尋邏輯可能因大小寫處理不當而漏掉結果。建議先修正驗證流程與錯誤處理，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證後未正確檢查錯誤，可能提交無效資料 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:173` | 錯誤處理中 console.error 可能洩漏敏感資訊 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69` | 搜尋過濾邏輯可能因大小寫處理不當而漏掉結果 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋過濾與後端查詢重複，可能造成不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證後未正確檢查錯誤，可能提交無效資料</summary>

在 `onSave` 中，呼叫 `await validateForm({ schema: values })` 後，程式碼檢查 `errors.length > 0` 來決定是否中斷。但 `errors` 是來自 `useSchemaForm` 的 state，而 `validateForm` 可能是非同步更新 state，因此 `errors` 在 `await` 後可能尚未更新，導致即使驗證失敗仍繼續執行 `createBlockDocument`。

**失敗情境**：使用者輸入無效的 schema 資料（例如必填欄位留空），`validateForm` 回傳後 `errors` 仍為空陣列，於是呼叫 `createBlockDocument`，將無效資料送到後端。

**建議**：讓 `validateForm` 直接回傳驗證結果（例如 `boolean` 或錯誤陣列），並使用該回傳值判斷，而不是依賴 state。

**判斷依據**：diff 中新增的 `onSave` 函式，第 160-163 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:173</code> 錯誤處理中 console.error 可能洩漏敏感資訊</summary>

在 `onError` 回呼中，使用 `console.error(message, err)` 記錄錯誤。`err` 可能包含 API 回應的詳細資料，包括使用者輸入的資料或後端錯誤訊息，若這些資料包含敏感資訊（如密碼、token），則會洩漏到瀏覽器主控台。

**失敗情境**：建立區塊文件時，若後端因驗證失敗回傳包含使用者輸入的錯誤訊息，該訊息會被記錄到主控台，任何能開啟開發者工具的人都能看到。

**建議**：僅記錄錯誤的類型或一般訊息，避免輸出完整錯誤物件；或使用結構化日誌並確保敏感欄位被遮蔽。

**判斷依據**：diff 中 `onError` 回呼內，第 173 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69</code> 搜尋過濾邏輯可能因大小寫處理不當而漏掉結果</summary>

在 `filteredData` 的 `useMemo` 中，使用 `blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase())` 進行過濾。但 `deferredSearch` 可能包含特殊正規表示式字元，雖然 `includes` 是字串比對，不會有正規表示式問題，但若 `blockDocument.name` 為 `null` 或 `undefined`，`toLowerCase()` 會拋出錯誤。

**失敗情境**：當某個區塊文件的名稱是 `null`（例如匿名區塊），使用者輸入搜尋字串時，`blockDocument.name?.toLowerCase()` 會因為 `name` 為 `null` 而拋出 `TypeError`，導致元件崩潰。

**建議**：使用 `blockDocument.name?.toLowerCase() ?? ""` 或先檢查 `name` 是否存在。

**判斷依據**：diff 中 `filteredData` 的 `useMemo`，第 72 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋過濾與後端查詢重複，可能造成不一致</summary>

元件同時使用 `useSuspenseQuery` 的 `deferredSearch` 參數進行後端過濾，又在 `filteredData` 中進行前端過濾。這可能導致當後端過濾與前端過濾條件不同時，顯示的結果不一致。例如後端可能因為大小寫或模糊比對而回傳不同結果，前端又再過濾一次。

**失敗情境**：使用者輸入搜尋字串，後端回傳了符合的區塊文件，但前端過濾因為大小寫敏感而將某些結果排除，導致使用者看不到實際上符合的選項。

**建議**：統一過濾邏輯，要嘛完全依賴後端查詢，要嘛完全在前端過濾，避免雙重過濾造成混淆。

**判斷依據**：diff 中 `filteredData` 的 `useMemo`，第 70-74 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11333 (cache hit 11264) ｜ completion tokens 1446 ｜ PR #4</sub>