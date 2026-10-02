<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl 欄位，並調整多處 UI 樣式（如將藍色改為黑色、移除邊框）。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者看到錯誤或無法操作；此外，部分元件新增的 inline style 可能與 className 重複或造成維護問題。建議優先確認 bookingUrl 的來源與格式，並處理空值情境。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的顯示前綴 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 狀態可能未正確更新，導致預覽/複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:257` | URL 前綴計算邏輯重複且可讀性差 | 0.70 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:11` | getDisplayUrl 函式可能回傳不一致的格式 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的顯示前綴</summary>

在 BasicsTab 中，解析 bookingUrl 以取得顯示前綴的邏輯使用 `new URL(props.bookingUrl)`，但若 bookingUrl 是相對路徑（例如 `/username/slug`）或缺少 protocol，則會拋出例外並 fallback 到 `cal.com/${props.username}/`。這可能導致顯示的前綴與實際 bookingUrl 不一致。建議明確處理相對路徑，或直接使用 API 提供的完整 URL 進行顯示。

**判斷依據**：diff 中新增的程式碼片段：`const url = new URL(props.bookingUrl);` 位於 BasicsTab.tsx 的 URL 顯示區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 狀態可能未正確更新，導致預覽/複製功能失效</summary>

在 event-type-detail.tsx 中，新增了 `bookingUrl` state，但未看到從 API 或 props 設定此 state 的程式碼。若此 state 一直為空，則 handlePreview 和 handleCopyLink 會直接顯示錯誤，使用者無法使用預覽或複製連結功能。建議確認 bookingUrl 的來源並在取得資料後更新 state。

**判斷依據**：diff 中 handlePreview 和 handleCopyLink 的修改，新增了對 bookingUrl 的空值檢查，但未見設定 bookingUrl 的程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:257</code> URL 前綴計算邏輯重複且可讀性差</summary>

在 BasicsTab 中，使用 IIFE 來計算 URL 前綴，邏輯較為複雜且不易閱讀。建議將此邏輯提取為獨立的函式，並加上單元測試，以確保各種 bookingUrl 格式（含相對路徑、有無 protocol、有無 slug 等）都能正確處理。

**判斷依據**：diff 中 BasicsTab.tsx 的 URL 顯示區塊，新增了 IIFE 來計算前綴。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:11</code> getDisplayUrl 函式可能回傳不一致的格式</summary>

getDisplayUrl 函式在 bookingUrl 存在時回傳 `url.hostname + url.pathname`，但 fallback 時回傳 `/${username}/${slug}`（以斜線開頭）。這可能導致 UI 顯示不一致（例如有時有前導斜線，有時沒有）。建議統一格式，或明確區分顯示用途。

**判斷依據**：diff 中 EventTypeListItemParts.tsx 新增的 getDisplayUrl 函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 content.ts 的 copyBtn 事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/...`，未使用新增的 `eventType.bookingUrl` 欄位。這可能導致複製的連結與實際 bookingUrl 不一致（例如使用自訂網域時）。建議與 previewBtn 一樣，優先使用 `eventType.bookingUrl`。

**判斷依據**：diff 中 content.ts 的 copyBtn 事件處理，bookingUrl 仍為手動拼接，未使用 eventType.bookingUrl。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13910 (cache hit 1536) ｜ completion tokens 1583 ｜ PR #5</sub>