<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為 UI v2 的任務執行詳情頁增加與 Vue 版本一致的功能：動態 favicon、頁面標題、麵包屑導航改進、狀態圖示，以及將條件式顯示改為一律顯示並以 'None' 表示空值。整體風險中等，主要問題在於 favicon 切換邏輯未處理不支援的狀態類型、未監聽系統主題變更，以及部分欄位使用 `||` 可能將 0 或空字串顯示為 'None'。建議修正後合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:50` | favicon 路徑可能指向不存在的檔案 | 0.80 |
| 🔸 | Minor | `ui-v2/src/hooks/use-state-favicon.ts:39` | 未監聽系統主題變更 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | 使用 `\|\|` 可能將 0 或空字串顯示為 'None' | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:163` | Retries 顯示邏輯可能不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:50</code> favicon 路徑可能指向不存在的檔案</summary>

`stateType` 包含 `CANCELLING` 和 `PAUSED`，但 `public` 目錄中只有 `cancelled.svg`、`completed.svg`、`crashed.svg`、`failed.svg`、`pending.svg`、`running.svg`、`scheduled.svg`。當狀態為 `CANCELLING` 或 `PAUSED` 時，會嘗試載入 `/cancelling.svg` 或 `/paused.svg`，導致 404 並顯示預設 favicon。建議為所有可能的狀態提供對應的 SVG，或將不支援的狀態映射到現有圖示。

**判斷依據**：diff 中新增的 `use-state-favicon.ts` 第 44 行，以及 `public` 目錄下缺少 `cancelling.svg` 和 `paused.svg`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:39</code> 未監聽系統主題變更</summary>

`getPreferredColorScheme` 只在 effect 執行時讀取一次，若使用者在頁面開啟期間切換系統深淺色模式，favicon 不會更新。建議使用 `matchMedia` 的 `change` 事件監聽，或將 `colorScheme` 加入依賴陣列並在變更時重新執行 effect。

**判斷依據**：diff 中 `use-state-favicon.ts` 第 29 行，effect 依賴陣列僅有 `[stateType]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> 使用 `||` 可能將 0 或空字串顯示為 'None'</summary>

`taskRun.run_count || 0` 在 `run_count` 為 0 時會顯示 0，但若 `run_count` 為 `null` 或 `undefined` 也會顯示 0，可能誤導。同樣地，`taskRun.cache_key || "None"` 和 `taskRun.dynamic_key || "None"` 在值為空字串時會顯示 'None'，但空字串可能是合法值。建議使用 `??` 或明確檢查 `null`/`undefined`。

**判斷依據**：diff 中 `task-run-details.tsx` 第 121 行，以及後續的 `cache_key` 和 `dynamic_key` 使用 `||`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:163</code> Retries 顯示邏輯可能不一致</summary>

`taskRun.empirical_policy?.retries ?? "0"` 在 `retries` 為 0 時會顯示 0，但若為 `null` 或 `undefined` 則顯示字串 '0'，型別不一致。建議統一使用數字或字串，或明確處理 null/undefined。

**判斷依據**：diff 中 `task-run-details.tsx` 第 137 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9766 (cache hit 9728) ｜ completion tokens 1116 ｜ PR #12</sub>