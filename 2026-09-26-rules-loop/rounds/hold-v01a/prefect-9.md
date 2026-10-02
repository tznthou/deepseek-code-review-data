<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 FlowIconText 元件，用於在 UI v2 中顯示帶有 Workflow 圖示的 flow 名稱連結。主要風險在於元件使用 useSuspenseQuery 取得資料，但外層的 Suspense 沒有提供 fallback，可能導致使用者看到空白畫面；此外，測試檔案缺失（違反 R10），且 stories 中的 QueryClient 設定可能造成快取污染。建議先補上 Suspense fallback 與測試，再考慮合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14` | Suspense 缺少 fallback，可能導致空白畫面 | 0.90 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21` | 查詢函式名稱拼寫錯誤：buildFLowDetailsQuery | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12` | Storybook decorator 中的 QueryClient 可能造成快取污染 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:6` | 未使用的匯入：Skeleton | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1` | 缺少對應的測試檔案（R10） | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14</code> Suspense 缺少 fallback，可能導致空白畫面</summary>

元件使用 `useSuspenseQuery` 取得資料，但外層的 `<Suspense>` 沒有提供 `fallback` prop。當查詢處於 pending 狀態時，React 會暫停渲染並尋找最近的 Suspense boundary；如果沒有 fallback，使用者會看到空白內容，直到資料載入完成。建議提供一個載入中的 UI，例如 `<Suspense fallback={<Skeleton />}>`，以改善使用者體驗。

**判斷依據**：diff 中第 13-15 行顯示 `<Suspense>` 沒有 fallback 屬性，而 `FlowIconTextImplementation` 使用了 `useSuspenseQuery`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21</code> 查詢函式名稱拼寫錯誤：buildFLowDetailsQuery</summary>

匯入的查詢建構函式名稱為 `buildFLowDetailsQuery`，其中 `FLow` 的大小寫可能不符合命名慣例（應為 `buildFlowDetailsQuery`）。這可能導致可讀性問題，且若其他程式碼使用正確拼寫，會造成不一致。建議確認函式名稱並修正。

**判斷依據**：diff 中第 20 行顯示使用了 `buildFLowDetailsQuery`，而匯入來源為 `@/api/flows`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12</code> Storybook decorator 中的 QueryClient 可能造成快取污染</summary>

在 `createTestRouter` 中，每次呼叫都會建立一個新的 `QueryClient` 並傳入 router context，但 decorator 外層的 `QueryClientProvider` 使用的是模組層級的 `queryClient`。這可能導致不同 story 之間共用快取，造成測試資料互相干擾。建議在 decorator 內建立新的 `QueryClient` 並傳遞給 `QueryClientProvider`，以確保每個 story 有獨立的查詢客戶端。

**判斷依據**：diff 中第 8-14 行定義了模組層級的 `queryClient`，並在第 38 行用於 `QueryClientProvider`，而 `createTestRouter` 內又建立了新的 `QueryClient`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:6</code> 未使用的匯入：Skeleton</summary>

檔案中匯入了 `Skeleton` 元件，但在程式碼中並未使用。這可能違反 R12（未使用的匯入應自動移除），並增加 bundle 大小。建議移除未使用的匯入。

**判斷依據**：diff 中第 5 行匯入了 `Skeleton`，但整個檔案中沒有使用到它。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1</code> 缺少對應的測試檔案（R10）</summary>

根據規範 R10，每個 React 元件檔案應有同目錄下的測試檔案（`flow-icon-text.test.tsx`）。此 PR 新增了元件但未包含測試，可能降低測試覆蓋率。建議補上測試，涵蓋載入狀態、成功渲染和錯誤處理。

**判斷依據**：diff 中只新增了元件檔案，沒有對應的測試檔案。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4255 (cache hit 2688) ｜ completion tokens 1274 ｜ PR #9</sub>