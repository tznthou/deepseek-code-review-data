<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將事件類型連結的產生方式從前端動態組裝改為使用 API 回傳的 bookingUrl，並調整多處 UI 顏色與樣式。主要風險在於 bookingUrl 可能為空或格式不符時，BasicsTab 的 URL 前綴解析邏輯可能產生錯誤顯示，且部分元件未處理空值。整體改動方向合理，但需確保 bookingUrl 的可靠性與顯示邏輯的健壯性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `companion/components/event-type-detail/tabs/BasicsTab.tsx:261` | bookingUrl 解析邏輯可能產生錯誤的 URL 前綴 | 0.80 |
| 🔸 | Minor | `companion/components/event-type-detail/tabs/BasicsTab.tsx:275` | bookingUrl 為空時顯示 fallback 但可能與實際不符 | 0.70 |
| 🔸 | Minor | `companion/components/event-type-list-item/EventTypeListItemParts.tsx:16` | getDisplayUrl 未處理 bookingUrl 含 port 或非標準路徑 | 0.70 |
| 🔸 | Minor | `companion/extension/entrypoints/content.ts:1122` | copyBtn 的 bookingUrl 未使用 eventType.bookingUrl | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:261</code> bookingUrl 解析邏輯可能產生錯誤的 URL 前綴</summary>

在解析 bookingUrl 以取得前綴時，程式碼直接使用 `url.hostname` 而忽略了 port，且未處理 pathname 為空或僅有 slug 的情況。若 bookingUrl 為 `https://example.com:8080/user/slug`，前綴會變成 `https://example.com/user/`，遺失 port；若 bookingUrl 為 `https://example.com/slug`，則前綴會是 `https://example.com/`，可能不符合預期。建議使用 `url.origin` 並更嚴謹地處理路徑分段。

**判斷依據**：diff 中新增的程式碼片段，使用 `url.hostname` 而非 `url.host`，且未考慮 port。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-detail/tabs/BasicsTab.tsx:275</code> bookingUrl 為空時顯示 fallback 但可能與實際不符</summary>

當 `props.bookingUrl` 為空時，回傳 `cal.com/${props.username}/`，但若 username 也為空，則會顯示 `cal.com/undefined/`。建議在 username 缺失時提供更合理的 fallback，或隱藏前綴。

**判斷依據**：diff 中新增的 fallback 程式碼。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/components/event-type-list-item/EventTypeListItemParts.tsx:16</code> getDisplayUrl 未處理 bookingUrl 含 port 或非標準路徑</summary>

`getDisplayUrl` 直接回傳 `url.hostname + url.pathname`，若 bookingUrl 包含 port（如 `https://example.com:8080/user/slug`），顯示會遺失 port；若 pathname 為空，則僅顯示 hostname。建議使用 `url.host` 並處理空 pathname。

**判斷依據**：diff 中新增的函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>companion/extension/entrypoints/content.ts:1122</code> copyBtn 的 bookingUrl 未使用 eventType.bookingUrl</summary>

在 copyBtn 的事件處理中，bookingUrl 仍使用硬編碼的 `https://cal.com/...`，未像 previewBtn 一樣使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致。建議改為 `eventType.bookingUrl || ...`。

**判斷依據**：diff 中 copyBtn 的程式碼未使用 eventType.bookingUrl。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12435 (cache hit 1408) ｜ completion tokens 1056 ｜ PR #5</sub>