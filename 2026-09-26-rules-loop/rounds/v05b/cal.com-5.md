<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為直接使用 API 回傳的 bookingUrl，並進行多處 UI 調整（顏色改為黑色、移除邊框、增加 flex 樣式）。主要風險在於 bookingUrl 可能不存在或格式不符預期，導致使用者看到錯誤訊息或顯示不正確的連結。此外，部分程式碼重複且缺少測試，建議補強。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的顯示前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:180` | handlePreview 依賴 bookingUrl state，但未見設定邏輯 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 事件處理中未使用 eventType.bookingUrl | 0.60 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 事件處理中 bookingUrl 建構邏輯重複 | 0.50 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯缺少測試 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的顯示前綴</summary>

在 `BasicsTab` 中，從 `bookingUrl` 解析顯示前綴的邏輯假設路徑的最後一段是 slug，並將其移除。但若 `bookingUrl` 包含 query string、hash，或路徑結構不同（例如 `/username/event-type` 但 slug 不在最後），則顯示的前綴會錯誤。此外，若 `bookingUrl` 為相對路徑或格式不合法，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。

建議：改為直接顯示 `bookingUrl` 的 origin + pathname，或由後端提供明確的 `bookingUrlPrefix` 欄位，避免前端解析。

**判斷依據**：diff 中新增的程式碼片段，位於 BasicsTab.tsx 第 257 行附近。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:180</code> handlePreview 依賴 bookingUrl state，但未見設定邏輯</summary>

`handlePreview` 現在直接使用 `bookingUrl` state，但 diff 中僅新增了 state 宣告，未看到任何設定 `bookingUrl` 的程式碼（例如從 API 回應或 props 中取得）。這可能導致 `bookingUrl` 永遠為空字串，使用者點擊預覽時只會看到錯誤訊息。

建議：確認 `bookingUrl` 的來源，並在元件掛載或資料載入時正確設定。

**判斷依據**：diff 中新增的 state 宣告，但未見 setBookingUrl 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 事件處理中未使用 eventType.bookingUrl</summary>

在 `copyBtn` 的 click 事件中，仍使用舊的邏輯建構 bookingUrl，未使用 `eventType.bookingUrl`。這可能導致複製的連結與預覽不一致。

建議：與 previewBtn 一致，改為 `eventType.bookingUrl || 舊邏輯`。

**判斷依據**：diff 中 copyBtn 事件處理的程式碼片段，未使用 eventType.bookingUrl。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 事件處理中 bookingUrl 建構邏輯重複</summary>

多處重複建構 bookingUrl 的邏輯，建議抽成共用函式以減少維護成本。

**判斷依據**：diff 中多處出現相同的 bookingUrl 建構邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯缺少測試</summary>

新增的 URL 解析邏輯較複雜，但未見對應的單元測試。建議加入測試涵蓋各種 bookingUrl 格式（含 query、hash、無 slug 等）。

**判斷依據**：diff 中新增的解析邏輯，但無測試檔案變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13879 (cache hit 13824) ｜ completion tokens 1304 ｜ PR #5</sub>