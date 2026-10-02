<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了區塊文件（block document）的選取器與建立對話框，並整合進 schema form 以支援 blockTypeSlug 屬性。主要風險在於前端資料驗證不足、錯誤處理不完整，以及部分元件缺少測試。最應優先處理的是建立對話框中的表單驗證邏輯與錯誤處理，以及選取器在資料載入失敗時的行為。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161` | 表單驗證邏輯可能無法正確阻止提交 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179` | 建立失敗時僅顯示通用錯誤訊息，未提供具體原因 | 0.75 |
| ⚠️ | Major | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:50` | 資料載入失敗時無錯誤處理，可能導致元件無回應 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67` | 搜尋過濾邏輯可能與後端不一致 | 0.65 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73` | 選取的區塊文件可能不在目前過濾結果中 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/schemas/schema-form-input.tsx:79` | blockTypeSlug 非字串時未處理，可能導致錯誤 | 0.55 |
| 🔸 | Minor | `ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:117` | 缺少對 blockSchema 不存在的處理 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161</code> 表單驗證邏輯可能無法正確阻止提交</summary>

在 `onSave` 中，先呼叫 `await validateForm({ schema: values })`，然後檢查 `errors.length > 0`。但 `errors` 是從 `useSchemaForm` 取得的 state，而 `validateForm` 可能是非同步更新 state，因此 `errors` 可能尚未反映最新的驗證結果，導致即使驗證失敗仍繼續執行 `createBlockDocument`。

建議：讓 `validateForm` 直接回傳驗證結果（例如 boolean 或錯誤陣列），並根據回傳值決定是否繼續，而不是依賴非同步的 state 更新。

**判斷依據**：diff 中新增的 `onSave` 函式，第 151-154 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179</code> 建立失敗時僅顯示通用錯誤訊息，未提供具體原因</summary>

在 `createBlockDocument` 的 `onError` 回呼中，僅顯示固定的 'Unknown error while creating block.'，並將錯誤記錄到 console。使用者無法得知失敗原因（例如名稱重複、驗證失敗等）。

建議：從錯誤物件中提取可讀的錯誤訊息並顯示給使用者，或至少顯示後端回傳的錯誤細節。

**判斷依據**：diff 中新增的 `onError` 回呼，第 166-170 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:50</code> 資料載入失敗時無錯誤處理，可能導致元件無回應</summary>

使用 `useSuspenseQuery` 取得資料，但沒有提供錯誤邊界（Error Boundary）或錯誤狀態處理。若 API 請求失敗，Suspense 會拋出錯誤，若上層沒有錯誤邊界，整個應用程式可能崩潰。

建議：在 `BlockDocumentCombobox` 外層加入錯誤邊界，或在元件內處理錯誤狀態（例如顯示錯誤訊息）。

**判斷依據**：diff 中新增的 `useSuspenseQuery` 呼叫，第 66 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67</code> 搜尋過濾邏輯可能與後端不一致</summary>

元件同時使用後端查詢（`deferredSearch` 傳入 `like_`）和前端過濾（`filteredData` 使用 `toLowerCase().includes`）。這可能導致結果不一致，例如後端已過濾但前端又重複過濾，或大小寫處理不同。

建議：統一過濾邏輯，僅使用後端查詢或前端過濾，避免重複。

**判斷依據**：diff 中新增的 `filteredData` 計算，第 78-82 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73</code> 選取的區塊文件可能不在目前過濾結果中</summary>

`selectedBlockDocument` 是從 `filteredData` 中尋找，若使用者已選取某個區塊文件，但之後搜尋條件改變導致該文件不在 `filteredData` 中，則 `selectedBlockDocument` 會是 `undefined`，觸發器會顯示 'Select a block...'，但實際上仍有選取值。

建議：從完整的 `data` 中尋找選取的區塊文件，或確保選取的文件始終顯示。

**判斷依據**：diff 中新增的 `selectedBlockDocument` 計算，第 86-90 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/schemas/schema-form-input.tsx:79</code> blockTypeSlug 非字串時未處理，可能導致錯誤</summary>

程式碼檢查 `typeof blockTypeSlug === "string"`，若不是字串則不渲染任何內容，但沒有提供 fallback 或錯誤提示。這可能導致表單欄位消失，使用者無法輸入。

建議：若非字串，顯示錯誤訊息或使用預設行為。

**判斷依據**：diff 中新增的條件判斷，第 78-80 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:117</code> 缺少對 blockSchema 不存在的處理</summary>

若 `blockSchemas` 陣列為空，`blockSchema` 會是 `undefined`，程式碼有檢查並顯示 'No schema found for this block type.'，但沒有提供建立 schema 的選項或更詳細的指引。

建議：可考慮提供連結或按鈕讓使用者建立 schema。

**判斷依據**：diff 中新增的條件渲染，第 112-118 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12828 (cache hit 12800) ｜ completion tokens 1845 ｜ PR #4</sub>