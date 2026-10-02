<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為多種自動化觸發器模板新增了實際的表單欄位元件，取代原本的「coming soon」佔位文字，並更新了對應的測試。整體結構與現有 flow-run-state 元件一致，但存在幾個值得注意的問題：`tsconfig.app.json` 將 `strict` 從 `true` 改為 `false`，大幅降低型別安全，可能掩蓋潛在錯誤；`custom-trigger-fields.tsx` 中 `Expected Events` 的處理邏輯可能導致空陣列被轉換為 `undefined`，造成非預期的表單狀態；`work-pool-status-trigger-fields.tsx` 的 `Threshold` 欄位使用 `parseInt` 而非 `Number`，可能導致輸入小數或非數字字串時行為不一致。建議優先恢復 `strict` 設定，並統一數值輸入的處理方式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/tsconfig.app.json:19` | 關閉 TypeScript strict 模式將大幅降低型別安全 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38` | Expected Events 欄位可能將空陣列轉換為 undefined | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | Threshold 欄位使用 parseInt 而非 Number，可能導致非預期結果 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30` | Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/tsconfig.app.json:19</code> 關閉 TypeScript strict 模式將大幅降低型別安全</summary>

將 `strict` 從 `true` 改為 `false` 會停用多項關鍵的型別檢查（如 `strictNullChecks`、`strictFunctionTypes` 等），可能導致未處理的 `null`/`undefined` 錯誤在編譯期無法被發現，增加 runtime 錯誤風險。此變更與 PR 的主要功能無關，且會影響整個專案的型別安全。建議恢復為 `true`，若有必要可針對特定檔案使用 `// @ts-ignore` 或調整型別定義，而非全域關閉。

**判斷依據**：diff 中 `tsconfig.app.json` 的變更：`- "strict": true,` → `+ "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38</code> Expected Events 欄位可能將空陣列轉換為 undefined</summary>

在 `onChange` 中，當使用者清空 textarea 時，`e.target.value.split("\n")` 會得到 `[""]`，`lines.length > 0` 為 true，因此 `field.onChange([""])` 會將值設為包含一個空字串的陣列，而非預期的 `undefined` 或空陣列。這可能導致表單驗證或後續處理出現非預期行為。建議改為：`const lines = e.target.value.split("\n").filter(line => line.trim() !== ""); field.onChange(lines.length > 0 ? lines : undefined);`

**判斷依據**：diff 中 `custom-trigger-fields.tsx` 第 34-35 行：`const lines = e.target.value.split("\n");` 和 `field.onChange(lines.length > 0 ? lines : undefined);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> Threshold 欄位使用 parseInt 而非 Number，可能導致非預期結果</summary>

`parseInt(e.target.value)` 會將輸入轉為整數，若使用者輸入小數（如 1.5）會被截斷為 1，且若輸入為空字串或非數字字串，`parseInt` 會回傳 `NaN`，可能導致表單驗證失敗或提交錯誤資料。其他元件（如 `custom-trigger-fields.tsx`）使用 `Number(e.target.value)`，行為較一致且能正確處理小數。建議改為 `Number(e.target.value)`。

**判斷依據**：diff 中 `work-pool-status-trigger-fields.tsx` 第 82 行：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30</code> Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證</summary>

當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

**判斷依據**：diff 中 `deployment-status-trigger-fields.tsx` 第 39-40 行：`const statusFieldName = posture === "Proactive" ? "trigger.after" : "trigger.expect";`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7609 (cache hit 1536) ｜ completion tokens 1385 ｜ PR #10</sub>