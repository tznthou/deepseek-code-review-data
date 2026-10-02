<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 的 booking URL 從「由 slug 動態組出」改為「直接使用 API 回傳的 bookingUrl」，並在 UI 上將強調色從藍色改為黑色。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者無法複製/分享/預覽連結；此外，BasicsTab 中解析 bookingUrl 的邏輯可能產生錯誤的網域前綴。建議先確認 API 一定回傳 bookingUrl，並補強空值處理與 URL 解析的錯誤處理。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:259` | bookingUrl 解析邏輯可能產生錯誤的網域前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:180` | handlePreview 與 handleCopyLink 依賴 bookingUrl state，但該 state 可能永遠為空 | 0.75 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/index.ios.tsx:114` | handleCopyLink 中對 bookingUrl 的檢查可能導致使用者無法複製連結 | 0.60 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.50 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:271` | URL 解析失敗時 fallback 到 cal.com/{username}/，可能與實際 bookingUrl 不一致 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:259</code> bookingUrl 解析邏輯可能產生錯誤的網域前綴</summary>

在 `BasicsTab` 中，程式碼嘗試從 `bookingUrl` 解析出網域前綴，但邏輯有缺陷：
- 若 `bookingUrl` 為 `https://i.cal.com/keith/30min`，`url.pathname` 為 `/keith/30min`，移除最後一段後得到 `/keith`，最後回傳 `https://i.cal.com/keith/`，但實際上正確的前綴應為 `https://i.cal.com/`（因為 `keith` 是 username，不是路徑的一部分）。
- 若 `bookingUrl` 為 `https://cal.com/keith/30min`，則回傳 `https://cal.com/keith/`，但正確前綴應為 `https://cal.com/keith/`（此例剛好正確）。
- 若 `bookingUrl` 包含 query string 或 hash，`url.pathname` 不會包含它們，但回傳的前綴會遺失這些部分。

建議：不要自行解析 bookingUrl，而是直接顯示完整的 bookingUrl，或由後端提供一個獨立的 `bookingUrlPrefix` 欄位。

**判斷依據**：diff 中新增的程式碼區塊（BasicsTab.tsx 第 254-273 行）顯示了這個解析邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:180</code> handlePreview 與 handleCopyLink 依賴 bookingUrl state，但該 state 可能永遠為空</summary>

`handlePreview` 和 `handleCopyLink` 現在直接使用 `bookingUrl` state，但這個 state 的初始值為空字串，且程式碼中沒有看到任何地方呼叫 `setBookingUrl` 來設定它。這可能導致使用者在儲存 event type 之前點擊預覽或複製連結時，永遠看到「Booking URL not available」的錯誤。

建議：確認 `bookingUrl` 是否應該從 props 或 API 取得，並在元件掛載時設定；或者保留原本的 `buildEventTypeLink` 作為 fallback。

**判斷依據**：diff 中新增了 `bookingUrl` state（第 180 行），但沒有看到對應的 `setBookingUrl` 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:114</code> handleCopyLink 中對 bookingUrl 的檢查可能導致使用者無法複製連結</summary>

在 `handleCopyLink` 中，如果 `eventType.bookingUrl` 為空，會顯示錯誤並 return。但原本的實作會嘗試用 `buildEventTypeLink` 動態產生連結，即使 API 沒有回傳 bookingUrl 也能運作。如果 API 在某些情況下不提供 bookingUrl（例如舊版 API 或特定權限），使用者將無法複製連結。

建議：保留 fallback 邏輯，當 bookingUrl 不存在時，仍使用 `buildEventTypeLink` 或類似的機制產生連結。

**判斷依據**：diff 中新增了這個檢查（index.ios.tsx 第 114-117 行），移除了原本的 `buildEventTypeLink` 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 `copyBtn` 的 click handler 中，bookingUrl 的建構方式仍然是手動拼接 `https://cal.com/...`，沒有使用 `eventType.bookingUrl`。這可能導致複製的連結與預覽的連結不一致（如果 API 回傳的 bookingUrl 是自訂網域或不同路徑）。

建議：與其他 handler 一致，使用 `eventType.bookingUrl || fallback` 的模式。

**判斷依據**：diff 中此處的程式碼沒有被修改（第 1122-1125 行），但其他類似區塊都改為使用 `eventType.bookingUrl`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:271</code> URL 解析失敗時 fallback 到 cal.com/{username}/，可能與實際 bookingUrl 不一致</summary>

當 `bookingUrl` 存在但無法被 `new URL()` 解析時（例如格式錯誤），程式碼會 fallback 到 `cal.com/${props.username}/`。這可能導致顯示的 URL 前綴與實際的 bookingUrl 完全不同，造成使用者混淆。

建議：在解析失敗時，直接顯示完整的 bookingUrl 或顯示一個通用的提示，而不是猜測前綴。

**判斷依據**：diff 中新增的程式碼區塊（BasicsTab.tsx 第 254-273 行）顯示了這個 fallback 邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13920 (cache hit 12416) ｜ completion tokens 1786 ｜ PR #5</sub>