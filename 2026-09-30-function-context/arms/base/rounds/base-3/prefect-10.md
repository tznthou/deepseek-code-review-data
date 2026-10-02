<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為多種觸發器模板新增了實際的表單欄位元件，取代原本的「coming soon」佔位文字，並更新了對應的測試。整體結構與現有 FlowRunStateTriggerFields 一致，但存在幾個值得注意的問題：最嚴重的是將 tsconfig 的 strict 模式關閉，這會降低型別安全；另外在數字輸入處理上，部分元件使用 parseInt 而非 Number，可能導致 NaN 或非預期的值；最後，測試僅驗證欄位可見性，未涵蓋互動行為。建議先恢復 strict 模式並修正數字輸入處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/tsconfig.app.json:19` | 關閉 strict 模式將大幅降低型別安全 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | 使用 parseInt 可能導致 NaN 或非預期結果 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/trigger-step.test.tsx:53` | 測試僅驗證欄位可見性，未涵蓋互動行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/tsconfig.app.json:19</code> 關閉 strict 模式將大幅降低型別安全</summary>

將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查選項（包括 `noImplicitAny`、`strictNullChecks` 等），可能隱藏潛在的型別錯誤，並與專案既有的嚴格模式慣例相違背。建議恢復為 `true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.app.json 的變更：`- "strict": true,` 改為 `+ "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> 使用 parseInt 可能導致 NaN 或非預期結果</summary>

在 Threshold 輸入的 onChange 中使用 `parseInt(e.target.value)`，若輸入為空字串或非數字字元，`parseInt` 會回傳 `NaN`，可能導致表單值變成 `NaN`。其他元件（如 custom-trigger-fields.tsx）使用 `Number(e.target.value)`，行為較一致且可預期。建議改為 `Number(e.target.value)` 或加入驗證。

**判斷依據**：diff 中 work-pool-status-trigger-fields.tsx 第 82 行：`onChange={(e) => field.onChange(parseInt(e.target.value))}`，而其他元件使用 `Number(e.target.value)`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/trigger-step.test.tsx:53</code> 測試僅驗證欄位可見性，未涵蓋互動行為</summary>

新增的測試僅檢查欄位是否可見，未測試使用者輸入、選項選擇或表單提交等互動行為。建議增加測試以驗證欄位值能正確更新表單狀態，以及在不同 posture 下顯示/隱藏條件欄位。

**判斷依據**：diff 中 trigger-step.test.tsx 的測試內容，僅有可見性斷言

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7609 (cache hit 7552) ｜ completion tokens 840 ｜ PR #10</sub>