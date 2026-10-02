<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 UserListTable 中原本以 HoverCard 顯示的 badges 重構為新的 LimitedBadges 元件，並套用於 teams、attributes 與 insights 的 ResponseValueCell。主要風險在於 LimitedBadges 的 hover 互動在觸控裝置上可能無法開啟 popover，且鍵盤無障礙操作不足；此外，attributes 的顯示格式從原本的權重與群組視覺區分改為純文字，可能降低可讀性。整體程式碼結構清晰，但建議補強無障礙與互動細節。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:50` | Popover 在觸控裝置上無法透過 hover 開啟 | 0.80 |
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:75` | Popover 內容無法透過鍵盤操作 | 0.75 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:243` | Attributes 的權重與群組標示改為純文字，降低可讀性 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:85` | Popover 內容的滑鼠離開處理可能導致閃爍 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:50</code> Popover 在觸控裝置上無法透過 hover 開啟</summary>

LimitedBadges 的 Popover 僅透過 onMouseEnter/onMouseLeave 控制開啟，且 handleMouseEnter 在 isMobile 為 true 時直接 return，因此觸控裝置（如手機、平板）的使用者無法看到隱藏的 badges。建議改為點擊觸發（例如使用 PopoverTrigger 的 onClick），或提供明確的點擊目標。

**判斷依據**：在 LimitedBadges.tsx 中，handleMouseEnter 與 handleMouseLeave 皆檢查 isMobile，若為 true 則不改變 isOpen 狀態，導致 popover 無法開啟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:75</code> Popover 內容無法透過鍵盤操作</summary>

PopoverTrigger 使用 Button 元件，但未提供 onKeyDown 或 focus 管理，鍵盤使用者無法開啟或瀏覽 popover 內容。建議加入適當的鍵盤事件處理（例如 Enter/Space 開啟、Escape 關閉），並確保焦點能移至 popover 內。

**判斷依據**：Button 僅綁定滑鼠事件，未見任何鍵盤處理，可能違反無障礙規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:243</code> Attributes 的權重與群組標示改為純文字，降低可讀性</summary>

原本 attributes 的顯示會將權重以獨立 Badge 呈現，並以顏色區分群組選項；現在改為在 label 中附加權重與 "(group)" 文字，可能讓使用者難以快速辨識。建議保留原本的視覺區分，或提供更明確的格式。

**判斷依據**：在 UserListTable.tsx 的 generateAttributeColumns 中，原本的 Badge 結構被替換為單一 label 字串，失去視覺層次。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:85</code> Popover 內容的滑鼠離開處理可能導致閃爍</summary>

PopoverContent 的 onMouseLeave 直接關閉 popover，但若滑鼠在 trigger 與 content 之間移動時，可能因事件順序造成 popover 意外關閉。建議加入延遲關閉或使用 hover intent 邏輯。

**判斷依據**：PopoverContent 與 PopoverTrigger 各自綁定 mouse enter/leave，未見任何延遲或緩衝機制。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12659 (cache hit 1536) ｜ completion tokens 1171 ｜ PR #8</sub>