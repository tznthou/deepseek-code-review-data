<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的連結產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl，並統一將 UI 強調色從藍色改為黑色。主要風險在於 bookingUrl 可能不存在或格式不符預期，導致使用者無法複製或預覽連結；此外，BasicsTab 中的 URL 前綴解析邏輯可能產生錯誤的顯示結果。建議在合併前確認 bookingUrl 的來源與格式，並補齊相關測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | URL 前綴解析邏輯可能產生錯誤的顯示結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空字串，導致預覽與複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/index.ios.tsx:31` | 移除 CalComAPIService 匯入後，可能遺留未使用的匯入 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl，可能與預覽不一致 | 0.65 |
| 🔸 | Minor | `companion/services/calcom.ts:1655` | getUsername 函式新增的 try-catch 可能隱藏原始錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> URL 前綴解析邏輯可能產生錯誤的顯示結果</summary>

在 `BasicsTab` 中，使用 `new URL(props.bookingUrl)` 解析 bookingUrl 並取出 hostname 與 pathname 作為前綴。若 bookingUrl 包含 query string 或 hash，這些部分會被忽略，但 pathname 的處理假設最後一段是 slug 並將其移除。若 bookingUrl 的 pathname 結構不同（例如包含多層路徑或 slug 不在最後），前綴可能不正確。此外，若 bookingUrl 為相對路徑或格式錯誤，會 fallback 到 `cal.com/${props.username}/`，但此 fallback 可能與實際 bookingUrl 不一致。

**失敗情境**：假設 bookingUrl 為 `https://i.cal.com/keith/30min?date=2025-01-01`，解析後 pathname 為 `/keith/30min`，移除最後一段後得到 `/keith/`，顯示為 `https://i.cal.com/keith/`，但實際前綴可能應包含 query string 或不同結構。

**建議**：確認 bookingUrl 的格式規範，並考慮使用更穩健的方式取得前綴，例如直接從 API 取得前綴或使用正規表達式。

**判斷依據**：diff 中新增的 URL 解析邏輯，假設 pathname 最後一段為 slug 並移除，但未考慮 query string 或不同路徑結構。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空字串，導致預覽與複製功能失效</summary>

在 `handlePreview` 和 `handleCopyLink` 中，檢查 `if (!bookingUrl)` 來判斷是否有可用的 bookingUrl。但 `bookingUrl` 的初始值為空字串 `""`，若使用者尚未儲存 event type 或 API 未回傳 bookingUrl，則會顯示錯誤訊息。然而，若 bookingUrl 為空字串但實際上應有值（例如 API 回傳空字串），使用者將無法使用預覽或複製功能。

**失敗情境**：使用者開啟 event type 編輯頁面，尚未儲存，此時 bookingUrl 為空字串，點擊預覽或複製會顯示錯誤訊息，但使用者可能預期能使用預設連結。

**建議**：確認 bookingUrl 的來源與更新時機，確保在 event type 載入後能正確設定。若 bookingUrl 可能為空，應提供更明確的提示或 fallback 機制。

**判斷依據**：diff 中新增的檢查，依賴 bookingUrl 狀態，但未確認其更新時機。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:31</code> 移除 CalComAPIService 匯入後，可能遺留未使用的匯入</summary>

在 `index.ios.tsx` 中，移除了 `CalComAPIService` 的匯入，但未確認是否仍有其他程式碼使用該服務。若無使用，則匯入移除是正確的；但若仍有使用，會導致編譯錯誤。

**失敗情境**：若檔案中仍有呼叫 `CalComAPIService` 的程式碼，移除匯入後會導致 TypeScript 編譯錯誤。

**建議**：確認檔案中已無任何 `CalComAPIService` 的引用。

**判斷依據**：diff 中移除了 `CalComAPIService` 的匯入，但未顯示其他相關變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl，可能與預覽不一致</summary>

在 `copyBtn` 的 click handler 中，bookingUrl 的建構方式仍使用 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這可能導致複製的連結與預覽的連結不一致，若 eventType.bookingUrl 存在且不同於預設格式。

**失敗情境**：若 eventType.bookingUrl 為自訂網域或不同路徑，使用者點擊複製會得到錯誤的連結。

**建議**：與其他 handler 一致，使用 `eventType.bookingUrl ||` 的 fallback 模式。

**判斷依據**：diff 中 copyBtn 的 bookingUrl 建構未使用 eventType.bookingUrl，而其他 handler 已改用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/services/calcom.ts:1655</code> getUsername 函式新增的 try-catch 可能隱藏原始錯誤</summary>

在 `getUsername` 中，新增了 try-catch 並在 catch 中拋出新的 Error，但未保留原始錯誤資訊。這可能導致除錯困難。

**失敗情境**：若 `getUserProfile` 失敗，錯誤訊息僅為 "Failed to get username"，無法得知實際原因。

**建議**：保留原始錯誤，例如 `throw new Error("Failed to get username", { cause: error })` 或直接讓錯誤傳播。

**判斷依據**：diff 中新增的 try-catch 區塊，未保留原始錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13095 (cache hit 12416) ｜ completion tokens 1865 ｜ PR #5</sub>