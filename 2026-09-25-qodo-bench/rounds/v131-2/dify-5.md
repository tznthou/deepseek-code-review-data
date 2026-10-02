<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了文字輸入欄位的硬編碼 48 字元上限，改為依賴後端提供的 max_length。整體方向合理，但存在兩個主要問題：1) 在 text-generation/index.tsx 中新增了 console.log，可能洩漏批次輸入資料；2) 在 prompt-value-panel/index.tsx 中將 number 輸入的 type 從 'number' 改為 'text'，可能導致非數字輸入。此外，移除預設 max_length 後，若後端未提供該值，前端將無限制，需確認後端行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:199` | 新增 console.log 可能洩漏使用者輸入資料 | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入的 type 從 'number' 改為 'text' 可能允許非數字輸入 | 0.80 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 移除預設 max_length 後，若後端未提供 max_length 將無長度限制 | 0.80 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:200` | 移除 paragraph 類型的 max_length 設定可能導致無限制輸入 | 0.70 |
| 🔸 | Minor | `web/app/components/rag-pipeline/components/panel/input-field/editor/form/hooks.ts:89` | 移除 paragraph 類型的 maxLength 設定可能導致無限制輸入 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> 新增 console.log 可能洩漏使用者輸入資料</summary>

在批次輸入驗證前新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`。這會將使用者上傳的 CSV 標頭資料輸出到瀏覽器主控台，可能包含敏感資訊（如欄位名稱）。在生產環境中不應留下此類除錯日誌。建議移除該行。

**判斷依據**：diff 中新增的 console.log 行，位於 text-generation/index.tsx 的批次輸入處理函式中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入的 type 從 'number' 改為 'text' 可能允許非數字輸入</summary>

原本 `<Input type="number" ...>` 改為 `<Input type="text" ...>`。這會讓使用者可以輸入任意文字，而後端可能預期數字，導致提交時錯誤或資料不一致。若目的是移除 maxLength 限制，應保留 type="number" 並僅移除 maxLength 屬性。

**判斷依據**：diff 中 type 屬性的變更，位於 prompt-value-panel/index.tsx 的 number 輸入區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 移除預設 max_length 後，若後端未提供 max_length 將無長度限制</summary>

原本 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN` 確保有預設上限，現在改為 `if (item[varIndex].length > varItem.max_length)`。若 `varItem.max_length` 為 undefined，則比較結果永遠為 false，導致無長度驗證。需確認後端是否總是提供 max_length，否則應保留預設值或明確處理 undefined。

**判斷依據**：diff 中移除了 `|| DEFAULT_VALUE_MAX_LEN` 的邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:200</code> 移除 paragraph 類型的 max_length 設定可能導致無限制輸入</summary>

原本在型別變更為 paragraph 時會設定 `draft.max_length = DEFAULT_VALUE_MAX_LEN`，現在移除後，paragraph 輸入將沒有預設長度限制。若後端未提供 max_length，使用者可輸入任意長度，可能造成效能或儲存問題。建議確認後端行為或保留預設值。

**判斷依據**：diff 中刪除了設定 max_length 的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/rag-pipeline/components/panel/input-field/editor/form/hooks.ts:89</code> 移除 paragraph 類型的 maxLength 設定可能導致無限制輸入</summary>

原本在型別變更為 paragraph 時會呼叫 `setFieldValue('maxLength', DEFAULT_VALUE_MAX_LEN)`，現在移除後，paragraph 輸入將沒有預設長度限制。需確認後端是否提供 maxLength，否則應保留預設值。

**判斷依據**：diff 中刪除了設定 maxLength 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5600 (cache hit 5504) ｜ completion tokens 1181 ｜ PR #5</sub>