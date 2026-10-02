<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 重新設計了評論管理列表的版面，將原本多欄的表格改為單一主欄位整合作者、時間、文章與內容，並新增文章特色圖片縮圖。主要風險在於 `dangerouslySetInnerHTML` 渲染未經消毒的 HTML（XSS）、`CommentContent` 的 clamp 偵測在內容動態載入時可能失效，以及 `formatDate` 的正規表達式替換可能誤刪日期中的逗號。另有部分程式碼風格問題（缺少分號、JSX props 順序）需修正。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染未消毒的 HTML 可能導致 XSS | 0.95 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | clamp 偵測僅在掛載時執行，內容動態載入時可能失效 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:88` | [R19] 缺少分號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:110` | [R12] JSX props 順序不符合標準 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:70` | formatDate 的正規表達式可能誤刪日期中的逗號 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染未消毒的 HTML 可能導致 XSS</summary>

`dangerouslySetInnerHTML={{__html: item.html || ''}}` 直接將評論內容的 HTML 注入 DOM。若評論內容未經伺服器端消毒，攻擊者可提交包含 `<script>` 或事件處理器的惡意 HTML，當管理員查看評論列表時觸發 XSS。

建議：使用 DOMPurify 等函式庫在渲染前消毒 HTML，或確認後端已對 `item.html` 進行嚴格的白名單消毒。

**判斷依據**：diff 中新增的 `CommentContent` 元件直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`，且未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> clamp 偵測僅在掛載時執行，內容動態載入時可能失效</summary>

`useEffect` 僅在元件掛載時執行一次 `checkIfClamped`，並監聽 window resize。但評論內容可能因虛擬滾動或非同步載入而在掛載後才更新，導致 `scrollHeight` 與 `clientHeight` 的比較不準確，`isClamped` 狀態可能錯誤，使「Show more」按鈕不出現或在不該出現時出現。

建議：使用 `ResizeObserver` 監聽 `contentRef` 的大小變化，或在內容更新時重新檢查。

**判斷依據**：依賴陣列為空 `[]`，僅在掛載時執行；且未監聽內容變化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:88</code> [R19] 缺少分號</summary>

`const contentRef = useRef<HTMLDivElement>(null)` 和 `const [isClamped, setIsClamped] = useState(false)` 等陳述句結尾缺少分號，違反專案規範 R19。

**判斷依據**：diff 中新增的程式碼行末未加分號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> [R12] JSX props 順序不符合標準</summary>

`dangerouslySetInnerHTML` 應置於 `ref` 之前，且 `className` 應在 `dangerouslySetInnerHTML` 之前。目前順序為 `dangerouslySetInnerHTML`、`ref`、`className`，違反專案規範 R12。

**判斷依據**：diff 中該元素的 props 順序與規範要求的字母順序不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:70</code> formatDate 的正規表達式可能誤刪日期中的逗號</summary>

`formatted.replace(/(\d+),(\s+\d{4})/, '$1$2')` 意圖移除「Dec 17, 2025」中的逗號，但若日期格式因 locale 或瀏覽器差異而不同（例如「17 Dec, 2025」或「Dec 17, 2025, 10:30 AM」），可能無法正確匹配或誤刪其他逗號。

建議：使用更精確的格式化方式，例如 `Intl.DateTimeFormat` 的選項組合，或直接使用 `formatTimestamp` 函式。

**判斷依據**：正規表達式假設數字後緊接逗號和四位數年份，但實際格式可能因 locale 而異。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11314 (cache hit 8960) ｜ completion tokens 1507 ｜ PR #4</sub>