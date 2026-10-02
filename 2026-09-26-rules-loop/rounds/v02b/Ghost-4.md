<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了管理後台的留言審核清單版面，將原本的表格欄位改為單一主欄位，加入作者頭像、文章縮圖、回覆/喜歡/檢舉計數，並在 API 回應中新增文章的 feature_image 欄位。整體方向合理，但存在幾個需要修正的問題：CommentContent 元件在內容未截斷時仍可能顯示展開按鈕、useEffect 依賴陣列缺少必要依賴、以及多處違反專案規範（JSX props 順序、按鈕 type 屬性、單引號、分號）。最優先應處理的是 CommentContent 的截斷判斷邏輯與 useEffect 依賴，避免 UI 行為不一致。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | CommentContent 的截斷判斷可能導致展開按鈕在內容未截斷時仍顯示 | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列缺少必要依賴 | 0.75 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:100` | [R13] Button 元素缺少明確的 type 屬性 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:102` | [R12] JSX props 順序不符合標準 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:107` | [R18] 使用雙引號字串 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:108` | [R18] 使用雙引號字串 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:112` | [R18] 使用雙引號字串 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:88` | [R19] 缺少分號 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | [R19] 缺少分號 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:107` | [R18] 使用雙引號字串 | 0.85 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> CommentContent 的截斷判斷可能導致展開按鈕在內容未截斷時仍顯示</summary>

`isClamped` 的判斷僅在元件掛載時執行一次，且依賴陣列為空。若內容在掛載後因資料更新或視窗大小改變而不再截斷，`isClamped` 不會更新，導致展開按鈕錯誤顯示。此外，`useEffect` 中使用了 `contentRef`，但依賴陣列未包含任何變數，React 的 exhaustive-deps 規則會警告。建議將 `checkIfClamped` 的邏輯放入 `useLayoutEffect` 或使用 ResizeObserver 監聽內容大小變化，並在依賴陣列中加入 `item.html` 或相關變數。

**判斷依據**：diff 中新增的 CommentContent 元件，useEffect 依賴陣列為空，但內部使用 contentRef 且未處理內容變化。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列缺少必要依賴</summary>

`useEffect` 中使用了 `contentRef`，但依賴陣列為空。雖然 `contentRef` 是 ref 物件，其參考在元件生命週期中不變，但此處的意圖是監聽內容變化，應將 `item.html` 或 `item` 加入依賴陣列，否則當留言內容更新時，截斷判斷不會重新執行。

**判斷依據**：diff 中新增的 useEffect，依賴陣列為空，但函式內使用了 contentRef 和 item.html（透過 dangerouslySetInnerHTML）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:100</code> [R13] Button 元素缺少明確的 type 屬性</summary>

在 ExpandButton 元件中，`<Button>` 沒有指定 `type` 屬性。根據專案規範 R13，所有 button 元素必須明確指定 type（button、submit 或 reset），以避免意外的表單提交行為。建議加上 `type="button"`。

**判斷依據**：diff 中新增的 ExpandButton 元件，Button 缺少 type 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:102</code> [R12] JSX props 順序不符合標準</summary>

在 ExpandButton 元件中，`onClick` 放在 `variant` 之後，但根據規範 R12，callbacks 應放在 regular props 之後。建議調整為：`className`、`size`、`variant`、`onClick`。

**判斷依據**：diff 中新增的 ExpandButton 元件，props 順序為 className, size, variant, onClick，違反 R12。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:107</code> [R18] 使用雙引號字串</summary>

在 CommentContent 元件中，`className` 使用了雙引號字串，但專案規範 R18 要求使用單引號。建議改為單引號。

**判斷依據**：diff 中新增的 CommentContent 元件，className 使用雙引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:108</code> [R18] 使用雙引號字串</summary>

在 CommentContent 元件中，`className` 使用了雙引號字串，但專案規範 R18 要求使用單引號。建議改為單引號。

**判斷依據**：diff 中新增的 CommentContent 元件，className 使用雙引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:112</code> [R18] 使用雙引號字串</summary>

在 CommentContent 元件中，`className` 使用了雙引號字串，但專案規範 R18 要求使用單引號。建議改為單引號。

**判斷依據**：diff 中新增的 CommentContent 元件，className 使用雙引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:88</code> [R19] 缺少分號</summary>

在 CommentContent 元件中，`useRef` 和 `useState` 的陳述式結尾缺少分號。專案規範 R19 要求所有陳述式以分號結尾。建議補上分號。

**判斷依據**：diff 中新增的 CommentContent 元件，useRef 和 useState 陳述式缺少分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> [R19] 缺少分號</summary>

在 CommentContent 元件中，`useEffect` 的結尾缺少分號。專案規範 R19 要求所有陳述式以分號結尾。建議補上分號。

**判斷依據**：diff 中新增的 useEffect 陳述式缺少分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:107</code> [R18] 使用雙引號字串</summary>

在 CommentContent 元件中，`className` 使用了雙引號字串，但專案規範 R18 要求使用單引號。建議改為單引號。

**判斷依據**：diff 中新增的 CommentContent 元件，className 使用雙引號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11304 (cache hit 11264) ｜ completion tokens 2540 ｜ PR #4</sub>