<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要改善 UI v2 的 task run details 頁面，使其與 Vue 版本一致：新增狀態圖示、設定頁面標題與 favicon、調整詳細資料欄位顯示邏輯。整體改動合理，但存在一個可能導致 React 錯誤的邏輯問題：在 `TaskRunDetails` 中，`taskRun.flow_run_id` 存在但 `flow_run_name` 為空時，會渲染出空的連結。此外，`useStateFavicon` hook 在 SSR 環境下直接存取 `window`，可能造成錯誤。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:45` | flow_run_id 存在但 flow_run_name 為空時渲染空連結 | 0.80 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:15` | SSR 環境下直接存取 window 可能導致錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:45</code> flow_run_id 存在但 flow_run_name 為空時渲染空連結</summary>

原本的條件是 `taskRun.flow_run_name && taskRun.flow_run_id`，現在改成只檢查 `taskRun.flow_run_id`。如果 `flow_run_id` 有值但 `flow_run_name` 為 null/undefined，會進入第一個分支，但 `<Link>` 內顯示的 `taskRun.flow_run_name` 會是空的，導致使用者看到一個沒有文字的連結。建議改回同時檢查兩者，或是在名稱缺失時顯示 fallback 文字。

**判斷依據**：diff 中將條件從 `taskRun.flow_run_name && taskRun.flow_run_id` 改為 `taskRun.flow_run_id`，但下方 `<Link>` 內仍使用 `taskRun.flow_run_name` 作為顯示文字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:15</code> SSR 環境下直接存取 window 可能導致錯誤</summary>

`getPreferredColorScheme` 函式直接使用 `window.matchMedia`，但此 hook 可能在伺服器端渲染（SSR）時被呼叫，此時 `window` 未定義，會拋出 ReferenceError。建議加入 `typeof window !== 'undefined'` 的檢查，或將此邏輯移至 `useEffect` 內（該 hook 已在 `useEffect` 中呼叫此函式，但函式本身仍可能在 SSR 時被執行）。

**判斷依據**：新檔案 `use-state-favicon.ts` 中的 `getPreferredColorScheme` 函式直接使用 `window`，且此函式在 `useEffect` 內被呼叫，但 `useEffect` 在 SSR 時不會執行，因此函式本身不會在 SSR 時被呼叫。然而，若此 hook 被用於其他情境（如直接在元件 render 中呼叫），則可能出錯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9063 (cache hit 7552) ｜ completion tokens 735 ｜ PR #12</sub>