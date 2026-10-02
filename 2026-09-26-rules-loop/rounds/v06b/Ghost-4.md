<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了管理後台的留言審核清單版面，將原本的多欄表格改為單一主欄位整合作者、文章、時間與內容，並在後端 API 的 post 物件中新增 feature_image 欄位以顯示文章縮圖。主要風險在於前端使用 dangerouslySetInnerHTML 渲染留言內容，若後端未完整消毒，可能造成 XSS；此外，CommentContent 元件在內容變更時不會重新計算是否被截斷，可能導致「Show more」按鈕顯示不正確。整體程式碼結構尚可，但需優先處理 XSS 風險與 clamp 偵測的相依性問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染留言內容可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | CommentContent 的 clamp 偵測未依賴 item.html，內容變更時不會重新計算 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:70` | 使用正規表達式移除日期中的逗號可能因 locale 而失效 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染留言內容可能導致 XSS</summary>

此處直接將 `item.html` 以 `dangerouslySetInnerHTML` 插入 DOM。若後端在產生 `item.html` 時未對使用者輸入進行完整的 HTML 消毒（例如移除 `<script>`、事件處理器、`javascript:` URL 等），攻擊者可在留言中注入惡意腳本，當管理員查看留言時觸發 XSS。

**失敗情境**：攻擊者提交包含 `<img src=x onerror=alert(document.cookie)>` 的留言，若後端未過濾，管理員開啟留言清單時即會執行攻擊者腳本。

**建議**：確認後端在儲存留言時已使用如 DOMPurify 等函式庫進行嚴格消毒，並在前端渲染前再次消毒；或改用 React 的安全方式渲染（如將 HTML 轉為純文字或使用受信任的 sanitizer）。

**判斷依據**：diff 中新增的 CommentContent 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`，且未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> CommentContent 的 clamp 偵測未依賴 item.html，內容變更時不會重新計算</summary>

`useEffect` 的依賴陣列為空 `[]`，僅在元件掛載時執行一次 `checkIfClamped`。若 `item.html` 在掛載後發生變化（例如從 API 延遲載入或更新），`isClamped` 不會重新計算，導致「Show more」按鈕可能錯誤顯示或隱藏。

**失敗情境**：留言內容初始為空，之後才載入完整 HTML，此時 `scrollHeight` 可能仍為 0，`isClamped` 保持 false，使用者無法展開被截斷的內容。

**建議**：將 `item.html` 加入依賴陣列，或使用 `useLayoutEffect` 並在內容變更時重新檢查。

**判斷依據**：diff 中 `useEffect` 的依賴陣列為空，且 `item.html` 未列入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:70</code> 使用正規表達式移除日期中的逗號可能因 locale 而失效</summary>

`formatDate` 函式使用 `formatted.replace(/(\d+),(\s+\d{4})/, '$1$2')` 移除日期中的逗號。此正規表達式假設日期格式為「月 日, 年」，但 `Intl.DateTimeFormat` 的輸出會因執行環境的 locale 而異。雖然目前指定 `'en-US'`，但若未來變更 locale 或瀏覽器實作不同，可能無法正確移除逗號，導致顯示不一致。

**失敗情境**：在某些環境中，日期格式可能為「2025 Dec 17」或「17 Dec 2025」，正規表達式無法匹配，逗號仍會保留。

**建議**：使用 `Intl.DateTimeFormat` 的選項（如 `year: 'numeric'` 與 `month: 'short'` 的組合）直接產生無逗號格式，或使用更精確的字串處理。

**判斷依據**：diff 中新增的 `formatDate` 函式使用正規表達式移除逗號，依賴特定 locale 格式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11294 (cache hit 11264) ｜ completion tokens 1278 ｜ PR #4</sub>