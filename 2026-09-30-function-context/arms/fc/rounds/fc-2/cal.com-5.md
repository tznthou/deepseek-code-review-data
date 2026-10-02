<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從動態呼叫 API 改為使用 API 回傳的 bookingUrl，並進行多項 UI 調整（顏色改為黑色、加入 flex 樣式、移除部分邊框）。主要風險在於 bookingUrl 可能為空或格式不符，導致功能失效或顯示錯誤；此外，BasicsTab 中的 URL 解析邏輯可能產生錯誤的前綴，且部分程式碼重複。建議優先確認 bookingUrl 的可靠性與解析邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | URL 前綴解析可能產生錯誤結果 | 0.80 |
| ⚠️ | Major | `companion/app/(tabs)/(event-types)/event-type-detail.tsx:949` | bookingUrl 可能未初始化即被使用 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1125` | 複製連結時未使用 bookingUrl | 0.60 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:266` | URL 前綴顯示可能包含多餘的斜線 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> URL 前綴解析可能產生錯誤結果</summary>

在解析 bookingUrl 以取得前綴時，程式碼直接使用 `url.hostname`，但未包含 port（若存在），且未處理子路徑可能包含使用者名稱以外的情況。此外，若 bookingUrl 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。建議使用更穩健的解析方式，或直接顯示完整 bookingUrl。

**判斷依據**：diff 中新增的 URL 解析邏輯，使用 hostname 而非 host，且未處理 port；pathParts.pop() 假設最後一段是 slug，但若 bookingUrl 包含查詢參數或 hash 則可能出錯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>companion/app/(tabs)/(event-types)/event-type-detail.tsx:949</code> bookingUrl 可能未初始化即被使用</summary>

handlePreview 和 handleCopyLink 現在依賴 bookingUrl state，但該 state 的設定位置未在 diff 中顯示。若 bookingUrl 從未被設定（例如 API 未回傳或設定失敗），使用者將無法預覽或複製連結，且錯誤訊息可能誤導（提示先儲存，但儲存後可能仍無效）。建議確認 bookingUrl 的來源與更新時機，並提供更明確的錯誤處理。

**判斷依據**：diff 中新增的檢查，但未見 bookingUrl 的賦值邏輯，可能導致功能失效。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1125</code> 複製連結時未使用 bookingUrl</summary>

在 copyBtn 的事件處理中，bookingUrl 的建構仍使用舊的 `https://cal.com/...` 方式，未使用 eventType.bookingUrl。這可能導致複製的連結與實際 bookingUrl 不一致（例如使用自訂網域時）。建議與 previewBtn 一樣使用 eventType.bookingUrl 或 fallback。

**判斷依據**：diff 中 copyBtn 的程式碼未修改，而 previewBtn 已改為使用 eventType.bookingUrl。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:266</code> URL 前綴顯示可能包含多餘的斜線</summary>

當 bookingUrl 為根路徑（例如 `https://cal.com/username`）時，pathParts.pop() 後 pathParts 為空，prefix 設為 "/"，最後回傳 `https://cal.com/`，但實際應為 `https://cal.com/username/`。這可能導致顯示的 URL 前綴不正確。

**判斷依據**：diff 中的邏輯未考慮 pathParts 為空的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12471 (cache hit 12416) ｜ completion tokens 1214 ｜ PR #5</sub>