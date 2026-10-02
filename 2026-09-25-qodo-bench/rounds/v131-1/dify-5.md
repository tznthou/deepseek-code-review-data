<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了文字輸入欄位的硬編碼 48 字元上限，改為完全依賴後端提供的 max_length。整體方向合理，但存在幾個風險：1) 在 text-generation 的批次驗證中，若 max_length 未定義，比較會變成 `length > undefined`，永遠為 false，導致驗證失效；2) 新增的 console.log 可能洩漏使用者輸入資料；3) 將 number 輸入的 type 改為 text 可能影響使用者體驗與資料驗證。建議優先修正批次驗證的邏輯與移除 console.log。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | max_length 未定義時批次驗證失效 | 0.90 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:199` | console.log 可能洩漏使用者輸入資料 | 0.85 |
| 🔸 | Minor | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入類型改為 text 可能影響使用者體驗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> max_length 未定義時批次驗證失效</summary>

在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 確保有預設值，現在改為直接使用 `varItem.max_length`。若 `max_length` 未定義（例如舊資料或未設定），`item[varIndex].length > undefined` 的結果永遠是 `false`，導致長度驗證完全失效，使用者可以提交任意長度的輸入。

建議：在比較前先檢查 `varItem.max_length` 是否存在，若不存在則跳過驗證或使用其他預設值。

**判斷依據**：diff 中刪除了 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN`，並將條件改為 `item[varIndex].length > varItem.max_length`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> console.log 可能洩漏使用者輸入資料</summary>

新增的 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })` 會將批次輸入的標頭資料輸出到瀏覽器主控台。`headerData` 可能包含使用者上傳的 CSV 內容，若其中含有敏感資訊（如個人資料），將造成資料外洩風險。

建議：移除此 console.log，或改用不記錄資料內容的除錯方式。

**判斷依據**：diff 中新增了此行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入類型改為 text 可能影響使用者體驗</summary>

將 number 輸入的 `type` 從 `"number"` 改為 `"text"`，這會失去瀏覽器原生的數字輸入行為（如上下箭頭、數字鍵盤、自動驗證）。若此變更非刻意為之，建議保留 `type="number"`；若為了移除 maxLength 限制，可考慮其他方式。

**判斷依據**：diff 中將 `type="number"` 改為 `type="text"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5600 (cache hit 1408) ｜ completion tokens 820 ｜ PR #5</sub>