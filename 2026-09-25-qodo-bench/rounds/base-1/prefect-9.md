<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 FlowIconText 元件，用於在 UI v2 中顯示帶有 Workflow 圖示的 flow 名稱連結。主要風險在於元件使用 useSuspenseQuery 但未提供 error boundary，且 stories 中的 queryClient 設定可能導致測試不穩定。建議先補上錯誤處理與測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 缺少 error boundary 處理查詢失敗 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | stories 中 queryClient 設定不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 缺少 error boundary 處理查詢失敗</summary>

`useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或路由層級加入 error boundary，並提供 fallback UI。

**判斷依據**：diff 中第 20 行使用 useSuspenseQuery，且檔案中沒有 error boundary 相關程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> stories 中 queryClient 設定不一致</summary>

在 `createTestRouter` 中建立了一個新的 `QueryClient` 並放入 router context，但 decorator 中使用的 `QueryClientProvider` 是全域的 `queryClient`。這可能導致測試時 query client 不一致，建議統一使用同一個 instance。

**判斷依據**：diff 中第 24 行建立新的 QueryClient，而 decorator 使用全域 queryClient。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2760 (cache hit 1536) ｜ completion tokens 482 ｜ PR #9</sub>