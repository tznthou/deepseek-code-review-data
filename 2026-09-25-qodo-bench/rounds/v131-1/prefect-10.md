<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為多種觸發器模板新增了實際的表單欄位元件，取代原本的「coming soon」佔位文字，並更新了對應的測試。整體結構與現有 FlowRunStateTriggerFields 一致，但存在幾個需要修正的問題：最嚴重的是關閉了 TypeScript 的 strict 模式，這會大幅降低型別安全；另外在數字輸入的處理上，不同元件間不一致（Number vs parseInt），且未處理 NaN 的情況，可能導致表單資料錯誤。建議先恢復 strict 模式並修正型別問題，再統一數字輸入的處理方式。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/tsconfig.app.json:19` | 關閉 strict 模式會大幅降低型別安全 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | 使用 parseInt 而非 Number 處理數字輸入，且未處理 NaN | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38` | Expected Events 欄位在空輸入時可能設定為 undefined，但型別可能不符 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30` | 動態切換欄位名稱可能導致資料殘留或驗證問題 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | Threshold 輸入未處理 NaN 或小於 1 的值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/tsconfig.app.json:19</code> 關閉 strict 模式會大幅降低型別安全</summary>

將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查選項（包括 `noImplicitAny`、`strictNullChecks` 等），可能隱藏潛在的型別錯誤，導致執行時期錯誤。這通常不是解決型別錯誤的正確方式，應修正具體的型別問題，而不是全域關閉嚴格模式。

**判斷依據**：diff 中 tsconfig.app.json 的變更：`- "strict": true,` 改為 `+ "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> 使用 parseInt 而非 Number 處理數字輸入，且未處理 NaN</summary>

在 Threshold 欄位的 onChange 中使用 `parseInt(e.target.value)`，而其他元件使用 `Number(e.target.value)`。`parseInt` 會解析開頭的數字並忽略後續非數字字元（例如輸入 "10abc" 會得到 10），可能導致非預期的值。此外，若輸入為空字串，`parseInt('')` 會得到 `NaN`，而 `Number('')` 會得到 0。建議統一使用 `Number` 並處理 `NaN` 的情況（例如設為 undefined 或顯示驗證錯誤）。

**判斷依據**：diff 中 work-pool-status-trigger-fields.tsx 第 88 行：`onChange={(e) => field.onChange(parseInt(e.target.value))}`，而其他元件使用 `Number(e.target.value)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38</code> Expected Events 欄位在空輸入時可能設定為 undefined，但型別可能不符</summary>

在 Expected Events 的 Textarea onChange 中，若輸入為空字串，`lines` 會是 `['']`，長度為 1，因此 `field.onChange(lines)` 會設定為 `['']`，而不是 `undefined`。這可能導致表單資料包含空字串陣列，與預期的 `string[] | undefined` 型別不符。建議明確處理空輸入的情況，例如 `field.onChange(lines.filter(Boolean).length > 0 ? lines.filter(Boolean) : undefined)`。

**判斷依據**：diff 中 custom-trigger-fields.tsx 第 41-42 行：`const lines = e.target.value.split("\n");` 和 `field.onChange(lines.length > 0 ? lines : undefined);`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30</code> 動態切換欄位名稱可能導致資料殘留或驗證問題</summary>

根據 posture 動態決定使用 `trigger.after` 或 `trigger.expect` 欄位。當 posture 從 Reactive 切換到 Proactive 時，原本在 `trigger.expect` 的值不會自動轉移到 `trigger.after`，可能導致資料不一致。此外，若兩個欄位都有值，切換時可能造成混淆。建議在切換 posture 時清除或轉移相關欄位的值，或使用固定的欄位名稱並在提交時轉換。

**判斷依據**：diff 中 deployment-status-trigger-fields.tsx 第 34-35 行：`const statusFieldName = posture === "Proactive" ? "trigger.after" : "trigger.expect";`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> Threshold 輸入未處理 NaN 或小於 1 的值</summary>

Threshold 欄位設定 `min={1}`，但使用者仍可手動輸入 0 或負數，且 `onChange` 直接將值存入表單，沒有驗證。若輸入無效值（如空字串），`Number('')` 會得到 0，可能導致後端驗證錯誤。建議在 onChange 中檢查數值範圍，或依賴表單驗證機制（如 zod schema）來處理。

**判斷依據**：diff 中 work-pool-status-trigger-fields.tsx 第 88 行：`onChange={(e) => field.onChange(parseInt(e.target.value))}`，且 Input 有 `min={1}` 屬性

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7573 (cache hit 1408) ｜ completion tokens 1528 ｜ PR #10</sub>