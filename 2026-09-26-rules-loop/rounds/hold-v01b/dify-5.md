<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了文字輸入框的硬編碼 48 字元上限，改為依賴後端設定的 max_length。整體方向合理，但存在兩個必須修正的問題：一是新增了 console.log 除錯語句（違反 R25），二是 number 輸入框的 type 從 'number' 改為 'text'，可能破壞數值輸入的驗證與使用者體驗。此外，移除預設 max_length 後，若後端未提供該值，前端將不再限制輸入長度，需確認後端是否已保證提供。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/share/text-generation/index.tsx:199` | [R25] 新增 console.log 除錯語句 | 0.95 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入框 type 改為 text 可能破壞數值輸入 | 0.80 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 移除預設 max_length 後可能導致無限制輸入 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> [R25] 新增 console.log 除錯語句</summary>

在批次輸入驗證前新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將資料輸出到瀏覽器主控台，可能洩漏使用者輸入內容，且違反專案規範 R25（禁止 console 語句）。請移除該行。

**判斷依據**：diff 中新增的 console.log 語句，違反 R25。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入框 type 改為 text 可能破壞數值輸入</summary>

將 number 輸入框的 `type` 從 `"number"` 改為 `"text"`，這會失去瀏覽器原生的數值輸入行為（如 spinner、行動裝置數字鍵盤），且可能允許非數值字元輸入。若後端預期數值，可能導致提交錯誤。請確認此變更的必要性，或改用 `inputMode="numeric"` 等替代方案。

**判斷依據**：diff 中 `-                        type="number"` 改為 `+                        type="text"`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 移除預設 max_length 後可能導致無限制輸入</summary>

原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 作為長度上限，現在改為直接使用 `varItem.max_length`。若後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，因此不會觸發長度錯誤，等同於無限制。請確認後端是否保證提供 `max_length`，或在前端保留預設值作為 fallback。

**判斷依據**：diff 中 `-          if (item[varIndex].length > maxLen) {` 改為 `+          if (item[varIndex].length > varItem.max_length) {`，且 `maxLen` 原本有 fallback。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8315 (cache hit 8192) ｜ completion tokens 828 ｜ PR #5</sub>