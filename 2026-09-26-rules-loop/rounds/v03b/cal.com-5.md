<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的 booking URL 從動態建構改為使用 API 回傳的 bookingUrl 欄位，並將多處 UI 的強調色從藍色改為黑色。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者無法複製或分享連結；此外，BasicsTab 中的 URL 前綴解析邏輯可能產生錯誤的顯示結果。建議優先確認 bookingUrl 的資料來源與格式，並補齊相關測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | URL 前綴解析邏輯可能產生錯誤的顯示結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能未初始化，導致預覽/複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.70 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/index.ios.tsx:31` | 移除 CalComAPIService 匯入後，可能遺留未使用的 import | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> URL 前綴解析邏輯可能產生錯誤的顯示結果</summary>

在 `BasicsTab.tsx` 中，透過解析 `bookingUrl` 來產生 URL 前綴的邏輯存在缺陷。當 `bookingUrl` 為 `https://cal.com/username/event-slug` 時，`pathParts` 為 `['username', 'event-slug']`，移除最後一個元素後得到 `['username']`，最後回傳 `https://cal.com/username/`，這可能正確。但若 `bookingUrl` 為 `https://i.cal.com/username/event-slug`，則回傳 `https://i.cal.com/username/`，這可能不是預期的顯示格式（例如應顯示 `i.cal.com/username/`）。此外，若 `bookingUrl` 包含 query string 或 hash，`url.pathname` 不會包含它們，但 `url.hostname` 可能包含 port，導致顯示不一致。建議明確規範 bookingUrl 的格式，或直接使用 `bookingUrl` 本身作為顯示文字，避免自行解析。

**判斷依據**：diff 中新增的 URL 解析邏輯，試圖從 bookingUrl 提取前綴，但未考慮不同 domain 或路徑結構的變化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能未初始化，導致預覽/複製功能失效</summary>

在 `handlePreview` 和 `handleCopyLink` 中，直接使用 `bookingUrl` state，但該 state 的初始值為空字串，且未看到在何處被設定。若使用者尚未儲存 event type 或 API 未回傳 bookingUrl，則會顯示錯誤訊息，但使用者可能不清楚如何取得 bookingUrl。建議確認 bookingUrl 的設定時機，並在 UI 上提供明確的引導。

**判斷依據**：diff 中新增的檢查，但未看到 bookingUrl 的賦值邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 `copyBtn` 的 click handler 中，bookingUrl 的建構仍使用舊的 `https://cal.com/...` 方式，未使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致。建議與其他 handler 一致，使用 `eventType.bookingUrl ||` 的 fallback 模式。

**判斷依據**：diff 中此處未修改，但其他類似 handler 已改用 eventType.bookingUrl。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:31</code> 移除 CalComAPIService 匯入後，可能遺留未使用的 import</summary>

移除了 `CalComAPIService` 的匯入，但未確認是否仍有其他程式碼使用它。若無使用，則為多餘的 import，應一併移除。

**判斷依據**：diff 中移除了 CalComAPIService 的匯入，但未檢查其他使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13920 (cache hit 13824) ｜ completion tokens 1238 ｜ PR #5</sub>