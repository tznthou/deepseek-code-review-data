<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 新增 FlowIconText 元件與其 Storybook 檔案。主要風險在於 Storybook 的 decorator 中 QueryClientProvider 與 RouterProvider 的 context 不一致，可能導致測試或展示時資料取得異常；此外元件本身缺少對應的測試檔案，違反 R10。整體而言功能簡單，但需補上測試並修正 decorator 的 context 設定。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | QueryClientProvider 與 RouterProvider 使用不同的 QueryClient 實例 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1` | [R10] 缺少對應的測試檔案 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> QueryClientProvider 與 RouterProvider 使用不同的 QueryClient 實例</summary>

在 decorator 中，`QueryClientProvider` 使用模組層級的 `queryClient`，但 `createTestRouter` 內部的 `context` 卻傳入 `new QueryClient()`。這會導致 `useSuspenseQuery` 在 RouterProvider 的 context 中找不到對應的 QueryClient，可能拋出錯誤或無法正確取得資料。建議統一使用同一個 QueryClient 實例，例如將模組層級的 `queryClient` 傳入 `createTestRouter` 的 context。

**判斷依據**：diff 中第 33 行 `context: { queryClient: new QueryClient() }` 與第 38 行 `<QueryClientProvider client={queryClient}>` 使用不同的 QueryClient 實例。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1</code> [R10] 缺少對應的測試檔案</summary>

根據規範 R10，每個 React 元件檔案應有同目錄下的測試檔案（`flow-icon-text.test.tsx`）。本次新增元件但未提供測試，建議補上測試以確保元件行為正確。

**判斷依據**：diff 中新增了 `flow-icon-text.tsx`，但沒有對應的 `flow-icon-text.test.tsx`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4292 (cache hit 4224) ｜ completion tokens 565 ｜ PR #9</sub>