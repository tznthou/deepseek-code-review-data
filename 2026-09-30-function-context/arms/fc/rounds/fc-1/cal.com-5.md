<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl，並統一將強調色從藍色改為黑色。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者看到錯誤訊息或顯示不正確的連結；此外，部分元件新增的 style 屬性可能影響既有佈局，需確認視覺回歸。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的 URL 前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | handlePreview 與 handleCopyLink 依賴 bookingUrl state，但 state 可能未正確更新 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.60 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:21` | getDisplayUrl 的 fallback 邏輯可能產生不一致的顯示 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的 URL 前綴</summary>

在 `BasicsTab.tsx` 中，解析 `bookingUrl` 以取得前綴的邏輯會將 URL 的 pathname 最後一段移除，但若 `bookingUrl` 的 pathname 不包含 slug（例如 `https://cal.com/username`），則會錯誤地移除 username，導致前綴變成 `https://cal.com/`。此外，若 `bookingUrl` 包含 query string 或 hash，這些部分不會被包含在前綴中，可能導致顯示不完整。建議改為直接使用 `bookingUrl` 的 origin 加上 pathname 的前段，或由後端提供明確的 prefix 欄位。

**判斷依據**：diff 中新增的程式碼片段，位於 BasicsTab.tsx 的 URL 顯示區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> handlePreview 與 handleCopyLink 依賴 bookingUrl state，但 state 可能未正確更新</summary>

`bookingUrl` state 的更新來源未在 diff 中顯示，若該 state 未在取得事件類型資料時設定，則使用者在儲存前點擊預覽或複製連結會看到錯誤訊息。此外，若事件類型尚未儲存，`bookingUrl` 可能為空，但使用者仍可嘗試操作，造成不佳的使用者體驗。建議確認 `bookingUrl` 的設定時機，並在 UI 上禁用相關按鈕直到 `bookingUrl` 可用。

**判斷依據**：diff 中 handlePreview 與 handleCopyLink 的修改，新增了對 bookingUrl 的檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 content.ts 的 copyBtn 事件處理中，bookingUrl 的建構仍使用硬編碼的 `https://cal.com/...`，未使用 `eventType.bookingUrl`，與其他部分的修改不一致。這可能導致複製的連結與實際 bookingUrl 不同，若後端提供了自訂網域或不同路徑，使用者會複製到錯誤的連結。建議統一使用 `eventType.bookingUrl` 或提供 fallback。

**判斷依據**：diff 中 copyBtn 的修改，未加入 eventType.bookingUrl 的使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:21</code> getDisplayUrl 的 fallback 邏輯可能產生不一致的顯示</summary>

當 `bookingUrl` 存在但解析失敗時，會 fallback 到 `/${username}/${slug}`，但若 `username` 不存在，則會顯示 `/${slug}`，與原本的行為一致。然而，若 `bookingUrl` 存在且解析成功，顯示的格式為 `hostname + pathname`，與 fallback 的格式不同，可能造成視覺上的不一致。建議統一顯示格式，或考慮僅顯示 pathname 部分。

**判斷依據**：diff 中 getDisplayUrl 函式的實作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12471 (cache hit 12416) ｜ completion tokens 1172 ｜ PR #5</sub>