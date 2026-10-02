<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從前端動態呼叫 API 改為直接使用後端提供的 bookingUrl，並統一將強調色從藍色改為黑色。主要風險在於 bookingUrl 可能為空或格式不符，導致 UI 顯示異常或功能失效；另外，BasicsTab 中的 URL 解析邏輯可能產生錯誤的前綴。建議先確認 bookingUrl 的資料來源與格式，並補強空值處理。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:259` | bookingUrl 解析邏輯可能產生錯誤的 URL 前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽與複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:16` | getDisplayUrl 可能顯示不完整的網址 | 0.60 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | 複製連結時未使用 bookingUrl，可能導致不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:259</code> bookingUrl 解析邏輯可能產生錯誤的 URL 前綴</summary>

在 `BasicsTab` 中，程式碼嘗試從 `bookingUrl` 解析出網域與路徑前綴，但實作有缺陷：
1. 若 `bookingUrl` 為 `https://cal.com/username/30min`，`pathParts` 為 `['username', '30min']`，移除最後一段後得到 `['username']`，前綴為 `/username/`，但實際應為 `/username/`（正確）。
2. 若 `bookingUrl` 為 `https://i.cal.com/keith/30min`，`pathParts` 為 `['keith', '30min']`，移除後得到 `['keith']`，前綴為 `/keith/`，但實際應為 `/`（因為 `i.cal.com` 是子網域，路徑不應包含使用者名稱）。
3. 若 `bookingUrl` 為 `https://cal.com/username/30min?metadata[foo]=bar`，`pathname` 不包含 query，但 `url.hostname` 可能包含 port，且未處理 port。
4. 若 `bookingUrl` 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊為空，導致回退到 `cal.com/${props.username}/`，可能與實際 bookingUrl 不一致。
建議：直接使用 `bookingUrl` 的完整網址，或提供明確的後端欄位來取得前綴，避免前端解析。

**判斷依據**：diff 中新增的程式碼片段，位於 BasicsTab.tsx 的 URL 顯示區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽與複製功能失效</summary>

在 `handlePreview` 和 `handleCopyLink` 中，若 `bookingUrl` 為空字串，會顯示錯誤訊息並中斷。但 `bookingUrl` 的來源是 `useState<string>("")`，且未看到從何處設定。若使用者尚未儲存事件類型，或後端未回傳 bookingUrl，這些功能將無法使用。建議：
1. 確認 `bookingUrl` 的設定時機，並在取得後才啟用按鈕。
2. 若 `bookingUrl` 可能為空，應提供明確的提示或引導使用者儲存。

**判斷依據**：diff 中 `handlePreview` 和 `handleCopyLink` 的修改。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:16</code> getDisplayUrl 可能顯示不完整的網址</summary>

`getDisplayUrl` 回傳 `url.hostname + url.pathname`，但若 `bookingUrl` 包含 port（例如 `https://cal.com:8080/username/30min`），則會遺漏 port。此外，若 `bookingUrl` 為 `https://cal.com/username/30min?metadata[foo]=bar`，query string 不會顯示，但這可能不是問題。建議：使用 `url.host` 取代 `url.hostname`，以包含 port。

**判斷依據**：diff 中新增的 `getDisplayUrl` 函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> 複製連結時未使用 bookingUrl，可能導致不一致</summary>

在 `copyBtn` 的 click handler 中，程式碼仍然使用 `https://cal.com/${username}/${slug}` 來建構連結，而沒有使用 `eventType.bookingUrl`。這可能導致複製的連結與實際的 bookingUrl 不同（例如使用自訂網域或子網域時）。建議：與其他 handler 一致，使用 `eventType.bookingUrl || fallback`。

**判斷依據**：diff 中 `copyBtn` 的修改，未使用 `eventType.bookingUrl`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13910 (cache hit 13824) ｜ completion tokens 1469 ｜ PR #5</sub>