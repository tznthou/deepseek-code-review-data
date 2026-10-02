<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了區塊文件參考支援，包含 combobox、建立對話框及 schema form 整合。整體架構合理，但存在幾個需要修正的問題：最嚴重的是 `BlockDocumentCombobox` 中重複的客戶端過濾邏輯，可能導致選取的項目無法正確顯示；其次是 `BlockDocumentCreateDialog` 中驗證錯誤處理不完整，可能讓使用者誤以為建立成功；另外還有一些型別安全與可維護性的小問題。建議先修正重複過濾與驗證錯誤處理，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 重複的客戶端過濾導致選取項目可能無法顯示 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 驗證錯誤處理不完整，可能誤導使用者 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤處理中使用 `console.error` 可能洩漏敏感資訊 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:81` | 型別斷言可能隱藏錯誤 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 重複的客戶端過濾導致選取項目可能無法顯示</summary>

`useSuspenseQuery` 的查詢參數中已經包含了 `name: { like_: deferredSearch }` 的過濾條件，但又在 `filteredData` 中對 `data` 進行了一次 `toLowerCase().includes()` 的客戶端過濾。這會造成兩個問題：
1. 伺服器端過濾可能因為大小寫或部分匹配規則不同，導致某些符合條件的項目被客戶端過濾掉。
2. 當 `selectedBlockDocumentId` 對應的項目不在 `filteredData` 中時（例如使用者選取後清除搜尋字串，但資料尚未重新載入），`selectedBlockDocument` 會是 `undefined`，導致 combobox 顯示 placeholder 而非已選取的名稱。

建議移除客戶端過濾，直接使用 `data` 作為顯示清單，並依賴伺服器端過濾。

**判斷依據**：diff 中新增的 `filteredData` 邏輯與查詢參數中的 `name: { like_: deferredSearch }` 重複，且 `selectedBlockDocument` 是從 `filteredData` 中尋找，可能找不到已選取的項目。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 驗證錯誤處理不完整，可能誤導使用者</summary>

在 `onSave` 中，呼叫 `validateForm` 後檢查 `errors.length > 0` 就 `return`，但沒有顯示任何錯誤訊息給使用者。使用者可能填寫了無效的資料，按下送出後沒有任何反應，誤以為建立成功。

建議在 `errors.length > 0` 時顯示錯誤提示（例如 toast 或表單內錯誤），或將驗證錯誤整合到表單的錯誤顯示中。

**判斷依據**：diff 中新增的 `onSave` 函式，在驗證失敗時僅 `return`，沒有使用者可見的錯誤回饋。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤處理中使用 `console.error` 可能洩漏敏感資訊</summary>

在 `onError` 和 `catch` 區塊中，使用 `console.error` 記錄錯誤物件。如果錯誤物件包含敏感資訊（例如 API 回應中的詳細資料），可能會在瀏覽器主控台中暴露。建議使用結構化記錄或僅記錄錯誤訊息，避免輸出完整物件。

**判斷依據**：diff 中新增的錯誤處理程式碼，直接將 `err` 傳給 `console.error`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:81</code> 型別斷言可能隱藏錯誤</summary>

在處理 `blockTypeSlug` 時，使用 `value as { $ref: string } | undefined` 進行型別斷言。如果 `value` 的實際型別不是預期的形狀，可能會在執行時期造成問題。建議使用型別守衛或更精確的型別檢查。

**判斷依據**：diff 中新增的型別斷言，沒有驗證 `value` 的實際結構。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12633 (cache hit 2176) ｜ completion tokens 1285 ｜ PR #4</sub>