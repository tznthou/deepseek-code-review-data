<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了文字輸入欄位的硬編碼 48 字元上限，改為依賴後端提供的 max_length 設定。主要風險在於當 max_length 未定義時，前端不再有預設限制，可能導致使用者輸入超長內容，進而影響後端處理或儲存。此外，`PromptValuePanel` 中將數字輸入的 type 從 'number' 改為 'text'，可能影響輸入驗證與使用者體驗。建議確認後端對未設定 max_length 的處理方式，並評估數字輸入變更的必要性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 當 max_length 未定義時，長度檢查可能失效 | 0.80 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | 數字輸入類型從 number 改為 text，可能影響輸入驗證 | 0.70 |
| 🔸 | Minor | `web/app/components/share/text-generation/index.tsx:199` | 殘留的 console.log 可能洩漏敏感資訊 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 當 max_length 未定義時，長度檢查可能失效</summary>

在 `varItem.max_length` 為 `undefined` 時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 `false`，因此不會觸發錯誤。這可能導致使用者提交超長文字，造成後端處理問題或資料截斷。建議在 max_length 未定義時，使用合理的預設值或明確跳過檢查。

**判斷依據**：diff 中移除了 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN`，改為直接使用 `varItem.max_length`，但未處理 undefined 的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> 數字輸入類型從 number 改為 text，可能影響輸入驗證</summary>

將 `<Input type="number">` 改為 `<Input type="text">`，可能導致使用者輸入非數字字元，且喪失瀏覽器原生的數字驗證與上下箭頭調整功能。若後端預期數字，可能造成型別錯誤。建議確認此變更的必要性，或改用其他方式限制輸入。

**判斷依據**：diff 中將 `type="number"` 改為 `type="text"`，且未見其他驗證邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> 殘留的 console.log 可能洩漏敏感資訊</summary>

新增的 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })` 會將批次輸入的資料輸出到主控台，可能包含使用者提供的敏感內容。建議移除或改用適當的日誌機制。

**判斷依據**：diff 中新增了此行，且未見移除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5636 (cache hit 5632) ｜ completion tokens 752 ｜ PR #5</sub>