<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了評論管理清單的版面，將原本多欄表格改為單一主欄加上縮圖欄，並新增了作者、文章、時間戳、回覆/喜歡/檢舉計數等資訊的顯示。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論 HTML，若後端未徹底消毒，可能造成 XSS；此外，`useEffect` 的相依陣列為空，可能導致在內容動態更新時無法正確偵測截斷狀態。整體而言，程式碼結構清晰，但需優先處理 XSS 風險與相依性問題。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 相依陣列為空可能導致截斷偵測失效 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接插入 `item.html`。若評論內容未經徹底消毒（例如包含 `<script>` 或事件處理器），攻擊者可注入任意 JavaScript，竊取管理員 session 或執行未授權操作。建議使用 sanitize 函式庫（如 DOMPurify）在渲染前清理 HTML，或改用安全的替代方案（如將內容轉為純文字）。

**判斷依據**：diff 中新增的 `CommentContent` 元件內含此行，且 `item.html` 來自 API 回應，未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 相依陣列為空可能導致截斷偵測失效</summary>

`useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

**判斷依據**：相依陣列為空，且未包含 `item.html`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8995 (cache hit 8960) ｜ completion tokens 712 ｜ PR #4</sub>