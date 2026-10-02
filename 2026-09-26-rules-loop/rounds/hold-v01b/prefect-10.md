<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為自動化精靈的觸發器步驟新增了多種觸發器欄位元件（自訂、部署狀態、工作池狀態、工作佇列狀態），並更新了對應的測試。主要風險在於將 TypeScript 的 strict 模式關閉（違反 R11），這會降低型別安全；此外，數字輸入的處理方式不一致（Number vs parseInt）可能導致非預期行為。建議先恢復 strict 模式並修正型別問題，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/tsconfig.app.json:19` | [R11] 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | 數字輸入處理不一致：使用 parseInt 而非 Number | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38` | Expected Events 欄位在空輸入時可能設定為 undefined | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30` | Posture 變更時可能殘留舊欄位值 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/tsconfig.app.json:19</code> [R11] 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 違反了專案規範 R11（TypeScript Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復 `strict: true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 `- "strict": true,` 改為 `+ "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> 數字輸入處理不一致：使用 parseInt 而非 Number</summary>

在 `work-pool-status-trigger-fields.tsx` 中，Threshold 欄位的 `onChange` 使用 `parseInt(e.target.value)`，而其他元件（如 `custom-trigger-fields.tsx`）使用 `Number(e.target.value)`。`parseInt` 會忽略非數字字元（例如輸入 "12abc" 會得到 12），可能導致非預期行為。建議統一使用 `Number` 並搭配驗證。

**判斷依據**：diff 中該行使用 `parseInt`，而其他檔案使用 `Number`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38</code> Expected Events 欄位在空輸入時可能設定為 undefined</summary>

在 `custom-trigger-fields.tsx` 中，當使用者清空文字區域時，`lines` 會是 `[""]`（長度為 1），因此 `field.onChange(lines)` 會被呼叫，而不是 `undefined`。這可能導致表單值變成 `[""]` 而非預期的空陣列或 undefined。建議檢查是否為空字串並設定為空陣列或 undefined。

**判斷依據**：diff 中該邏輯未處理空字串行

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30</code> Posture 變更時可能殘留舊欄位值</summary>

在 `deployment-status-trigger-fields.tsx` 中，當 posture 從 Reactive 切換到 Proactive 時，欄位名稱從 `trigger.expect` 改為 `trigger.after`，但舊的 `trigger.expect` 值可能仍保留在表單狀態中。這可能導致提交時包含不必要的資料。建議在 posture 變更時清除對應欄位。

**判斷依據**：diff 中根據 posture 動態切換欄位名稱，但未清除舊值

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9104 (cache hit 9088) ｜ completion tokens 1035 ｜ PR #10</sub>