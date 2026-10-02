<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為自動化精靈的觸發步驟新增了四種觸發器表單欄位（自訂、部署狀態、工作池狀態、工作佇列狀態），並更新了對應的測試。整體結構與現有 flow-run-state 欄位一致，但存在幾個問題：最嚴重的是將 tsconfig 的 strict 模式關閉，這會降低型別安全；另外在數字輸入的處理上，部分元件使用 Number() 而工作池狀態使用 parseInt()，可能造成行為不一致；且當 posture 從 Proactive 切換回 Reactive 時，trigger.within 的值不會被清除，可能導致提交不必要的資料。建議修復 strict 設定與數字處理的一致性，並考慮在切換 posture 時清除 within 欄位。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/tsconfig.app.json:19` | 關閉 TypeScript strict 模式會降低型別安全 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78` | 數字輸入使用 parseInt 而非 Number，可能導致非預期結果 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:16` | 切換 posture 時未清除 trigger.within 欄位 | 0.70 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27` | 切換 posture 時未清除 trigger.within 欄位 | 0.70 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:28` | 切換 posture 時未清除 trigger.within 欄位 | 0.70 |
| ⚠️ | Major | `ui-v2/src/components/automations/automations-wizard/trigger-step/work-queue-status-trigger-fields.tsx:28` | 切換 posture 時未清除 trigger.within 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/tsconfig.app.json:19</code> 關閉 TypeScript strict 模式會降低型別安全</summary>

將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查，包括 `strictNullChecks`、`strictFunctionTypes` 等，可能導致未處理的 null/undefined 錯誤、錯誤的型別推斷，並隱藏潛在的執行時期錯誤。這通常不是一個可接受的變更，除非有明確的技術原因。建議恢復為 `true`，並修正任何因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.app.json 的變更：`- "strict": true,` 改為 `+ "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78</code> 數字輸入使用 parseInt 而非 Number，可能導致非預期結果</summary>

在 `work-pool-status-trigger-fields.tsx` 中，Threshold 欄位的 `onChange` 使用 `parseInt(e.target.value)`，而其他元件（如 `custom-trigger-fields.tsx`、`deployment-status-trigger-fields.tsx`、`work-queue-status-trigger-fields.tsx`）使用 `Number(e.target.value)`。`parseInt` 會解析字串直到遇到非數字字元，例如輸入 "10abc" 會得到 10，而 `Number` 會得到 NaN。這可能導致使用者輸入無效值時，表單狀態不一致。建議統一使用 `Number`，並考慮加入驗證。

**判斷依據**：diff 中 work-pool-status-trigger-fields.tsx 的該行，與其他檔案中的 `Number(e.target.value)` 形成對比。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:16</code> 切換 posture 時未清除 trigger.within 欄位</summary>

當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

**判斷依據**：在 custom-trigger-fields.tsx 中，`trigger.within` 的渲染條件為 `posture === "Proactive"`，但沒有對應的清理邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27</code> 切換 posture 時未清除 trigger.within 欄位</summary>

當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

**判斷依據**：在 deployment-status-trigger-fields.tsx 中，`trigger.within` 的渲染條件為 `posture === "Proactive"`，但沒有對應的清理邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:28</code> 切換 posture 時未清除 trigger.within 欄位</summary>

當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

**判斷依據**：在 work-pool-status-trigger-fields.tsx 中，`trigger.within` 的渲染條件為 `posture === "Proactive"`，但沒有對應的清理邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/automations/automations-wizard/trigger-step/work-queue-status-trigger-fields.tsx:28</code> 切換 posture 時未清除 trigger.within 欄位</summary>

當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

**判斷依據**：在 work-queue-status-trigger-fields.tsx 中，`trigger.within` 的渲染條件為 `posture === "Proactive"`，但沒有對應的清理邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7609 (cache hit 7552) ｜ completion tokens 1733 ｜ PR #10</sub>