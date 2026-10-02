<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 FlowIconText 元件，用於在 UI v2 中顯示流程名稱與圖示並連結至流程詳情頁。主要風險在於 Storybook 測試設定中 QueryClient 的建立方式可能導致快取污染，以及元件本身缺少錯誤處理與可存取性考量。建議先修正測試環境的 QueryClient 管理，並考慮加入錯誤邊界與 aria-label。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12` | Storybook 全域 QueryClient 可能導致測試間狀態污染 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 缺少錯誤處理，查詢失敗時元件會直接拋出錯誤 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:27` | 連結缺少可存取性標籤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12</code> Storybook 全域 QueryClient 可能導致測試間狀態污染</summary>

`queryClient` 在模組頂層建立，且 `createTestRouter` 內部又建立新的 `QueryClient` 但未使用。全域 `queryClient` 會被所有 story 共用，若某個 story 的快取資料被修改，可能影響其他 story 的渲染結果，導致測試不穩定。建議在每個 decorator 中建立新的 `QueryClient`，或使用 `QueryClientProvider` 的 `key` prop 強制重新掛載。

**判斷依據**：第 10-16 行建立全域 queryClient，第 24 行在 createTestRouter 中又建立新的 QueryClient 但未使用，第 37 行 decorator 使用全域 queryClient。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 缺少錯誤處理，查詢失敗時元件會直接拋出錯誤</summary>

`useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 ErrorBoundary 包覆，整個應用程式可能崩潰。建議在元件外層加入 ErrorBoundary，或在查詢選項中設定 `retry` 與 `onError` 處理。

**判斷依據**：第 22 行使用 useSuspenseQuery，但元件本身沒有錯誤處理邏輯，且未見 ErrorBoundary 包覆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:27</code> 連結缺少可存取性標籤</summary>

連結內容只有圖示和流程名稱，但圖示可能無法被螢幕閱讀器正確讀取，建議加入 `aria-label` 或 `title` 屬性，提供更明確的描述。

**判斷依據**：第 27-31 行的 Link 元件沒有 aria-label 或 title。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2760 (cache hit 2688) ｜ completion tokens 807 ｜ PR #9</sub>