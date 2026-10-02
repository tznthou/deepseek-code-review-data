<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 event type 連結的產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl 欄位，並調整多處 UI 顏色與樣式。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者看到錯誤或無法操作；此外，部分程式碼重複且缺少測試。建議優先確認 bookingUrl 的來源與格式，並補上對應的單元測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的 URL 前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:180` | bookingUrl 可能永遠為空，導致預覽與複製連結功能失效 | 0.75 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | 複製連結功能未使用 bookingUrl 欄位 | 0.90 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:11` | getDisplayUrl 函式缺少單元測試 | 0.70 |
| 🔸 | Minor | `companion/services/calcom.ts:1655` | getUsername 函式錯誤處理過於籠統 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的 URL 前綴</summary>

在解析 bookingUrl 以顯示 URL 前綴時，程式碼直接使用 `url.hostname` 並忽略 port，且未處理可能存在的子路徑。若 bookingUrl 包含 port（例如開發環境）或路徑結構與預期不同，顯示的前綴將不正確。建議改用 `url.origin` 並保留完整路徑（移除最後一段 slug 後），或直接顯示完整 bookingUrl 並讓使用者編輯 slug 部分。

**判斷依據**：diff 中新增的 URL 解析邏輯（BasicsTab.tsx 第 257-268 行）使用 `url.hostname` 而非 `url.host`，會遺漏 port；且未考慮 pathname 中可能包含多層路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:180</code> bookingUrl 可能永遠為空，導致預覽與複製連結功能失效</summary>

`bookingUrl` state 初始化為空字串，且未在 component 中看到設定該 state 的程式碼（可能由 props 傳入但未在 diff 中顯示）。若該值未正確設定，使用者點擊預覽或複製連結時只會看到錯誤訊息，功能完全無法使用。建議確認 bookingUrl 的來源，並在 component mount 或資料載入時正確設定。

**判斷依據**：diff 中新增 `bookingUrl` state（event-type-detail.tsx 第 180 行），但未見任何 `setBookingUrl` 呼叫；`handlePreview` 與 `handleCopyLink` 皆依賴此值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> 複製連結功能未使用 bookingUrl 欄位</summary>

在 content.ts 的 copyBtn 事件處理中，仍使用手動組成的 URL，未改用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致（例如使用自訂網域時）。建議與 previewBtn 一樣，優先使用 `eventType.bookingUrl`。

**判斷依據**：diff 中 copyBtn 的 bookingUrl 建構方式未變更（content.ts 第 1125-1128 行），而 previewBtn 已改為使用 `eventType.bookingUrl`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:11</code> getDisplayUrl 函式缺少單元測試</summary>

新增的 `getDisplayUrl` 函式包含 URL 解析與 fallback 邏輯，但未見對應的測試。建議補上測試涵蓋：有效 bookingUrl、無 bookingUrl 但有 username/slug、無 bookingUrl 且無 username、無效 URL 等情境。

**判斷依據**：diff 中新增 `getDisplayUrl` 函式（EventTypeListItemParts.tsx 第 10 行），但未見測試檔案變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/services/calcom.ts:1655</code> getUsername 函式錯誤處理過於籠統</summary>

`getUsername` 函式將所有錯誤包裝成 `Failed to get username`，喪失原始錯誤資訊，不利於除錯。建議保留原始錯誤或使用結構化錯誤。

**判斷依據**：diff 中新增的 `getUsername` 函式（calcom.ts 第 1654-1661 行）捕獲錯誤後僅拋出通用訊息。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13095 (cache hit 13056) ｜ completion tokens 1400 ｜ PR #5</sub>