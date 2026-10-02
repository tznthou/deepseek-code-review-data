<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 FlowIconText 元件，用於在 UI v2 中顯示 flow 名稱與圖示，並連結到 flow 詳細頁。主要風險在於 Storybook 測試設定中 QueryClient 的建立方式可能導致快取共用與測試隔離問題，以及元件本身缺少錯誤處理與可存取性考量。建議先修正測試設定，並考慮加入錯誤邊界與 aria-label。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12` | Storybook decorator 中 QueryClient 共用可能導致測試隔離問題 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 缺少錯誤處理，查詢失敗時可能導致整個應用程式崩潰 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:29` | 連結缺少可存取性標籤，圖示可能被螢幕閱讀器忽略 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12</code> Storybook decorator 中 QueryClient 共用可能導致測試隔離問題</summary>

在 decorator 中使用了模組層級的 `queryClient`（第 9 行），並在 `createTestRouter` 中又建立了一個新的 `QueryClient` 傳入 router context。這會造成兩個不同的 QueryClient 實例：一個提供給 `QueryClientProvider`，另一個存在 router context 中。如果元件或其依賴的 hooks 使用 router context 中的 queryClient，快取將不會被共用，可能導致非預期的行為或測試污染。建議統一使用同一個 QueryClient，或明確區分用途。

**判斷依據**：第 9-15 行定義了模組層級的 queryClient，第 25 行在 createTestRouter 中又建立了新的 QueryClient 並放入 context。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 缺少錯誤處理，查詢失敗時可能導致整個應用程式崩潰</summary>

使用 `useSuspenseQuery` 會在查詢失敗時拋出錯誤，如果沒有 ErrorBoundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層加入 ErrorBoundary，或在查詢選項中設定 `throwOnError: false` 並手動處理錯誤狀態。

**判斷依據**：第 20 行使用 useSuspenseQuery，但元件本身沒有錯誤處理邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:29</code> 連結缺少可存取性標籤，圖示可能被螢幕閱讀器忽略</summary>

連結內容包含圖示和文字，但圖示沒有提供替代文字（如 `aria-hidden` 或 `alt`），且連結本身沒有 `aria-label`。如果圖示是裝飾性的，應加上 `aria-hidden="true"`；如果具有意義，應提供文字描述。這有助於螢幕閱讀器使用者理解連結目的。

**判斷依據**：第 27 行使用了 Icon 元件，但沒有提供任何無障礙屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2760 (cache hit 2688) ｜ completion tokens 834 ｜ PR #9</sub>