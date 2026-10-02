<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了文字輸入的硬編碼 48 字元上限，改為依賴後端提供的 max_length。整體方向合理，但存在幾個問題：1) 在 text-generation/index.tsx 中新增了 console.log，可能洩漏批次輸入資料；2) 在 prompt-value-panel/index.tsx 中將 number 輸入的 type 從 'number' 改為 'text'，可能破壞數字驗證；3) 在 text-generation/index.tsx 中，當 max_length 未定義時，比較 item[varIndex].length > undefined 會得到 false，導致不再檢查長度，可能允許超長輸入。建議先移除 console.log 並修正數字輸入的型別。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:199` | 新增的 console.log 可能洩漏批次輸入資料 | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | 數字輸入的 type 從 'number' 改為 'text' 可能破壞數字驗證 | 0.85 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 當 max_length 未定義時，長度檢查失效 | 0.80 |
| 🔸 | Minor | `web/app/components/share/text-generation/run-once/index.tsx:142` | maxLength 屬性可能傳入 undefined | 0.70 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:197` | 移除 paragraph 類型的 max_length 設定可能導致未定義 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> 新增的 console.log 可能洩漏批次輸入資料</summary>

在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將使用者上傳的批次輸入資料（至少包含標頭列）輸出到瀏覽器主控台。如果資料包含敏感資訊（例如個人資料），可能造成隱私外洩。建議移除這行 console.log，或改用適當的日誌機制（如 debug 級別且不輸出資料內容）。

**判斷依據**：diff 中新增的這一行，位於 text-generation/index.tsx 的 checkBatchInput 函式內。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> 數字輸入的 type 從 'number' 改為 'text' 可能破壞數字驗證</summary>

原本 `<Input type="number" ...>` 改為 `<Input type="text" ...>`，這會讓瀏覽器不再限制輸入為數字，使用者可以輸入任意文字。如果後端預期收到數字，可能導致型別錯誤或驗證失敗。建議保留 `type="number"`，或明確說明為何需要改為文字輸入（例如為了自訂格式），並確保有適當的驗證。

**判斷依據**：diff 中將 `type="number"` 改為 `type="text"` 的這一行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 當 max_length 未定義時，長度檢查失效</summary>

原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在改為直接使用 `varItem.max_length`。如果 `varItem.max_length` 是 `undefined`，則 `item[varIndex].length > undefined` 會是 `false`（因為 `undefined` 會被轉成 `NaN`，任何比較都為 false），導致長度檢查永遠不會觸發，可能允許超長輸入。建議保留預設值，或明確處理 `max_length` 未定義的情況（例如視為無限制）。

**判斷依據**：diff 中將 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN` 和 `if (item[varIndex].length > maxLen)` 改為直接使用 `varItem.max_length` 的這幾行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/share/text-generation/run-once/index.tsx:142</code> maxLength 屬性可能傳入 undefined</summary>

原本 `maxLength={item.max_length || DEFAULT_VALUE_MAX_LEN}` 確保有預設值，現在改為 `maxLength={item.max_length}`。如果 `item.max_length` 是 `undefined`，React 會將該屬性設為 `undefined`，瀏覽器會忽略它，因此不會限制輸入長度。這可能是有意為之（移除限制），但需確認是否符合預期。

**判斷依據**：diff 中將 `maxLength={item.max_length || DEFAULT_VALUE_MAX_LEN}` 改為 `maxLength={item.max_length}` 的這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:197</code> 移除 paragraph 類型的 max_length 設定可能導致未定義</summary>

原本在型別變更為 paragraph 時會設定 `draft.max_length = DEFAULT_VALUE_MAX_LEN`，現在移除了這個設定。如果後續程式碼依賴 `max_length` 有值，可能會遇到 `undefined`。建議確認所有使用 `max_length` 的地方都能正確處理 `undefined`。

**判斷依據**：diff 中刪除了 `if (type === InputVarType.paragraph) draft.max_length = DEFAULT_VALUE_MAX_LEN` 的這幾行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5636 (cache hit 5632) ｜ completion tokens 1348 ｜ PR #5</sub>