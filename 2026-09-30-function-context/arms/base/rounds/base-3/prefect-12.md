<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在改善 UI v2 的任務執行詳細頁面，使其與 Vue 版本的功能對齊。主要變更包括：新增基於任務狀態的 favicon 切換、設定頁面標題、調整麵包屑導航連結、在 JSON 輸入元件加入複製功能，以及重構任務詳細資訊的顯示邏輯，使其在缺少資料時顯示「None」而非隱藏欄位。整體而言，變更方向合理，但存在一些潛在問題：favicon 切換邏輯在 SSR 環境下可能因 `window` 未定義而失敗；`useStateFavicon` 的 cleanup 函式可能因閉包變數在 effect 重新執行時被覆寫而無法正確還原；此外，部分欄位使用 `||` 運算子處理數值 0 或空字串時可能顯示不正確。建議優先處理 SSR 相容性與 cleanup 邏輯，並確認數值 0 的顯示行為。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:15` | SSR 環境下直接存取 window 可能導致錯誤 | 0.80 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:55` | cleanup 函式可能無法正確還原 favicon | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | 使用 `\|\|` 可能錯誤處理數值 0 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117` | 使用 `\|\|` 可能錯誤處理空字串 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179` | 使用 `\|\|` 可能錯誤處理數值 0 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:15</code> SSR 環境下直接存取 window 可能導致錯誤</summary>

`getPreferredColorScheme` 函式直接使用 `window.matchMedia`，但此 hook 可能在伺服器端渲染（SSR）期間被呼叫，此時 `window` 未定義，會拋出 ReferenceError。建議在函式內加入 `typeof window === 'undefined'` 的檢查，或將邏輯移至 `useEffect` 內（因為 effect 僅在客戶端執行）。

**判斷依據**：新增的 hook 檔案中，`getPreferredColorScheme` 在函式主體直接存取 `window`，而此函式在 `useEffect` 外被呼叫（第 31 行），若在 SSR 階段執行會失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:55</code> cleanup 函式可能無法正確還原 favicon</summary>

在 `useEffect` 的回傳 cleanup 函式中，使用了 `colorScheme` 變數，但該變數是在 effect 執行時決定的。若 effect 因 `stateType` 改變而重新執行，新的 effect 會先執行 cleanup（使用舊的 `colorScheme`），然後再執行新的 effect。然而，cleanup 中使用的 `favicon16` 和 `favicon32` 是舊的 DOM 元素參考，但這些元素在 DOM 中仍然存在，因此設定 href 仍有效。但若 `colorScheme` 在兩次執行之間發生變化（例如使用者切換系統主題），cleanup 會使用舊的 `colorScheme` 來決定要還原成哪個預設 favicon，可能導致還原錯誤。建議在 cleanup 中重新取得當前的 color scheme，或直接使用固定的預設路徑。

**判斷依據**：cleanup 函式依賴於 effect 執行時捕獲的 `colorScheme`，若在 effect 生命週期內主題變更，可能導致還原到錯誤的預設圖示。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> 使用 `||` 可能錯誤處理數值 0</summary>

在顯示 Run Count 時使用 `{taskRun.run_count || 0}`，若 `run_count` 為 0（合法值），則會顯示 0，這符合預期。但若 `run_count` 為其他 falsy 值（如 null、undefined），也會顯示 0，可能掩蓋資料缺失。建議使用 `??` 運算子以精確處理 null/undefined。

**判斷依據**：此處使用 `||` 運算子，當 `run_count` 為 0 時會顯示 0，但若為 null 或 undefined 也會顯示 0，無法區分「0」與「無資料」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117</code> 使用 `||` 可能錯誤處理空字串</summary>

在顯示 Cache Key 和 Dynamic Key 時使用 `{taskRun.cache_key || "None"}`，若 `cache_key` 為空字串（合法值），則會顯示「None」，可能造成混淆。建議使用 `??` 運算子。

**判斷依據**：此處使用 `||` 運算子，空字串會被視為 falsy 而顯示「None」，但空字串可能是有效值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179</code> 使用 `||` 可能錯誤處理數值 0</summary>

在顯示 Retries 時使用 `{taskRun.empirical_policy?.retries ?? "0"}`，此處已使用 `??`，正確。但下方 Retry Jitter Factor 使用 `? ... : "None"`，若值為 0 會顯示「None」，可能不正確。建議改用 `??` 或明確檢查 null/undefined。

**判斷依據**：此處使用三元運算子檢查 truthiness，若 `retry_jitter_factor` 為 0（合法值），會顯示「None」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7568 (cache hit 7552) ｜ completion tokens 1692 ｜ PR #12</sub>