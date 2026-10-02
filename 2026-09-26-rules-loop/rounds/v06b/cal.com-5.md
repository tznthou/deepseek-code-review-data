<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的 booking URL 從動態建構改為使用 API 回傳的 bookingUrl 欄位，並將多處 UI 的藍色 (#007AFF) 改為黑色 (#000000)。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者無法預覽或複製連結；此外，BasicsTab 中的 URL 前綴解析邏輯可能產生錯誤的顯示結果。建議優先確認 bookingUrl 的來源與格式，並補齊相關測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:263` | URL 前綴解析可能產生錯誤的顯示結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽/複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.60 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:21` | getDisplayUrl 的 fallback 可能產生不一致的顯示 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:263</code> URL 前綴解析可能產生錯誤的顯示結果</summary>

在 BasicsTab 中，從 bookingUrl 解析前綴的邏輯假設 URL 的最後一個 path segment 是 slug，並將其移除。然而，bookingUrl 可能包含 query string、hash，或 slug 並非最後一個 segment（例如自訂路徑），導致前綴錯誤。此外，若 bookingUrl 為相對路徑或格式不符，會 fallback 到 `cal.com/${username}/`，但此 fallback 可能與實際 bookingUrl 不一致。建議改為直接顯示 bookingUrl 的 origin + pathname（不移除最後一段），或由後端提供明確的 prefix 欄位。

**判斷依據**：diff 中新增的 URL 解析邏輯，假設最後一個 segment 是 slug 並移除，但未考慮其他 URL 結構。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽/複製功能失效</summary>

handlePreview 和 handleCopyLink 現在直接使用 state 中的 bookingUrl，但該 state 的初始值為空字串，且未在 diff 中看到何時被設定。若使用者尚未儲存 event type 或 API 未回傳 bookingUrl，則會顯示錯誤訊息。這可能造成功能回歸，因為先前是動態建構連結。建議確認 bookingUrl 的設定時機，並在無值時提供 fallback 或明確的引導。

**判斷依據**：diff 中新增的檢查，但未看到 bookingUrl 的賦值邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 content.ts 的 copyBtn 事件處理中，bookingUrl 的建構仍然使用硬編碼的 `https://cal.com/...`，而沒有像 previewBtn 一樣使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致。建議統一使用 eventType.bookingUrl 或 fallback 邏輯。

**判斷依據**：diff 中 copyBtn 的程式碼未修改，但 previewBtn 已改用 eventType.bookingUrl。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:21</code> getDisplayUrl 的 fallback 可能產生不一致的顯示</summary>

getDisplayUrl 在 bookingUrl 存在時回傳 hostname + pathname，但若 bookingUrl 為空或解析失敗，則回傳 `/${username}/${slug}`。這可能導致列表顯示的連結格式與實際 bookingUrl 不同（例如缺少 domain）。建議統一顯示格式，或直接顯示 bookingUrl 的完整 URL。

**判斷依據**：diff 中新增的 getDisplayUrl 函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13900 (cache hit 13824) ｜ completion tokens 1113 ｜ PR #5</sub>