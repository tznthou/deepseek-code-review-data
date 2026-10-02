<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 重新設計了評論管理列表的版面，將原本多欄表格改為單一主欄加上縮圖欄，並新增了作者、文章、時間戳、回覆/喜歡/檢舉計數等資訊的顯示。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論 HTML，且未見任何消毒處理，若評論內容可被使用者控制，可能導致 XSS。此外，`useEffect` 依賴陣列為空，但內部使用了 `item.html`，可能導致內容更新時 clamp 狀態未重新計算。整體而言，功能改動合理，但安全性與狀態同步問題需要修正。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染未消毒的評論 HTML，可能導致 XSS | 0.90 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列缺少 item.html，可能導致 clamp 狀態未更新 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 時未提供 fallback 內容 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染未消毒的評論 HTML，可能導致 XSS</summary>

`CommentContent` 元件直接使用 `dangerouslySetInnerHTML={{__html: item.html || ''}}` 渲染評論內容。如果 `item.html` 來自使用者輸入且未經伺服器端消毒，攻擊者可以注入任意 HTML/JavaScript，造成儲存型 XSS。請確認後端在儲存評論時已進行嚴格的 HTML 消毒（例如使用 DOMPurify 或類似工具），或在前端渲染前進行消毒。

**判斷依據**：diff 中新增的 `CommentContent` 元件內含此行，且無任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列缺少 item.html，可能導致 clamp 狀態未更新</summary>

`CommentContent` 的 `useEffect` 依賴陣列為空 `[]`，但內部使用了 `item.html` 來判斷內容是否被截斷。當 `item.html` 改變時（例如評論被編輯或載入不同評論），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。建議將 `item.html` 加入依賴陣列，或改用 `useLayoutEffect` 並在依賴中列出相關變數。

**判斷依據**：diff 中新增的 `CommentContent` 元件，`useEffect` 依賴陣列為空，但函式內使用了 `item.html`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 時未提供 fallback 內容</summary>

當 `item.html` 為空字串時，`dangerouslySetInnerHTML` 會渲染空內容，但元件仍會顯示。建議在 `item.html` 為空時顯示替代文字（例如「此評論無內容」），以提升使用者體驗。

**判斷依據**：diff 中該行直接使用 `item.html || ''`，未處理空值情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10184 (cache hit 10112) ｜ completion tokens 950 ｜ PR #4</sub>