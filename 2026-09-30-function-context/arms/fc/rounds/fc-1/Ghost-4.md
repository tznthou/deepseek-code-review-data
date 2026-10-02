<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了評論管理清單的版面，將原本的表格欄位整合為單一欄位，並加入作者、文章、時間、計數與文章特色圖片等資訊。主要風險在於 `CommentContent` 元件中 `dangerouslySetInnerHTML` 的使用，以及 `useEffect` 僅在掛載時執行一次，可能導致內容變更或圖片載入後截斷判斷不準確。此外，`formatDate` 的正規表達式替換可能因 locale 差異而失效。整體而言，功能改動合理，但需注意上述問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | dangerouslySetInnerHTML 可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空，可能無法正確偵測內容截斷 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:70` | formatDate 的正規表達式替換可能因 locale 而失效 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> dangerouslySetInnerHTML 可能導致 XSS</summary>

`item.html` 直接透過 `dangerouslySetInnerHTML` 渲染，若評論內容未經適當消毒，攻擊者可注入惡意腳本。建議確認後端已對 HTML 進行消毒，或改用安全的渲染方式（如 DOMPurify）。

**判斷依據**：diff 中新增的 `CommentContent` 元件使用了 `dangerouslySetInnerHTML`，且 `item.html` 來自 API 回應，未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空，可能無法正確偵測內容截斷</summary>

`useEffect` 僅在掛載時執行一次，若 `item.html` 內容在掛載後變更（例如虛擬滾動重用元件），`isClamped` 可能不會更新。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監測內容變化。

**判斷依據**：diff 中 `useEffect` 的依賴陣列為空，但元件可能因虛擬滾動而重用，導致內容變更時未重新檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:70</code> formatDate 的正規表達式替換可能因 locale 而失效</summary>

`formatted.replace(/(\d+),(\s+\d{4})/, '$1$2')` 假設日期格式為「日, 年」，但不同 locale 可能產生不同格式（例如「2025年12月17日」），導致逗號未被移除。建議使用更穩健的日期格式化方式，或直接使用 `formatTimestamp`。

**判斷依據**：diff 中新增的 `formatDate` 函式使用正規表達式移除逗號，但依賴於 `Intl.DateTimeFormat` 的輸出格式，可能因 locale 而異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9502 (cache hit 1536) ｜ completion tokens 917 ｜ PR #4</sub>