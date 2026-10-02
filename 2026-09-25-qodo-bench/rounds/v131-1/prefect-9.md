<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 FlowIconText 元件，用於在 UI v2 中顯示帶有 Workflow 圖示的 flow 名稱連結。主要風險在於元件使用 useSuspenseQuery 但未提供 error boundary，且 stories 中的 router context 與 QueryClientProvider 的 queryClient 不一致，可能導致測試或使用上的問題。建議先修正 error boundary 與 router context 的設定。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 使用 useSuspenseQuery 但未提供 error boundary | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | Router context 中的 queryClient 與實際使用的 queryClient 不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 使用 useSuspenseQuery 但未提供 error boundary</summary>

`useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或應用程式層級加入 error boundary，或改用 `useQuery` 並自行處理錯誤狀態。

**判斷依據**：diff 中新增的 `useSuspenseQuery` 呼叫，且未見任何 error boundary 相關程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> Router context 中的 queryClient 與實際使用的 queryClient 不一致</summary>

在 `createTestRouter` 中，`context` 設定了新的 `QueryClient`，但 decorator 中使用的 `QueryClientProvider` 是外部的 `queryClient`。這可能導致 router 內部使用不同的 queryClient，造成快取不一致或測試問題。建議統一使用同一個 queryClient 實例。

**判斷依據**：diff 中 `createTestRouter` 的 context 設定與 decorator 中的 `QueryClientProvider` 使用不同的 queryClient。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2724 (cache hit 1408) ｜ completion tokens 534 ｜ PR #9</sub>