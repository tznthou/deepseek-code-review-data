<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 FlowIconText 元件，用於 UI v2 遷移，以連結形式顯示流程名稱與圖示。主要風險在於測試基礎設施的設定：Storybook 裝飾器中建立的 router 與 queryClient 可能與元件實際使用的 queryClient 不一致，導致測試不穩定或誤報。此外，元件本身使用 useSuspenseQuery 但未提供錯誤邊界，若查詢失敗可能導致整個應用程式崩潰。建議優先修正測試設定，並考慮加入錯誤處理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | Storybook 裝飾器中的 queryClient 與元件使用的 queryClient 不一致 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 缺少錯誤邊界，useSuspenseQuery 失敗可能導致應用程式崩潰 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> Storybook 裝飾器中的 queryClient 與元件使用的 queryClient 不一致</summary>

在 `createTestRouter` 中，`context` 使用了 `new QueryClient()`，但裝飾器外層的 `QueryClientProvider` 使用的是模組頂層的 `queryClient`。這可能導致元件內部的 `useSuspenseQuery` 使用到錯誤的 queryClient 實例，造成測試行為不一致或快取問題。建議在 `createTestRouter` 中傳入相同的 `queryClient` 實例，或將 `queryClient` 的建立移到裝飾器內。

**判斷依據**：diff 中第 24 行顯示 `context: { queryClient: new QueryClient() }`，而第 8-14 行定義了模組層級的 `queryClient`，並在第 36 行用於 `QueryClientProvider`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 缺少錯誤邊界，useSuspenseQuery 失敗可能導致應用程式崩潰</summary>

元件使用 `useSuspenseQuery`，但沒有提供錯誤邊界（Error Boundary）。如果查詢失敗（例如網路錯誤或 API 回傳 500），React 會將錯誤拋出到最近的錯誤邊界；若沒有錯誤邊界，整個應用程式可能會 unmount。建議在元件外層或應用程式路由層級加入錯誤邊界，以妥善處理查詢失敗的情況。

**判斷依據**：diff 中第 20 行顯示使用 `useSuspenseQuery`，但整個元件檔案中沒有錯誤邊界的實作或引入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2760 (cache hit 2688) ｜ completion tokens 659 ｜ PR #9</sub>