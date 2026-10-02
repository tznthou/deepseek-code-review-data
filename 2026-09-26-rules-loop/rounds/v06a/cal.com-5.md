<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的連結產生方式從動態呼叫 API 改為使用後端提供的 bookingUrl，並進行多處 UI 調整（顏色改為黑色、移除部分邊框、增加 flex 樣式）。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者看到錯誤訊息或顯示不正確的連結；此外，部分程式碼重複且缺少測試。建議優先確認 bookingUrl 的來源與格式，並補齊相關測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的 prefix | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽/複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.70 |
| 🔸 | Minor | `companion/services/calcom.ts:1655` | getUsername 的錯誤處理可能隱藏原始錯誤 | 0.65 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:11` | getDisplayUrl 的 fallback 邏輯可能產生不一致的顯示 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的 prefix</summary>

在 `BasicsTab.tsx` 中，從 `bookingUrl` 解析 prefix 的邏輯假設 URL 的最後一個 path segment 是 slug，並將其移除。但若 bookingUrl 包含 query string、hash，或 slug 並非最後一個 segment（例如有 trailing slash），則可能產生錯誤的 prefix。例如 `https://cal.com/user/event?foo=bar` 會得到 `https://cal.com/user/`，但預期可能是 `https://cal.com/user/event/`。建議改為從後端直接取得 prefix，或使用更可靠的解析方式。

**判斷依據**：diff 中新增的程式碼片段，行號約 257-268。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽/複製功能失效</summary>

`handlePreview` 和 `handleCopyLink` 現在直接使用 `bookingUrl` state，但該 state 的初始值為空字串，且未看到何處被設定。若使用者尚未儲存 event type 或後端未回傳 bookingUrl，則會顯示錯誤訊息，但使用者可能不清楚如何取得 bookingUrl。建議在載入 event type 時一併取得 bookingUrl，或提供明確的引導。

**判斷依據**：diff 中 `handlePreview` 和 `handleCopyLink` 的修改，行號約 949-960。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 `copyBtn` 的 click handler 中，bookingUrl 的建構方式仍為手動拼接，未使用 `eventType.bookingUrl`，與其他地方的修改不一致。這可能導致複製的連結與實際 bookingUrl 不同。建議統一使用 `eventType.bookingUrl || fallback` 的模式。

**判斷依據**：diff 中 copyBtn 的修改，行號約 1122-1125。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/services/calcom.ts:1655</code> getUsername 的錯誤處理可能隱藏原始錯誤</summary>

`getUsername` 函式在 catch 中拋出一個新的 Error，但未保留原始錯誤資訊，不利於除錯。建議使用 `throw new Error("Failed to get username", { cause: error })` 或直接 rethrow。

**判斷依據**：diff 中新增的 getUsername 函式，行號約 1654-1661。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:11</code> getDisplayUrl 的 fallback 邏輯可能產生不一致的顯示</summary>

`getDisplayUrl` 在 bookingUrl 存在時回傳 `url.hostname + url.pathname`，但若 bookingUrl 包含 protocol 以外的資訊（如 port），則顯示可能不完整。此外，fallback 邏輯在 username 存在時回傳 `/${username}/${slug}`，但若 slug 為空則可能產生 `//`。建議統一處理 edge cases。

**判斷依據**：diff 中新增的 getDisplayUrl 函式，行號約 7-18。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13900 (cache hit 12416) ｜ completion tokens 1445 ｜ PR #5</sub>