<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為多種觸發器模板新增了具體的表單欄位，取代原本的「coming soon」佔位文字。整體結構與現有 FlowRunStateTriggerFields 一致，但存在幾個值得注意的問題：關閉 TypeScript 嚴格模式會降低型別安全；部分欄位使用 parseInt 而非 Number 可能導致非預期行為；表單欄位在切換模板時可能殘留舊值；且缺少對新元件的測試覆蓋。建議優先修復嚴格模式與欄位殘留問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/tsconfig.app.json:19` | 關閉 TypeScript 嚴格模式降低型別安全 | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | 使用 parseInt 而非 Number 可能導致非預期結果 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30` | 切換模板時可能殘留舊的 trigger 欄位值 | 0.65 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:39` | Expected Events 欄位在空輸入時可能提交 undefined | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/trigger-step.test.tsx:45` | 測試僅檢查元件可見性，未驗證互動行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/tsconfig.app.json:19</code> 關閉 TypeScript 嚴格模式降低型別安全</summary>

將 `strict` 從 `true` 改為 `false` 會停用多項重要的型別檢查（如 `strictNullChecks`、`strictFunctionTypes` 等），可能導致未處理的 null/undefined 錯誤在編譯期無法被發現。此變更似乎與新增 UI 元件無直接關聯，若無充分理由，建議恢復為 `true`。

**判斷依據**：diff 中 tsconfig.app.json 的變更：`- "strict": true,` 改為 `+ "strict": false,`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> 使用 parseInt 而非 Number 可能導致非預期結果</summary>

在 threshold 欄位的 onChange 中使用 `parseInt(e.target.value)`，若輸入為空字串或非數字字串（如 "abc"），`parseInt` 會回傳 `NaN`，而 `Number` 會回傳 `NaN` 或 0。但 `parseInt` 會解析前綴數字（如 "10abc" 回傳 10），可能造成非預期行為。建議與其他元件一致使用 `Number(e.target.value)`，並考慮處理 NaN 的情況。

**判斷依據**：work-pool-status-trigger-fields.tsx 第 76 行，其他元件（如 custom-trigger-fields.tsx）使用 `Number(e.target.value)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30</code> 切換模板時可能殘留舊的 trigger 欄位值</summary>

當使用者從一個模板切換到另一個模板時，例如從 deployment-status 切換到 work-pool-status，`trigger.expect` 或 `trigger.after` 的值可能不會被重置，導致表單提交時包含不屬於當前模板的欄位。建議在模板變更時清除相關欄位，或確保 schema 驗證能忽略不相關的欄位。

**判斷依據**：deployment-status-trigger-fields.tsx 第 31-32 行，根據 posture 動態決定欄位名稱，但未清除另一個欄位的值

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:39</code> Expected Events 欄位在空輸入時可能提交 undefined</summary>

當使用者清空 Expected Events 文字框時，`onChange` 會將 `field.onChange(undefined)` 傳入，這可能導致表單值變成 `undefined`，而 schema 可能預期為陣列。建議改為傳入空陣列 `[]` 或確保 schema 能處理 `undefined`。

**判斷依據**：custom-trigger-fields.tsx 第 33 行，當 lines 為空時傳入 undefined

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/trigger-step.test.tsx:45</code> 測試僅檢查元件可見性，未驗證互動行為</summary>

新增的測試僅確認元件渲染（如 `getByLabelText`），未測試使用者互動（如選擇狀態、輸入數值）後表單值的正確性。建議增加測試覆蓋這些互動，以確保功能正常。

**判斷依據**：trigger-step.test.tsx 中多個測試僅檢查可見性，未模擬使用者操作

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7573 (cache hit 7552) ｜ completion tokens 1289 ｜ PR #10</sub>