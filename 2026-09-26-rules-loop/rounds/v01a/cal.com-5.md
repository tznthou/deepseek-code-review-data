<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl 欄位，並進行多項 UI 調整（顏色改為黑色、增加 flex 樣式、移除部分邊框）。主要風險在於 bookingUrl 可能為空或格式不符預期，導致使用者無法預覽或複製連結；此外，BasicsTab 中的 URL 前綴解析邏輯可能產生錯誤的顯示結果。建議優先確認 bookingUrl 的來源與格式，並補強空值處理。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | URL 前綴解析邏輯可能產生錯誤的顯示結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能為空，導致預覽和複製功能失效 | 0.75 |
| 🔸 | Minor | `companion/app/(tabs)/(event-types)/index.ios.tsx:114` | bookingUrl 可能為空，導致分享功能失效 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | 複製按鈕未使用 bookingUrl 欄位 | 0.70 |
| 🔸 | Minor | `companion/services/calcom.ts:1655` | getUsername 函數的錯誤處理可能隱藏原始錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> URL 前綴解析邏輯可能產生錯誤的顯示結果</summary>

在解析 bookingUrl 以取得前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號（若存在）。此外，若 bookingUrl 包含查詢字串或 hash，這些部分不會被移除，可能導致顯示不正確。建議使用 `url.origin` 並確保路徑處理正確，或直接顯示完整 URL 並讓使用者編輯。

**判斷依據**：diff 中新增的 URL 解析邏輯（BasicsTab.tsx 第 257 行附近）使用 `url.hostname` 而非 `url.host`，且未處理查詢字串或 hash。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能為空，導致預覽和複製功能失效</summary>

`handlePreview` 和 `handleCopyLink` 現在依賴 `bookingUrl` state，但該 state 的設定方式未在 diff 中顯示。若 `bookingUrl` 未正確初始化或更新，使用者將無法預覽或複製連結，且錯誤訊息可能不夠明確。建議確認 `bookingUrl` 的來源與更新時機，並在 UI 上提供明確的提示。

**判斷依據**：diff 中 `handlePreview` 和 `handleCopyLink` 改為檢查 `bookingUrl`，但未顯示其設定邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/app/(tabs)/(event-types)/index.ios.tsx:114</code> bookingUrl 可能為空，導致分享功能失效</summary>

`_handleShare` 現在直接使用 `eventType.bookingUrl`，若該欄位為空，分享訊息將缺少連結。雖然有檢查並顯示錯誤，但使用者可能不清楚原因。建議在 UI 上提供更明確的提示，或考慮 fallback 到舊的連結產生方式。

**判斷依據**：diff 中 `_handleShare` 新增空值檢查，但未提供替代方案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> 複製按鈕未使用 bookingUrl 欄位</summary>

在 content.ts 的複製按鈕事件處理中，仍使用舊的連結產生方式（`https://cal.com/...`），未改用 `eventType.bookingUrl`。這可能導致複製的連結與其他功能不一致。建議統一使用 `eventType.bookingUrl` 並提供 fallback。

**判斷依據**：diff 中此處未修改，但其他類似功能已改用 `eventType.bookingUrl`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/services/calcom.ts:1655</code> getUsername 函數的錯誤處理可能隱藏原始錯誤</summary>

新增的 `getUsername` 函數在 catch 中拋出一個新的 Error，但未包含原始錯誤資訊，可能導致除錯困難。建議保留原始錯誤作為 cause 或記錄原始錯誤。

**判斷依據**：diff 中新增的 getUsername 函數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13910 (cache hit 12416) ｜ completion tokens 1376 ｜ PR #5</sub>