<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 重新設計了評論管理列表的版面，將原本的表格欄位（作者、文章、日期）整合到單一欄位中，並加入文章縮圖、展開/收合內容、回覆/喜歡/檢舉計數等元素。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論 HTML，若後端未徹底消毒，可能造成 XSS；此外，`useEffect` 的依賴陣列為空，可能導致在內容動態更新時無法正確偵測截斷狀態。整體而言，功能改動合理，但需優先處理 XSS 風險與可存取性問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空可能導致截斷偵測失效 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:104` | 展開/收合按鈕缺少可存取性屬性 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:355` | 文章縮圖缺少載入失敗處理 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 評論內容可能包含未受信任的連結 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未經伺服器端徹底消毒（例如允許 `<script>` 或事件處理器），攻擊者可注入惡意腳本，在管理員檢視評論時執行。建議確認後端已使用如 DOMPurify 等函式庫進行嚴格消毒，或在前端渲染前再次消毒。

**判斷依據**：diff 中新增的 `CommentContent` 元件包含此行，直接將 `item.html` 插入 DOM。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空可能導致截斷偵測失效</summary>

`useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示錯誤。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監聽內容變化。

**判斷依據**：依賴陣列為空，且 `item.html` 未包含在內。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:104</code> 展開/收合按鈕缺少可存取性屬性</summary>

`ExpandButton` 元件使用 `Button` 但未提供 `aria-expanded` 屬性，螢幕閱讀器使用者無法得知內容是否已展開。建議加入 `aria-expanded={expanded}` 並考慮使用 `aria-controls` 關聯內容區域。

**判斷依據**：按鈕僅有 `onClick`，無 `aria-expanded`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:355</code> 文章縮圖缺少載入失敗處理</summary>

`<img>` 標籤直接使用 `item.post.feature_image` 作為 `src`，若圖片 URL 失效或載入失敗，會顯示破圖。建議加入 `onError` 處理或使用 fallback 圖片。

**判斷依據**：無 `onError` 處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 評論內容可能包含未受信任的連結</summary>

評論 HTML 中可能包含 `<a>` 標籤，若未加上 `rel="noopener noreferrer"`，點擊後可能導致 `window.opener` 安全風險。建議在渲染前對連結進行處理，或確認後端已加入防護。

**判斷依據**：直接渲染 HTML，無法保證連結屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11304 (cache hit 8960) ｜ completion tokens 1304 ｜ PR #4</sub>