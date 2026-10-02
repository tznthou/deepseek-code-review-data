<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為直接使用 API 回傳的 bookingUrl，並統一將強調色從藍色改為黑色。主要風險在於 bookingUrl 可能為空或格式不符預期，導致 UI 顯示錯誤或功能失效；此外，BasicsTab 中的 URL 前綴解析邏輯可能產生不正確的顯示結果。建議優先確認 bookingUrl 的來源與格式，並補強空值處理與測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | URL 前綴解析可能產生錯誤的顯示結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽與複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:21` | getDisplayUrl 的 fallback 可能產生不一致的顯示 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | 複製按鈕未使用 bookingUrl 欄位 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> URL 前綴解析可能產生錯誤的顯示結果</summary>

在解析 bookingUrl 以取得前綴時，程式碼直接使用 `url.hostname` 並忽略 port，且未處理子路徑可能包含使用者名稱以外的情況。例如，若 bookingUrl 為 `https://cal.com/team/event-slug`，前綴會是 `https://cal.com/team/`，但實際應為 `https://cal.com/`。此外，若 bookingUrl 包含 port（如 `https://localhost:3000/user/slug`），顯示結果會缺少 port。建議改為使用 `url.origin` 並搭配已知的使用者名稱來建構前綴，或直接顯示完整 URL 的一部分。

**判斷依據**：diff 中新增的程式碼片段，使用 `url.hostname` 而非 `url.host`，且未考慮路徑結構可能與預期不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽與複製功能失效</summary>

`handlePreview` 和 `handleCopyLink` 現在直接使用 `bookingUrl` state，但該 state 的初始值為空字串，且未見在何處被設定。若使用者尚未儲存事件類型或 API 未回傳 bookingUrl，這兩個功能將無法使用。建議確認 bookingUrl 的設定時機，並在元件載入時從 API 取得或提供明確的 fallback。

**判斷依據**：diff 中新增的檢查，但未見 bookingUrl 的賦值邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:21</code> getDisplayUrl 的 fallback 可能產生不一致的顯示</summary>

當 bookingUrl 存在但解析失敗時，會回退到 `/${username}/${slug}` 或 `/${slug}`，但若 username 或 slug 為 undefined，可能顯示 `undefined`。建議在 fallback 中檢查這些值是否存在，或提供更安全的預設值。

**判斷依據**：diff 中新增的函式，未處理 username 或 slug 可能為 undefined 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> 複製按鈕未使用 bookingUrl 欄位</summary>

在 copyBtn 的事件處理中，仍使用手動建構的 URL，而非優先使用 `eventType.bookingUrl`。這可能導致複製的連結與實際的 bookingUrl 不一致。建議與其他處理一致，使用 `eventType.bookingUrl ||` 的 fallback 模式。

**判斷依據**：diff 中此處未修改，但其他類似區塊已改為使用 bookingUrl。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12471 (cache hit 12416) ｜ completion tokens 1180 ｜ PR #5</sub>