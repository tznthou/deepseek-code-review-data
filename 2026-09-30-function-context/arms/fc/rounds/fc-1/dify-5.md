<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了文字輸入欄位的硬編碼 48 字元上限（DEFAULT_VALUE_MAX_LEN），改為依賴後端提供的 max_length 或完全不加限制。主要風險在於：1) 批次輸入驗證（checkBatchInputs）在 max_length 未定義時可能因比較 undefined 而失效，導致超長輸入被接受；2) 在 share/text-generation 中新增了 console.log，可能洩漏使用者批次資料；3) 將 number 輸入的 type 從 number 改為 text，可能影響使用者體驗與資料型別。整體而言，移除硬編碼限制的方向合理，但需確保後端一定有提供 max_length，否則可能造成無限制輸入。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 批次輸入驗證在 max_length 未定義時可能失效 | 0.90 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:199` | 新增 console.log 可能洩漏使用者批次資料 | 0.85 |
| 🔸 | Minor | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入的 type 從 number 改為 text 可能影響使用者體驗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 批次輸入驗證在 max_length 未定義時可能失效</summary>

在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 來取得長度上限，現在改為直接使用 `varItem.max_length`。如果後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，導致超長輸入不會被擋下。

**失敗情境**：使用者上傳的 CSV 中某欄位超過後端允許的長度，但該變數的 `max_length` 未定義，驗證會通過，可能造成後續 API 錯誤或資料截斷。

**建議**：確認後端一定提供 `max_length`，或在此處加入 fallback（例如 `varItem.max_length ?? DEFAULT_VALUE_MAX_LEN`，但需保留常數）。

**判斷依據**：diff 中刪除了 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN`，並將條件改為 `item[varIndex].length > varItem.max_length`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> 新增 console.log 可能洩漏使用者批次資料</summary>

在 `checkBatchInputs` 函式開頭新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`。這會將使用者上傳的批次資料（包含標頭）輸出到瀏覽器主控台，可能包含敏感資訊（如使用者輸入的變數名稱或內容）。

**失敗情境**：使用者在公用電腦上操作，或使用開發者工具時，可能無意中暴露資料。

**建議**：移除這行 `console.log`，或改用適當的 logging 機制（如 debug level 且不輸出資料內容）。

**判斷依據**：diff 中新增了這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入的 type 從 number 改為 text 可能影響使用者體驗</summary>

在 `PromptValuePanel` 中，原本 number 類型的輸入使用 `<Input type="number">`，現在改為 `<Input type="text">`。這會失去瀏覽器原生的數字輸入行為（如上下箭頭、輸入驗證），且可能導致使用者輸入非數字字元。

**失敗情境**：使用者在數字欄位輸入字母，後續處理可能出錯。

**建議**：確認此變更是否為預期。若需保留數字輸入，應維持 `type="number"` 並加上適當驗證。

**判斷依據**：diff 中將 `type="number"` 改為 `type="text"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23760 (cache hit 1536) ｜ completion tokens 1019 ｜ PR #5</sub>