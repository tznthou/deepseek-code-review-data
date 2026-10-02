<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 FlowIconText 元件，用於在 UI v2 中顯示 flow 名稱與圖示，並連結到 flow 詳細頁。主要風險在於元件使用 useSuspenseQuery 但未提供錯誤邊界，可能導致整個應用程式在查詢失敗時崩潰；此外，Storybook 設定中 QueryClient 的建立方式可能造成快取與測試隔離問題。建議先補上錯誤處理與測試，再考慮合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | useSuspenseQuery 缺少錯誤邊界，查詢失敗可能導致應用程式崩潰 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12` | Storybook decorator 中 QueryClient 實例可能造成快取污染 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1` | 未提供對應的測試檔案 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> useSuspenseQuery 缺少錯誤邊界，查詢失敗可能導致應用程式崩潰</summary>

`useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有被 ErrorBoundary 捕獲，會導致整個 React 元件樹卸載。建議在 FlowIconText 外層包覆 ErrorBoundary，或改用 `useQuery` 並自行處理錯誤狀態。

**判斷依據**：diff 中新增的 flow-icon-text.tsx 第 19 行使用 useSuspenseQuery，但檔案中未見任何 ErrorBoundary 或錯誤處理邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12</code> Storybook decorator 中 QueryClient 實例可能造成快取污染</summary>

`createTestRouter` 每次呼叫都會建立新的 QueryClient，但 decorator 外層的 `queryClient` 是模組層級的單例。這可能導致不同 story 之間共用快取，影響測試隔離性。建議將 QueryClient 的建立移入 decorator 內，或使用 Storybook 的 `parameters` 來注入。

**判斷依據**：diff 中 flow-icon-text.stories.tsx 第 4-10 行定義了模組層級的 queryClient，並在第 27 行的 decorator 中使用，但 createTestRouter 內又建立了新的 QueryClient，可能造成不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1</code> 未提供對應的測試檔案</summary>

根據規範 R10，React 元件測試檔案應與元件放在同一目錄。此 PR 新增了 flow-icon-text.tsx，但未見 flow-icon-text.test.tsx。建議補上測試，至少涵蓋成功載入與錯誤處理的情境。

**判斷依據**：diff 中僅新增 stories 與元件檔案，沒有測試檔案。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4255 (cache hit 4224) ｜ completion tokens 808 ｜ PR #9</sub>