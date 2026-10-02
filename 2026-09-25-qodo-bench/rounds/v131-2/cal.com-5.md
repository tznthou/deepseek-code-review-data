<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從前端動態組裝改為使用 API 回傳的 bookingUrl，並進行多項 UI 調整（顏色改為黑色、移除部分邊框、增加 flex 樣式）。主要風險在於 bookingUrl 可能為空或格式不符時，BasicsTab 的 URL 前綴解析邏輯可能產生錯誤顯示，且部分元件未處理 bookingUrl 缺失的 fallback。整體改動方向合理，但需確保 bookingUrl 的可靠性與顯示邏輯的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的 URL 前綴 | 0.80 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:275` | bookingUrl 為空時 fallback 顯示可能與實際不符 | 0.70 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 狀態可能未在儲存後更新 | 0.65 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | copyBtn 事件中未使用 eventType.bookingUrl | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的 URL 前綴</summary>

在 BasicsTab 中，使用 `new URL(props.bookingUrl)` 解析 bookingUrl 並移除最後一段路徑來產生前綴。若 bookingUrl 包含查詢參數或 hash，`url.pathname` 仍會正確取得路徑，但若 bookingUrl 格式為 `https://cal.com/username`（無 slug），則 `pathParts.pop()` 會移除 username，導致前綴變成根路徑 `/`，顯示不正確。此外，若 bookingUrl 為相對路徑（例如 `/username/slug`），`new URL` 會拋出錯誤，進入 fallback 顯示 `cal.com/${props.username}/`，但此 fallback 可能與實際 bookingUrl 不一致。建議改為從 bookingUrl 中提取 domain 與 path，並保留最後一段作為 slug，或直接顯示完整 bookingUrl 並讓使用者編輯 slug 部分。

**判斷依據**：diff 中新增的程式碼片段顯示使用 `new URL` 解析 bookingUrl，並以 `pathParts.pop()` 移除最後一段，但未考慮 bookingUrl 可能不含 slug 或為相對路徑的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:275</code> bookingUrl 為空時 fallback 顯示可能與實際不符</summary>

當 `props.bookingUrl` 為空或未定義時，程式碼回退到 `cal.com/${props.username}/`。但若使用者名稱包含特殊字元或實際 bookingUrl 使用自訂網域，此 fallback 可能不正確。建議在 bookingUrl 缺失時顯示提示或直接使用 API 提供的 username 與 slug 組合，並確保 username 已正確編碼。

**判斷依據**：diff 中顯示 fallback 邏輯直接使用 `props.username`，未考慮特殊字元或自訂網域。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 狀態可能未在儲存後更新</summary>

在 `handlePreview` 和 `handleCopyLink` 中，直接使用 `bookingUrl` state，但未看到在儲存事件類型後更新此 state 的邏輯。若使用者編輯了 slug 或 username 並儲存，`bookingUrl` 可能仍是舊值，導致預覽或複製的連結不正確。建議在儲存成功後更新 `bookingUrl`，或直接從最新的 eventTypeData 中取得。

**判斷依據**：diff 中新增了 `bookingUrl` state，但未顯示其更新時機；`handlePreview` 直接使用該 state，若未在儲存後更新，可能使用過期值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> copyBtn 事件中未使用 eventType.bookingUrl</summary>

在 content.ts 的 copyBtn 點擊處理中，仍使用硬編碼的 `https://cal.com/...` 建構 bookingUrl，而未使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致（例如使用自訂網域或不同路徑）。建議與 previewBtn 一樣，優先使用 `eventType.bookingUrl`，並提供 fallback。

**判斷依據**：diff 中顯示 copyBtn 的程式碼未使用 `eventType.bookingUrl`，而 previewBtn 已改用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12435 (cache hit 12416) ｜ completion tokens 1322 ｜ PR #5</sub>