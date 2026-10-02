<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了文字輸入的硬編碼 48 字元限制，改為依賴後端提供的 max_length。整體方向合理，但存在幾個問題：1) 在 text-generation/index.tsx 中新增了 console.log，違反 R25；2) 在 prompt-value-panel/index.tsx 中將 number 輸入的 type 從 'number' 改為 'text'，可能導致非數字輸入；3) 在 text-generation/index.tsx 中，當 max_length 未定義時，比較邏輯可能失效；4) 在 utils/var.ts 中，解構賦值沒有實際作用。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:199` | [R25] 新增 console.log 違反前端禁止 console 語句規範 | 0.95 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | 將 number 輸入的 type 從 'number' 改為 'text' 可能導致非數字輸入 | 0.90 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | 當 max_length 未定義時，比較邏輯可能失效 | 0.85 |
| 🔸 | Minor | `web/utils/var.ts:33` | 解構賦值沒有實際作用 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> [R25] 新增 console.log 違反前端禁止 console 語句規範</summary>

在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，違反 R25 規範。應移除或改用適當的 logging 機制。

**判斷依據**：diff 中新增的 console.log 行，違反 R25。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> 將 number 輸入的 type 從 'number' 改為 'text' 可能導致非數字輸入</summary>

原本使用 `type="number"` 可限制輸入為數字，改為 `type="text"` 後，使用者可以輸入任意字元，可能導致後續處理錯誤。若目的是移除 maxLength 限制，應保留 type="number" 並移除 maxLength 屬性。

**判斷依據**：diff 中將 type="number" 改為 type="text"。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> 當 max_length 未定義時，比較邏輯可能失效</summary>

原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，移除後若 `varItem.max_length` 為 undefined，則 `item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 false，導致長度檢查失效。應保留預設值或明確處理 undefined 情況。

**判斷依據**：diff 中移除了 `|| DEFAULT_VALUE_MAX_LEN`，且未處理 undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/utils/var.ts:33</code> 解構賦值沒有實際作用</summary>

`const { ...rest } = VAR_ITEM_TEMPLATE_IN_WORKFLOW` 只是複製整個物件，與直接使用 `VAR_ITEM_TEMPLATE_IN_WORKFLOW` 無異。若目的是移除 max_length，應明確排除該屬性，例如 `const { max_length, ...rest } = VAR_ITEM_TEMPLATE_IN_WORKFLOW`。

**判斷依據**：diff 中將 `const { max_length: _maxLength, ...rest }` 改為 `const { ...rest }`，但未排除任何屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8315 (cache hit 5632) ｜ completion tokens 942 ｜ PR #5</sub>