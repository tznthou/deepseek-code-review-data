<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為直接使用 API 回傳的 bookingUrl，並進行多項 UI 調整（顏色、flex 樣式、移除邊框）。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者無法複製或預覽連結；此外，部分 UI 變更可能影響視覺一致性。建議優先確認 bookingUrl 的來源與格式，並處理空值情境。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽和複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | 複製按鈕未使用 eventType.bookingUrl | 0.70 |
| 🔸 | Minor | `companion/app/(tabs)/(bookings)/index.ios.tsx:65` | 顏色變更可能影響可讀性 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的前綴</summary>

在解析 bookingUrl 以顯示 URL 前綴時，程式碼使用 `new URL(props.bookingUrl)` 並從 pathname 中移除最後一段（slug）。然而，若 bookingUrl 包含 query string 或 hash，`url.pathname` 不會包含這些部分，因此前綴可能不完整。此外，若 bookingUrl 的 pathname 為空或僅有 slug，前綴會變成 `/`，導致顯示不正確。建議改用更穩健的方式，例如直接從 bookingUrl 中移除最後一個路徑段，或使用正規表達式。

**判斷依據**：diff 中新增的程式碼片段，位於 BasicsTab.tsx 的 URL 顯示區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽和複製功能失效</summary>

handlePreview 和 handleCopyLink 現在直接使用 bookingUrl state，但該 state 的初始值為空字串，且未見在何處被設定。若使用者尚未儲存事件類型或 API 未回傳 bookingUrl，則會顯示錯誤訊息，但使用者可能不清楚如何取得 bookingUrl。建議在載入事件類型時就取得 bookingUrl，或在儲存後更新 state，並提供更明確的指引。

**判斷依據**：diff 中 handlePreview 和 handleCopyLink 的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> 複製按鈕未使用 eventType.bookingUrl</summary>

在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接，未使用 eventType.bookingUrl。這可能導致複製的連結與預覽不一致，若 bookingUrl 存在且與預設格式不同（例如使用自訂網域），使用者會複製到錯誤的連結。建議與 previewBtn 的處理方式一致，優先使用 eventType.bookingUrl。

**判斷依據**：diff 中 copyBtn 的修改，未包含 eventType.bookingUrl 的 fallback。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(bookings)/index.ios.tsx:65</code> 顏色變更可能影響可讀性</summary>

將文字顏色從 #007AFF 改為 #000000，可能降低在深色背景或特定主題下的可讀性。若應用程式支援深色模式，黑色文字在深色背景上可能難以閱讀。建議確認設計規範，或使用主題變數。

**判斷依據**：diff 中多處顏色變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12471 (cache hit 12416) ｜ completion tokens 1102 ｜ PR #5</sub>