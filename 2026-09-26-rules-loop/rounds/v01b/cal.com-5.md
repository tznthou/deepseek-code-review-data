<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為使用後端提供的 bookingUrl，並進行多處 UI 調整（顏色改為黑色、移除部分邊框、增加 flex 樣式）。主要風險在於 bookingUrl 可能為空或格式不符時，前端處理邏輯是否完善，以及 URL 解析邏輯在特殊情況下的正確性。整體改動方向合理，但需注意 bookingUrl 的來源與一致性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空字串，導致預覽/複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/index.ios.tsx:114` | bookingUrl 缺失時僅顯示錯誤，未提供替代方案 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的前綴</summary>

在解析 bookingUrl 以取得前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號。若 bookingUrl 包含非預設埠（例如開發環境），顯示的前綴會不正確。此外，若 bookingUrl 的 pathname 只有 slug（例如 `https://cal.com/30min`），`pathParts.pop()` 後陣列為空，前綴會是 `/`，但實際應為 `https://cal.com/`。建議改用 `url.origin` 並保留完整路徑結構。

**判斷依據**：diff 中新增的 URL 解析邏輯使用 `url.hostname` 而非 `url.host`，且未處理 pathname 僅有 slug 的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空字串，導致預覽/複製功能失效</summary>

handlePreview 和 handleCopyLink 僅檢查 `!bookingUrl`，但 bookingUrl 的初始值為空字串，若使用者尚未儲存事件類型，會顯示錯誤訊息。然而，若後端回傳的 bookingUrl 為空字串（例如未設定），使用者將無法使用預覽或複製功能，且錯誤訊息可能誤導。建議在取得事件類型資料時，若 bookingUrl 缺失，應提供明確的提示或停用相關按鈕。

**判斷依據**：diff 中新增的檢查僅判斷空字串，未區分未儲存與後端未提供 bookingUrl 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:114</code> bookingUrl 缺失時僅顯示錯誤，未提供替代方案</summary>

在 handleCopyLink、_handleShare 和 handlePreview 中，若 eventType.bookingUrl 不存在，僅顯示錯誤訊息。但舊版會嘗試動態建立連結，現在完全依賴後端提供 bookingUrl。若後端資料不完整，使用者將無法執行這些操作。建議保留 fallback 機制，或確保後端必定提供 bookingUrl。

**判斷依據**：diff 中新增的檢查直接 return，未提供任何替代方案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 copyBtn 的事件處理中，bookingUrl 的建構仍使用硬編碼的 `https://cal.com/...`，未使用 eventType.bookingUrl。這可能導致複製的連結與實際預覽不一致。建議與 previewBtn 的邏輯保持一致，使用 eventType.bookingUrl 或 fallback。

**判斷依據**：diff 中 copyBtn 的程式碼未修改，但 previewBtn 已改用 eventType.bookingUrl，兩者不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13910 (cache hit 13824) ｜ completion tokens 1220 ｜ PR #5</sub>