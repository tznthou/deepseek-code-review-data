<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 FlowIconText 元件，用於在 UI v2 中顯示帶有 Workflow 圖示的 flow 名稱連結。主要風險在於元件使用 useSuspenseQuery 但未提供錯誤處理，且 Storybook 設定中 QueryClient 的建立方式可能導致快取與測試隔離問題。建議補上錯誤邊界與調整 QueryClient 的建立方式。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | useSuspenseQuery 缺少錯誤處理 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32` | Storybook 中 QueryClient 建立方式可能導致快取共用 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> useSuspenseQuery 缺少錯誤處理</summary>

`useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 ErrorBoundary 包覆，整個應用程式可能因此崩潰。建議在元件外層加上 ErrorBoundary，或在查詢選項中設定 `retry` 與 `onError` 來處理錯誤。

**判斷依據**：diff 中新增的 `useSuspenseQuery` 呼叫沒有搭配 ErrorBoundary，且 `buildFLowDetailsQuery` 的實作未提供，無法確認是否已處理錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32</code> Storybook 中 QueryClient 建立方式可能導致快取共用</summary>

`createTestRouter` 每次呼叫都會建立新的 `QueryClient`，但 decorator 中使用的 `queryClient` 是模組層級的單例，可能導致不同 story 之間共用快取，影響測試隔離。建議在 decorator 內建立新的 QueryClient 並傳入 Router 的 context。

**判斷依據**：diff 中 `createTestRouter` 內建立新的 QueryClient，但 decorator 使用模組層級的 `queryClient`，兩者不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2724 (cache hit 2688) ｜ completion tokens 547 ｜ PR #9</sub>