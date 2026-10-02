<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 重新設計了評論管理列表的版面，將原本多欄位的表格改為單一欄位內整合作者、文章、日期與操作按鈕，並新增文章特色圖片顯示。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論 HTML，若評論內容未經適當消毒，可能導致 XSS 攻擊。此外，`useEffect` 的相依陣列為空，可能導致在內容動態更新時無法正確偵測截斷狀態。整體而言，功能改動合理，但需優先處理 XSS 風險。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.90 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 相依陣列為空可能導致截斷偵測失效 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行消毒，攻擊者可注入惡意腳本，導致儲存型 XSS。請確認 `item.html` 的來源是否已經過消毒（例如使用 DOMPurify），或改用安全的渲染方式（如 `react-html-parser` 或將 HTML 轉為純文字）。

**判斷依據**：diff 中新增的 `CommentContent` 元件內，直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`，且未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 相依陣列為空可能導致截斷偵測失效</summary>

`CommentContent` 中的 `useEffect` 僅在掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 載入或狀態變更）。若內容更新後高度改變，`isClamped` 不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

**判斷依據**：diff 中 `useEffect` 的相依陣列為空，但依賴 `item.html` 的內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8959 (cache hit 1408) ｜ completion tokens 730 ｜ PR #4</sub>