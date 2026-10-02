<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 重新設計了評論管理列表的版面，將原本多欄位的表格改為單一欄位整合顯示作者、文章、日期與操作，並新增文章特色圖片欄位。主要風險在於 `dangerouslySetInnerHTML` 渲染評論 HTML 時未見新增的消毒處理，且 `CommentContent` 的 `useEffect` 依賴陣列為空，可能導致在內容動態更新時無法正確偵測截斷狀態。另有數個 React 與程式碼風格問題，建議修正後再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | dangerouslySetInnerHTML 渲染評論 HTML 未見消毒處理 | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空可能導致截斷偵測失效 | 0.75 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:106` | [R13] Button 元件缺少 type 屬性 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:88` | [R19] 缺少分號 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:106` | [R12] JSX props 順序不符合標準 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:76` | [R15] Tailwind class 順序不符合標準 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:106` | 圖片缺少 loading="lazy" 與尺寸設定 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> dangerouslySetInnerHTML 渲染評論 HTML 未見消毒處理</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。雖然此程式碼在修改前已存在，但本次重構將渲染邏輯抽離，且未見任何消毒（sanitization）處理。若評論內容來自使用者輸入且未在伺服器端或客戶端消毒，可能導致 XSS 攻擊。建議確認 `item.html` 的來源是否已消毒，或在此處使用 DOMPurify 等函式庫進行消毒。

**判斷依據**：diff 中新增的 `CommentContent` 元件包含此行，且未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空可能導致截斷偵測失效</summary>

`CommentContent` 中的 `useEffect` 僅在掛載時執行一次（依賴陣列為 `[]`），但 `item.html` 可能在之後更新（例如從 API 取得資料或狀態變更）。若內容變更，`isClamped` 不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入依賴陣列，或改用 `useLayoutEffect` 並在內容變更時重新檢查。

**判斷依據**：依賴陣列為空，但函式內使用 `contentRef.current` 與 `item.html` 相關的 DOM 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:106</code> [R13] Button 元件缺少 type 屬性</summary>

多個 `<Button>` 元件未指定 `type` 屬性。在表單中可能導致意外提交，且違反專案規範 R13。建議為所有按鈕加上 `type="button"`（或適當的 type）。

**判斷依據**：diff 中新增的 `ExpandButton` 與其他按鈕均未見 type 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:88</code> [R19] 缺少分號</summary>

`CommentContent` 元件中 `useRef` 與 `useState` 的陳述式結尾缺少分號，違反專案規範 R19。建議補上分號。

**判斷依據**：diff 中新增的程式碼行末無分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:106</code> [R12] JSX props 順序不符合標準</summary>

多個 JSX 元素的 props 順序未依照專案規範 R12（reserved props 先、一般 props 字母序、callbacks 最後）。例如 `ExpandButton` 的 `className` 應在 `size` 之前，`onClick` 應在最後。建議使用 ESLint 自動修正或手動調整。

**判斷依據**：diff 中多處 JSX 元素 props 順序混亂。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:76</code> [R15] Tailwind class 順序不符合標準</summary>

多個 className 中的 Tailwind class 順序未依照專案規範 R15。例如 `className="shrink-0 gap-0.5 self-start p-0 text-muted-foreground hover:bg-transparent"` 中 `shrink-0` 應在 `gap-0.5` 之前。建議使用 prettier-plugin-tailwindcss 自動排序。

**判斷依據**：diff 中多處 className 順序混亂。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:106</code> 圖片缺少 loading="lazy" 與尺寸設定</summary>

新增的文章特色圖片 `<img>` 未設定 `loading="lazy"`，可能影響效能。此外，僅以 CSS 設定寬度，未提供 `width`/`height` 屬性，可能導致版面跳動。建議加上 `loading="lazy"` 與明確尺寸。

**判斷依據**：diff 中新增的 img 元素。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11304 (cache hit 11264) ｜ completion tokens 1805 ｜ PR #4</sub>