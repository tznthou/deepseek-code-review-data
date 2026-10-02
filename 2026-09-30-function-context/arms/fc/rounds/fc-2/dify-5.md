<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了文字輸入欄位的硬編碼 48 字元上限（DEFAULT_VALUE_MAX_LEN），改為依賴後端提供的 max_length 或完全不加限制。主要風險在於：若後端未提供 max_length，前端將不再有任何長度限制，可能導致使用者輸入超長內容，造成 API 錯誤或效能問題。此外，在 share/text-generation/index.tsx 中新增了一行 console.log，應移除。另有將 number 輸入類型改為 text 的變更，可能影響輸入驗證。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入類型改為 text 可能導致非數字輸入 | 0.80 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:120` | 移除 paragraph 類型的 max_length 設定可能導致無限制輸入 | 0.75 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/index.tsx:60` | 移除 textInput 的 max_length 預設值可能導致無限制輸入 | 0.75 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 批次輸入驗證中 max_length 可能為 undefined 導致比較錯誤 | 0.70 |
| 🔸 | Minor | `web/app/components/share/text-generation/index.tsx:199` | 移除除錯用的 console.log | 0.95 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入類型改為 text 可能導致非數字輸入</summary>

原本 number 類型的輸入使用 `<Input type="number">`，此 PR 將其改為 `<Input type="text">`。這會讓使用者可以輸入任意文字，而後續處理可能預期是數字，導致錯誤或非預期行為。若目的是移除 maxLength 限制，應保留 type="number" 並僅移除 maxLength 屬性。

**判斷依據**：diff 中將 type="number" 改為 type="text"

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:120</code> 移除 paragraph 類型的 max_length 設定可能導致無限制輸入</summary>

原本在 handleTypeChange 中，當類型切換為 paragraph 時會設定 `draft.max_length = DEFAULT_VALUE_MAX_LEN`，此 PR 移除了該設定。這表示 paragraph 類型的變數將不再有預設的 max_length，除非使用者手動設定。若後端未提供 max_length，前端將不會限制輸入長度，可能導致超長內容造成 API 錯誤或效能問題。

**判斷依據**：diff 中刪除了該段落

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/index.tsx:60</code> 移除 textInput 的 max_length 預設值可能導致無限制輸入</summary>

原本在 buildPromptVariableFromInput 中，若 payload.type 為 textInput 且未設定 max_length，會自動填入 DEFAULT_VALUE_MAX_LEN。此 PR 移除了該邏輯，因此若使用者未設定 max_length，該變數將沒有長度限制。這可能導致後端接收到超長輸入而發生錯誤。

**判斷依據**：diff 中刪除了該段落

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 批次輸入驗證中 max_length 可能為 undefined 導致比較錯誤</summary>

在 checkBatchInputs 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 來取得最大長度，現在改為直接使用 `varItem.max_length`。若後端未提供 max_length，則 `varItem.max_length` 為 undefined，與 `item[varIndex].length` 比較時會得到 false，導致驗證失效。建議保留 fallback 或明確處理 undefined 的情況。

**判斷依據**：diff 中將 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN` 改為直接使用 `varItem.max_length`

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> 移除除錯用的 console.log</summary>

在 checkBatchInputs 函式中新增了一行 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這應該是開發時留下的除錯程式碼，不應出現在正式程式碼中。建議移除。

**判斷依據**：diff 中新增的該行 console.log

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23760 (cache hit 23680) ｜ completion tokens 1137 ｜ PR #5</sub>