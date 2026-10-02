<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 重新設計了評論管理列表的版面，將原本多欄位的表格改為單一主欄位整合作者、時間、文章與內容，並加入文章特色圖片、回覆/喜歡/檢舉計數，同時在 API 回應中新增 post.feature_image 欄位。主要風險在於前端使用 dangerouslySetInnerHTML 渲染評論 HTML，若後端未徹底消毒，可能造成 XSS；此外，CommentContent 元件在內容變更時不會重新計算是否被截斷，可能導致「Show more」按鈕狀態錯誤。另有少數程式碼風格問題（缺少分號、單引號、JSX props 順序）需要修正。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論 HTML 可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:88` | [R19] 缺少分號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:112` | [R18] 使用雙引號字串 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | CommentContent 的截斷偵測不會在內容變更時重新執行 | 0.75 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:110` | [R12] JSX props 順序不符合規範 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論 HTML 可能導致 XSS</summary>

`dangerouslySetInnerHTML` 直接將 `item.html` 插入 DOM。若後端在儲存評論時未對 HTML 進行嚴格消毒（例如允許 `<script>` 或事件屬性），攻擊者可在評論中注入惡意腳本，當管理員查看評論列表時觸發 XSS。

**失敗情境**：攻擊者提交包含 `<img src=x onerror=alert(document.cookie)>` 的評論，若後端未移除 `onerror` 屬性，管理員開啟評論列表時即會執行腳本。

**建議**：確認後端在儲存評論時已使用如 DOMPurify 等函式庫進行消毒，並在前端渲染前再次消毒；或改用 React 的安全渲染方式（如將 HTML 轉為純文字或使用受信任的 sanitizer）。

**判斷依據**：diff 中新增的 CommentContent 元件使用 dangerouslySetInnerHTML 渲染 item.html，且未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:88</code> [R19] 缺少分號</summary>

`const contentRef = useRef<HTMLDivElement>(null)` 和 `const [isClamped, setIsClamped] = useState(false)` 等陳述式結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:112</code> [R18] 使用雙引號字串</summary>

`className={`prose flex-1 text-base leading-[1.45em] ${isExpanded ? '-mb-1 [&_p]:mb-[0.85em]' : 'line-clamp-2 [&_*]:m-0 [&_*]:inline'} ${item.status === 'hidden' && 'text-muted-foreground'}`}` 中的字串使用雙引號，違反專案規範 R18（應使用單引號）。

**判斷依據**：diff 中新增的 className 屬性值使用雙引號包覆字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> CommentContent 的截斷偵測不會在內容變更時重新執行</summary>

`useEffect` 的依賴陣列為空，只在掛載時執行一次。若 `item.html` 因資料更新而改變（例如從 API 重新取得），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。

**失敗情境**：評論內容原本超過兩行，顯示「Show more」；之後內容被更新為較短文字，但按鈕仍存在，點擊後無任何效果。

**建議**：將 `item.html` 加入依賴陣列，或使用 `useLayoutEffect` 確保在 DOM 更新後同步計算。

**判斷依據**：useEffect 依賴陣列為空，但內部使用了 item.html（透過 ref 間接依賴），當 item.html 改變時不會重新執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> [R12] JSX props 順序不符合規範</summary>

`dangerouslySetInnerHTML` 應在 `ref` 之前，且 `className` 應在 `dangerouslySetInnerHTML` 之前。目前順序為 `dangerouslySetInnerHTML`、`ref`、`className`，違反專案規範 R12（reserved props 先，再 regular props 字母序）。

**判斷依據**：diff 中新增的 div 元素 props 順序為 dangerouslySetInnerHTML、ref、className，不符合 R12 規定的 reserved props 先、regular props 字母序。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11314 (cache hit 11264) ｜ completion tokens 1669 ｜ PR #4</sub>