<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了區塊文件參考（block document reference）的支援，包含 combobox 元件、建立對話框，以及整合到 schema form 中。整體架構合理，但存在一些正確性與使用者體驗問題：搜尋邏輯重複、錯誤處理不完整、缺少載入狀態、以及可能的效能問題。最需要先修的是 `block-document-combobox.tsx` 中的重複過濾邏輯，以及 `block-document-create-dialog.tsx` 中錯誤處理與表單驗證的缺陷。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 重複的搜尋過濾邏輯可能導致不一致 | 0.90 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73` | 選取的區塊文件可能不在過濾後的列表中 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證錯誤處理不完整 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立區塊文件時缺少錯誤處理 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:30` | 缺少載入狀態顯示 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:229` | 表單送出按鈕缺少 disabled 狀態 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | blockTypeSlug 非字串時未處理 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input-block-document.tsx:36` | onValueChange 型別轉換不安全 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 重複的搜尋過濾邏輯可能導致不一致</summary>

`useSuspenseQuery` 的查詢參數中已經使用 `deferredSearch` 進行伺服器端過濾（`name: { like_: deferredSearch }`），但又在 `filteredData` 中對 `data` 進行客戶端過濾。這會造成：
1. 不必要的客戶端計算。
2. 如果伺服器端過濾與客戶端過濾的規則不一致（例如大小寫處理），可能導致結果不同。
建議移除客戶端過濾，完全依賴伺服器端過濾，或反之。

**判斷依據**：diff 中第 62-66 行顯示客戶端過濾，而第 48-55 行顯示查詢參數中已包含 `deferredSearch` 的 `like_` 條件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73</code> 選取的區塊文件可能不在過濾後的列表中</summary>

`selectedBlockDocument` 是從 `filteredData` 中尋找，如果使用者已選取某個區塊文件，但之後搜尋條件改變，導致該文件不在 `filteredData` 中，則 `selectedBlockDocument` 會是 `undefined`，觸發器會顯示「Select a block...」而非已選取的名稱。這會造成使用者困惑。建議從原始 `data` 中尋找選取的項目，或確保選取的項目永遠包含在列表中。

**判斷依據**：diff 中第 68-72 行顯示從 `filteredData` 中尋找，而 `filteredData` 會因搜尋而改變。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證錯誤處理不完整</summary>

在 `onSave` 中，呼叫 `validateForm` 後檢查 `errors.length > 0`，但 `errors` 是從 `useSchemaForm` 取得的狀態，可能不是最新的。此外，`validateForm` 是非同步的，但沒有等待其完成就檢查 `errors`，可能導致錯誤未顯示。建議使用 `await validateForm` 的回傳值或確保 `errors` 在驗證後更新。

**判斷依據**：diff 中第 158-161 行顯示驗證後立即檢查 `errors`，但 `errors` 可能尚未更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立區塊文件時缺少錯誤處理</summary>

`createBlockDocument` 的 `onError` 回呼中只顯示通用錯誤訊息並記錄錯誤，但沒有提供具體的錯誤細節給使用者。此外，沒有處理網路錯誤或伺服器回傳的驗證錯誤。建議顯示伺服器回傳的錯誤訊息，並在 UI 中呈現。

**判斷依據**：diff 中第 163-167 行顯示錯誤處理只顯示通用訊息。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:30</code> 缺少載入狀態顯示</summary>

使用 `useSuspenseQuery` 會暫停元件直到資料載入完成，但沒有提供 fallback UI。在 `Suspense` 邊界中沒有指定 fallback，因此載入期間會顯示空白或上一個 Suspense 的 fallback。建議提供明確的載入指示器。

**判斷依據**：diff 中第 29-31 行顯示 `<Suspense>` 沒有 `fallback` prop。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:229</code> 表單送出按鈕缺少 disabled 狀態</summary>

在表單送出期間，`isPending` 用於顯示載入狀態，但按鈕沒有 `disabled` 屬性，使用者可能重複點擊。建議加上 `disabled={isPending}`。

**判斷依據**：diff 中第 174-176 行顯示按鈕沒有 `disabled`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> blockTypeSlug 非字串時未處理</summary>

在 `if ("blockTypeSlug" in property)` 區塊中，如果 `blockTypeSlug` 存在但不是字串（例如是陣列或其他型別），則不會渲染任何內容，且沒有錯誤提示。建議加入 else 分支或拋出錯誤。

**判斷依據**：diff 中第 78-80 行顯示只有當 `blockTypeSlug` 是字串時才渲染，否則沒有處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input-block-document.tsx:36</code> onValueChange 型別轉換不安全</summary>

`handleSelect` 中，如果 `blockDocumentId` 是空字串或 falsy，會呼叫 `onValueChange(undefined)`，但 `onValueChange` 的參數型別是 `BlockDocumentReferenceValue`，包含 `undefined`，這是可以的。但 `handleCreated` 中直接傳入 `{ $ref: blockDocumentId }`，沒有檢查 `blockDocumentId` 是否有效。建議加入驗證。

**判斷依據**：diff 中第 31-33 行顯示直接使用 `blockDocumentId`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11297 (cache hit 11264) ｜ completion tokens 2103 ｜ PR #4</sub>