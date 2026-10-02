<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為直接使用 API 回傳的 bookingUrl，並進行多處 UI 調整（顏色改為黑色、移除部分邊框、增加 flex 樣式）。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者看到錯誤訊息或顯示不正確的連結；此外，部分程式碼重複且缺少測試。建議優先確認 bookingUrl 的來源與格式，並補齊相關測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的顯示前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:180` | bookingUrl 可能永遠為空，導致預覽與複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | 複製連結功能未使用 bookingUrl，可能導致不一致 | 0.70 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:11` | getDisplayUrl 函式可能回傳不一致的格式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的顯示前綴</summary>

在解析 bookingUrl 以取得顯示前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號。若 bookingUrl 包含非標準埠（例如開發環境），顯示的連結將不正確。此外，若 bookingUrl 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。建議使用 `url.host` 並考慮更完整的錯誤處理。

**判斷依據**：diff 中新增的程式碼片段，使用 `url.hostname` 而非 `url.host`，且 catch 區塊的回退值固定為 `cal.com/${props.username}/`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:180</code> bookingUrl 可能永遠為空，導致預覽與複製功能失效</summary>

新增的 `bookingUrl` state 初始值為空字串，但程式碼中未見任何設定該 state 的邏輯（例如從 API 回應或 props 中取得）。因此，`handlePreview` 和 `handleCopyLink` 將永遠顯示錯誤訊息，除非有其他未顯示的程式碼會更新此 state。建議確認是否有遺漏的 state 更新邏輯，或改為直接從 eventTypeData 取得 bookingUrl。

**判斷依據**：diff 中新增 state 宣告，但未見 setBookingUrl 被呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> 複製連結功能未使用 bookingUrl，可能導致不一致</summary>

在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這與其他地方的修改不一致，可能導致使用者複製到舊格式的連結。建議統一使用 `eventType.bookingUrl` 或提供一致的 fallback。

**判斷依據**：diff 中此處未修改，但其他類似程式碼已改為使用 `eventType.bookingUrl`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:11</code> getDisplayUrl 函式可能回傳不一致的格式</summary>

當 bookingUrl 存在且解析成功時，回傳 `url.hostname + url.pathname`，但若 bookingUrl 包含查詢參數或 hash，這些部分不會被包含，可能導致顯示不完整。此外，fallback 邏輯在 username 存在時回傳 `/${username}/${slug}`，但若 slug 為空則會產生 `/${username}/`，可能不是預期的格式。建議明確處理這些邊界情況。

**判斷依據**：diff 中新增的函式，未處理查詢參數、hash 或空 slug 的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12471 (cache hit 1536) ｜ completion tokens 1299 ｜ PR #5</sub>