<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選擇器與建立對話框，並整合到 schema form 中。主要風險在於建立對話框的錯誤處理不完整、表單驗證邏輯有缺陷，以及部分程式碼違反了專案的 TypeScript 縮排規範。建議先修正錯誤處理與驗證流程，再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤處理不完整：onError 未提供使用者回饋 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證邏輯錯誤：validateForm 後未正確處理 errors | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | [R09] 縮排不一致：使用空格而非 tab | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69` | 潛在的 null 錯誤：blockDocument.name 可能為 undefined | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋邏輯重複：後端已過濾，前端再次過濾 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 錯誤訊息未使用 API 回傳的詳細資訊 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤處理不完整：onError 未提供使用者回饋</summary>

在 `createBlockDocument` 的 `onError` 回呼中，僅顯示固定的錯誤訊息 'Unknown error while creating block.'，未使用 API 回傳的錯誤細節。這會讓使用者無法得知失敗原因（例如名稱重複、驗證失敗等），降低可用性。建議從 `err` 參數中提取具體錯誤訊息並顯示。

**判斷依據**：diff 中新增的 `onError` 回呼（第 175-179 行）忽略了 `err` 的內容，僅顯示固定訊息。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證邏輯錯誤：validateForm 後未正確處理 errors</summary>

在 `onSave` 中，呼叫 `await validateForm({ schema: values })` 後，檢查 `errors.length > 0` 來決定是否繼續。但 `errors` 是從 `useSchemaForm` 取得的狀態，可能不會在 `await` 後立即更新，導致驗證失敗時仍繼續建立文件。建議讓 `validateForm` 直接回傳驗證結果，或使用其回傳值來判斷。

**判斷依據**：diff 中第 168-171 行，`validateForm` 被呼叫後，`errors` 可能尚未更新，造成邏輯錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> [R09] 縮排不一致：使用空格而非 tab</summary>

此處的縮排使用了兩個空格，而專案規範要求使用 tab（R09）。這會導致 Biome 檢查失敗。請將縮排改為 tab。

**判斷依據**：diff 中第 63-68 行，縮排為兩個空格，違反 R09。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69</code> 潛在的 null 錯誤：blockDocument.name 可能為 undefined</summary>

在 `filteredData` 的過濾邏輯中，直接呼叫 `blockDocument.name?.toLowerCase()`，但 `name` 可能為 `undefined`（根據 API 型別）。雖然使用了 optional chaining，但若 `name` 為 `undefined`，`includes` 會收到 `undefined`，可能導致非預期結果。建議先檢查 `name` 是否存在。

**判斷依據**：diff 中第 65 行，`blockDocument.name` 可能為 undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋邏輯重複：後端已過濾，前端再次過濾</summary>

查詢參數中已包含 `name: { like_: deferredSearch }`，但前端又使用 `filteredData` 進行一次 `includes` 過濾。這可能導致結果不一致（例如後端使用 LIKE 語法，前端使用簡單包含），且增加不必要的計算。建議移除前端過濾，直接使用 `data`。

**判斷依據**：diff 中第 63-68 行，與查詢參數中的 `name: { like_: deferredSearch }` 重複。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 錯誤訊息未使用 API 回傳的詳細資訊</summary>

`onError` 回呼中忽略了 `err` 參數，僅顯示固定訊息。這可能導致使用者無法得知具體錯誤（例如名稱已存在）。建議從 `err` 中提取訊息並顯示。

**判斷依據**：diff 中第 175-179 行，`err` 未被使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12818 (cache hit 11264) ｜ completion tokens 1567 ｜ PR #4</sub>