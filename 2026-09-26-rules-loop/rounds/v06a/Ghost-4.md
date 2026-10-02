<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了評論管理清單的版面，將原本的多欄表格改為單一主欄位，整合作者、文章、時間等資訊，並加入文章特色圖片、回覆/喜歡/檢舉計數，以及可展開的評論內容。主要風險在於：1) 使用 dangerouslySetInnerHTML 渲染評論 HTML，若後端未徹底消毒，可能造成 XSS；2) 新增的 feature_image 欄位直接以 <img> 顯示，若來源不可信可能造成追蹤或內容注入；3) 部分程式碼違反專案規範（如缺少分號、JSX prop 順序、按鈕 type 屬性）。整體而言，功能改動合理，但需先處理安全性與規範問題。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:355` | 文章特色圖片來源未驗證，可能造成追蹤或內容注入 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:88` | [R19] 缺少分號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:89` | [R19] 缺少分號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:90` | [R19] 缺少分號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:102` | [R13] Button 缺少 type 屬性 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:203` | [R13] Button 缺少 type 屬性 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:233` | [R13] Button 缺少 type 屬性 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:264` | [R12] JSX props 順序不符合標準 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:270` | [R12] JSX props 順序不符合標準 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`。若評論內容未經徹底消毒（例如後端僅做基本過濾），攻擊者可能注入 `<script>` 或事件處理器，造成儲存型 XSS。

失敗情境：攻擊者提交包含 `<img src=x onerror=alert(document.cookie)>` 的評論，管理員在後台查看評論時觸發。

建議：確認後端在儲存評論時已使用嚴格的 HTML sanitizer（如 DOMPurify）移除所有危險標籤與屬性；若無法保證，應在前端渲染前進行消毒，或改用安全的渲染方式（如純文字或 React 元件）。

**判斷依據**：diff 中新增的 CommentContent 元件使用 dangerouslySetInnerHTML 直接輸出 item.html，且未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:355</code> 文章特色圖片來源未驗證，可能造成追蹤或內容注入</summary>

新增的 `<img>` 直接使用 `item.post.feature_image` 作為 src。若該 URL 由使用者控制（例如文章作者可設定任意圖片 URL），管理員查看評論時會載入該圖片，可能洩漏管理員 IP、User-Agent 等資訊，或利用圖片 URL 進行 CSRF 攻擊。

失敗情境：惡意作者將文章特色圖片設為 `http://attacker.com/track?admin=1`，管理員查看評論時瀏覽器請求該 URL，洩漏管理員資訊。

建議：限制圖片來源為同源或受信任的網域，或使用代理伺服器載入圖片；若無法限制，至少加入 `referrerPolicy="no-referrer"` 並考慮使用 `loading="lazy"`。

**判斷依據**：diff 中新增的 img 標籤直接使用 item.post.feature_image，無任何來源驗證或安全屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:88</code> [R19] 缺少分號</summary>

此處 `const contentRef = useRef<HTMLDivElement>(null)` 缺少結尾分號，違反專案規範 R19（Code Must Always Use Semicolons）。

建議：在行尾加上分號。

**判斷依據**：diff 中新增的該行沒有分號，與專案其他程式碼風格不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:89</code> [R19] 缺少分號</summary>

此處 `const [isClamped, setIsClamped] = useState(false)` 缺少結尾分號，違反專案規範 R19。

建議：在行尾加上分號。

**判斷依據**：diff 中新增的該行沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:90</code> [R19] 缺少分號</summary>

此處 `const [isExpanded, setIsExpanded] = useState(false)` 缺少結尾分號，違反專案規範 R19。

建議：在行尾加上分號。

**判斷依據**：diff 中新增的該行沒有分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:102</code> [R13] Button 缺少 type 屬性</summary>

此處 `<Button>` 元件未指定 `type` 屬性。若此按鈕位於表單內，預設 type 為 submit，可能導致非預期的表單提交。

失敗情境：若未來將此按鈕放入表單中，點擊「Show more」會觸發表單提交。

建議：明確加上 `type="button"`。

**判斷依據**：diff 中新增的 ExpandButton 元件使用 Button 但未指定 type。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:203</code> [R13] Button 缺少 type 屬性</summary>

此處 `<Button>` 元件未指定 `type` 屬性，可能導致非預期的表單提交行為。

建議：明確加上 `type="button"`。

**判斷依據**：diff 中新增的作者按鈕未指定 type。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:233</code> [R13] Button 缺少 type 屬性</summary>

此處 `<Button>` 元件未指定 `type` 屬性，可能導致非預期的表單提交行為。

建議：明確加上 `type="button"`。

**判斷依據**：diff 中新增的文章標題按鈕未指定 type。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:264</code> [R12] JSX props 順序不符合標準</summary>

此處 `<Button>` 的 props 順序為 `className`、`size`、`variant`、`onClick`，但根據規範 R12，callbacks 應放在最後，且 regular props 應按字母順序排列。

建議：調整為 `className`、`size`、`variant`、`onClick` 的順序（onClick 已在最後，但 className 應在 size 之前？實際標準需參考專案設定）。

**判斷依據**：diff 中新增的 Hide 按鈕 props 順序可能不符合規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:270</code> [R12] JSX props 順序不符合標準</summary>

此處 `<Button>` 的 props 順序為 `size`、`variant`、`onClick`，但根據規範 R12，callbacks 應放在最後，且 regular props 應按字母順序排列。

建議：調整為 `size`、`variant`、`onClick` 的順序（onClick 已在最後，但 size 應在 variant 之前？實際標準需參考專案設定）。

**判斷依據**：diff 中新增的 Show 按鈕 props 順序可能不符合規範。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11294 (cache hit 8960) ｜ completion tokens 2436 ｜ PR #4</sub>