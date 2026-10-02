<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為 UI v2 的任務執行詳情頁增加與 Vue 版本的對齊功能，包括動態 favicon、頁面標題、麵包屑連結參數、JSON 輸入複製按鈕，以及將條件式渲染改為一律顯示並以 'None' 表示空值。整體改動方向合理，但存在一些潛在問題：favicon hook 在 SSR 環境可能因 window 未定義而失敗；favicon 元素可能不存在而導致功能失效；使用 `||` 處理數字 0 時會錯誤顯示 'None'；以及缺少對新 hook 的測試。建議修正這些問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:15` | SSR 環境中直接使用 window 可能導致錯誤 | 0.80 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:40` | favicon 元素可能不存在，導致功能失效 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | 使用 `\|\|` 處理數字 0 會錯誤顯示 'None' | 0.80 |
| 🔸 | Minor | `ui-v2/src/hooks/use-state-favicon.ts:1` | 缺少對新 hook 的測試 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:15</code> SSR 環境中直接使用 window 可能導致錯誤</summary>

`getPreferredColorScheme` 函式直接存取 `window.matchMedia`，但此 hook 可能在伺服器端渲染（SSR）期間被呼叫，此時 `window` 未定義，會拋出 ReferenceError。建議將 `window` 的存取移至 `useEffect` 內，或加入 `typeof window !== 'undefined'` 的檢查。

**判斷依據**：diff 中新增的 `use-state-favicon.ts` 第 15 行直接使用 `window`，而此 hook 在元件渲染時即會執行，若在 SSR 環境下會導致錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:40</code> favicon 元素可能不存在，導致功能失效</summary>

程式碼透過 `document.getElementById` 取得 favicon 元素，但若 HTML 中未定義對應的 id（例如 `favicon-16`、`favicon-32` 等），則 `favicon16` 或 `favicon32` 會是 null，後續的 `setAttribute` 呼叫將拋出 TypeError。建議加入 null 檢查或確保元素存在。

**判斷依據**：diff 中新增的 `use-state-favicon.ts` 第 31-34 行取得元素後未檢查是否為 null，直接呼叫 `setAttribute`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> 使用 `||` 處理數字 0 會錯誤顯示 'None'</summary>

在顯示 `run_count` 時使用 `taskRun.run_count || 0`，若 `run_count` 為 0（合法值），則會顯示 0，但若 `run_count` 為 null 或 undefined，也會顯示 0，可能無法區分。建議使用 `??` 運算子：`taskRun.run_count ?? 0`。

**判斷依據**：diff 中第 104 行使用 `||`，而 `run_count` 可能為 0，應使用 `??` 以正確處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:1</code> 缺少對新 hook 的測試</summary>

新增的 `useStateFavicon` hook 沒有對應的測試，建議加入單元測試以驗證 favicon 設定與重置邏輯，特別是在不同 color scheme 下的行為。

**判斷依據**：diff 中新增了 `use-state-favicon.ts`，但未見任何測試檔案。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7568 (cache hit 1536) ｜ completion tokens 1058 ｜ PR #12</sub>