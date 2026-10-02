<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 FlowIconText 元件，用於 UI v2 遷移，透過 useSuspenseQuery 取得 flow 資料並以 Link 呈現。主要風險在於 Suspense 使用方式可能導致 fallback 永遠不會顯示，以及 Storybook 中 queryClient 與 router context 的 queryClient 不一致，可能造成測試或開發時資料快取行為異常。建議先修正 Suspense 用法與統一 queryClient 來源。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14` | Suspense 未提供 fallback，可能導致載入時無 UI 回饋 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | Storybook 中 queryClient 來源不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14</code> Suspense 未提供 fallback，可能導致載入時無 UI 回饋</summary>

`<Suspense>` 沒有指定 `fallback` prop。當 `useSuspenseQuery` 暫停元件時，React 會尋找最近的 Suspense boundary 並顯示其 fallback；若沒有 fallback，則會向上尋找其他 boundary，若都沒有，則整個應用程式會 suspend 且無任何 UI 回饋。建議提供明確的 fallback，例如 `<Suspense fallback={<Skeleton />}>`。

**判斷依據**：diff 中第 14-16 行顯示 `<Suspense>` 沒有 fallback prop。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> Storybook 中 queryClient 來源不一致</summary>

`createTestRouter` 內建立新的 `QueryClient` 並放入 router context，但 decorator 使用模組層級的 `queryClient` 包裹 `QueryClientProvider`。這可能導致 `useSuspenseQuery` 使用 decorator 提供的 client，而 router context 中的 client 未被使用，造成快取行為不一致或測試時資料無法正確隔離。建議統一使用同一個 queryClient，或明確指定 provider 的 client 與 router context 相同。

**判斷依據**：diff 中第 27 行建立新的 QueryClient，而第 36 行使用模組層級的 queryClient。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2760 (cache hit 2688) ｜ completion tokens 609 ｜ PR #9</sub>