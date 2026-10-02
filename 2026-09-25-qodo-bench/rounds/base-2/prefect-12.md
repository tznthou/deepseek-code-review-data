<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為 UI v2 的任務執行詳情頁增加與 Vue 版本一致的功能：動態 favicon、頁面標題、麵包屑連結參數、JSON 輸入複製按鈕，以及將條件式渲染改為一律顯示並以 'None' 表示空值。整體改動方向合理，但存在一些潛在問題：favicon 切換邏輯未處理 'CANCELLING' 與 'PAUSED' 狀態（會導致 favicon 設定為不存在的路徑）、`useStateFavicon` 在 stateType 為 null 時不會重置 favicon、`taskRun.run_count || 0` 可能將 0 以外的 falsy 值（如空字串）顯示為 0、`retry_jitter_factor` 的條件判斷可能因值為 0 而顯示 'None'。建議優先修正 favicon 狀態對應與重置邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:50` | favicon 路徑未涵蓋所有狀態，可能導致 404 | 0.90 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:49` | stateType 為 null/undefined 時不會重置 favicon | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | run_count 使用 `\|\|` 可能錯誤處理 falsy 值 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179` | retry_jitter_factor 為 0 時顯示 'None' | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:50</code> favicon 路徑未涵蓋所有狀態，可能導致 404</summary>

`stateType` 的型別包含 'CANCELLING' 和 'PAUSED'，但對應的 SVG 檔案（cancelling.svg、paused.svg）並未在此 PR 中新增。當任務處於這些狀態時，`faviconPath` 會指向不存在的檔案，瀏覽器將無法載入 favicon。建議補上對應的 SVG 檔案，或將狀態對應到現有圖示（例如 CANCELLING 使用 cancelled.svg）。

**判斷依據**：diff 中新增了 cancelled.svg、completed.svg、crashed.svg、failed.svg、pending.svg、running.svg、scheduled.svg，但沒有 cancelling.svg 或 paused.svg；而 StateType 型別包含 'CANCELLING' 和 'PAUSED'。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:49</code> stateType 為 null/undefined 時不會重置 favicon</summary>

當 `stateType` 為 null 或 undefined 時，effect 內部的 `if (stateType)` 不會執行，因此不會設定新的 favicon。但 cleanup 函式仍會執行，將 favicon 重置為預設值。這可能導致在元件掛載時 stateType 尚未載入（例如非同步取得），favicon 先被重置為預設，之後 stateType 載入後才設定為正確圖示，造成閃爍。建議在 stateType 為 null 時也明確設定為預設 favicon，或調整邏輯避免不必要的重置。

**判斷依據**：diff 中 `useStateFavicon` 的 effect 依賴 `[stateType]`，當 stateType 為 null 時，if 區塊不執行，但 cleanup 會重置 favicon。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> run_count 使用 `||` 可能錯誤處理 falsy 值</summary>

`taskRun.run_count || 0` 會將 0、空字串、NaN 等 falsy 值都顯示為 0。若 run_count 可能為空字串或 null，顯示 0 可能誤導使用者。建議改用 `taskRun.run_count ?? 0` 或明確檢查 null/undefined。

**判斷依據**：diff 中將原本條件式渲染改為 `{taskRun.run_count || 0}`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179</code> retry_jitter_factor 為 0 時顯示 'None'</summary>

條件 `taskRun.empirical_policy?.retry_jitter_factor` 在值為 0 時為 falsy，因此會顯示 'None'，但 0 是有效的 jitter factor。建議改用 `typeof ... === 'number'` 或 `??` 來判斷。

**判斷依據**：diff 中將原本的 `!== null && !== undefined` 改為 truthy 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7568 (cache hit 7552) ｜ completion tokens 1291 ｜ PR #12</sub>