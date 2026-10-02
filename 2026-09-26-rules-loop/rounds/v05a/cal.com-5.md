<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的 booking URL 從動態建構改為使用 API 回傳的 bookingUrl 欄位，並調整了多處 UI 顏色與樣式。主要風險在於 bookingUrl 可能為空或格式不符時，前端顯示與複製/分享功能會失效；此外，BasicsTab 中解析 bookingUrl 的邏輯可能產生錯誤的顯示前綴。建議先確認 API 是否保證 bookingUrl 存在且格式正確，並修正 URL 解析邏輯。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的顯示前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽與複製功能失效 | 0.75 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/index.ios.tsx:114` | bookingUrl 可能為空，導致複製/分享/預覽功能失效 | 0.70 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/index.tsx:136` | bookingUrl 可能為空，導致複製/分享/預覽功能失效 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.60 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:16` | getDisplayUrl 可能顯示不完整的 URL | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的顯示前綴</summary>

在 `BasicsTab` 中，程式碼嘗試從 `bookingUrl` 解析出 domain 與 path 前綴，但邏輯有誤：
- 若 `bookingUrl` 為 `https://cal.com/username/30min`，`pathParts` 為 `['username', '30min']`，移除 slug 後為 `['username']`，回傳 `https://cal.com/username/`，正確。
- 但若 `bookingUrl` 為 `https://i.cal.com/keith/30min`，`pathParts` 為 `['keith', '30min']`，移除 slug 後為 `['keith']`，回傳 `https://i.cal.com/keith/`，但實際上 `i.cal.com` 是短網域，booking URL 可能不含 username，此時應回傳 `https://i.cal.com/`。
- 此外，若 `bookingUrl` 為 `https://cal.com/username/30min?metadata[foo]=bar`，`pathname` 不含 query，但 `URL` 物件會正確解析，此處無問題。
建議：不要自行解析，而是直接使用 `bookingUrl` 的前綴（例如移除最後一個 path segment），或由 API 提供明確的 `bookingUrlPrefix` 欄位。

**判斷依據**：diff 中新增的 URL 解析邏輯，在處理短網域（如 i.cal.com）時會錯誤地包含 username 路徑段。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽與複製功能失效</summary>

`handlePreview` 與 `handleCopyLink` 現在直接使用 `bookingUrl` state，但該 state 的初始值為空字串，且未見何處被設定。若使用者尚未儲存 event type 或 API 未回傳 bookingUrl，則點擊預覽或複製只會顯示錯誤訊息，功能完全無法使用。
建議：確認 `bookingUrl` 的來源與更新時機，若可能為空，應提供 fallback（例如使用舊的 `buildEventTypeLink` 邏輯）或在使用前先檢查並提示。

**判斷依據**：diff 中 `handlePreview` 與 `handleCopyLink` 的修改，直接依賴 `bookingUrl` state，但未見其被賦值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:114</code> bookingUrl 可能為空，導致複製/分享/預覽功能失效</summary>

在 `EventTypesIOS` 中，`handleCopyLink`、`_handleShare`、`handlePreview` 都新增了 `if (!eventType.bookingUrl)` 的檢查，若 `bookingUrl` 不存在則直接顯示錯誤並返回。這可能導致使用者無法使用這些功能，尤其是當 API 未回傳該欄位時。
建議：確認 API 是否保證 `bookingUrl` 一定存在，若否，應提供 fallback 或在使用前先嘗試取得。

**判斷依據**：diff 中新增的檢查邏輯，若 `bookingUrl` 為空則功能完全無法使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/index.tsx:136</code> bookingUrl 可能為空，導致複製/分享/預覽功能失效</summary>

在 `EventTypes` 中，`handleCopyLink`、`_handleShare`、`handlePreview` 同樣新增了 `if (!eventType.bookingUrl)` 的檢查，若 `bookingUrl` 不存在則直接顯示錯誤並返回。這可能導致使用者無法使用這些功能，尤其是當 API 未回傳該欄位時。
建議：確認 API 是否保證 `bookingUrl` 一定存在，若否，應提供 fallback 或在使用前先嘗試取得。

**判斷依據**：diff 中新增的檢查邏輯，若 `bookingUrl` 為空則功能完全無法使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 `content.ts` 的 `copyBtn` 事件處理中，建構 `bookingUrl` 時仍使用舊的 `https://cal.com/${username}/${slug}` 邏輯，未使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 booking URL 不一致（例如使用短網域或自訂網域時）。
建議：與其他按鈕一致，使用 `eventType.bookingUrl || fallback`。

**判斷依據**：diff 中此處未修改，但其他按鈕已改用 `eventType.bookingUrl`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:16</code> getDisplayUrl 可能顯示不完整的 URL</summary>

`getDisplayUrl` 函式在 `bookingUrl` 存在時回傳 `url.hostname + url.pathname`，但若 `bookingUrl` 包含 port 或 protocol 不同（如 `http://`），顯示時會遺漏 protocol 與 port，可能造成使用者混淆。
建議：考慮顯示完整的 URL，或至少包含 protocol。

**判斷依據**：diff 中新增的函式，回傳值缺少 protocol。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13879 (cache hit 12416) ｜ completion tokens 1931 ｜ PR #5</sub>