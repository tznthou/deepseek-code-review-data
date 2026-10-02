<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並整合到編輯路由中。整體結構清晰，測試涵蓋了主要互動流程。主要風險在於表單提交時未處理非同步錯誤（handleSubmit 未 await），可能導致未捕獲的 Promise rejection；此外，測試中對 useUpdateWorkPool 的 mock 方式可能與實際 hook 的 API 不符，需確認。建議先修正錯誤處理，並驗證測試的可靠性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41` | handleSubmit 未 await updateWorkPool，可能導致未捕獲的 Promise rejection | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28` | 測試中 mock 的 useUpdateWorkPool 回傳值可能與實際 hook 不符 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41</code> handleSubmit 未 await updateWorkPool，可能導致未捕獲的 Promise rejection</summary>

在 `handleSubmit` 中，`updateWorkPool` 被呼叫但沒有 `await` 或回傳其 Promise。如果 `updateWorkPool` 內部拋出同步錯誤或回傳 rejected Promise，這個錯誤將不會被捕獲，可能導致 unhandled promise rejection。建議將 `handleSubmit` 改為 async 並 `await updateWorkPool(...)`，或至少回傳該 Promise 讓 react-hook-form 處理。

**判斷依據**：diff 中 `handleSubmit` 函式內呼叫 `updateWorkPool` 但未處理其回傳值，且函式未宣告為 async。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28</code> 測試中 mock 的 useUpdateWorkPool 回傳值可能與實際 hook 不符</summary>

測試中 mock 的 `useUpdateWorkPool` 回傳物件包含 `updateWorkPool` 和 `isPending`，但實際 hook 可能回傳不同的屬性名稱（例如 `mutate` 或 `isLoading`）。這可能導致測試通過但實際使用時出錯。建議確認 `useUpdateWorkPool` 的實際 API，並調整 mock 以符合。

**判斷依據**：diff 中 mock 回傳的物件結構可能與實際 hook 不一致，需查證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9256 (cache hit 1536) ｜ completion tokens 698 ｜ PR #13</sub>