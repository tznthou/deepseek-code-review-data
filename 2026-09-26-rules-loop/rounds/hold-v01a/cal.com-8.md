<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 將原本在 ResponseValueCell 和 UserListTable 中重複的 badge 顯示邏輯抽成共用的 LimitedBadges 元件，並在 UserListTable 中套用。主要風險在於 LimitedBadges 的 hover/click 互動在行動裝置上可能無法正常運作，且鍵盤可及性不足；此外，在 UserListTable 中將原本分開的權重與群組標示合併成單一 badge，可能造成視覺混淆。建議優先修正 LimitedBadges 的互動邏輯與可及性，並確認合併 badge 的設計是否符合預期。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:73` | 行動裝置上 Popover 可能無法透過點擊開啟 | 0.80 |
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:73` | 鍵盤使用者無法操作 Popover | 0.75 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 合併權重與群組標示可能造成視覺混淆 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:42` | items 陣列變動時 Popover 狀態未重置 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:73</code> 行動裝置上 Popover 可能無法透過點擊開啟</summary>

在行動裝置上（isMobile 為 true），handleMouseEnter 和 handleMouseLeave 都不會觸發 setIsOpen，因此 Popover 只能透過點擊觸發。但 PopoverTrigger 包著一個 Button，點擊 Button 時會觸發 Popover 的 onOpenChange，但因為沒有阻止預設行為，可能導致按鈕的點擊事件與 Popover 的開啟邏輯衝突。此外，PopoverContent 上的 onMouseEnter/onMouseLeave 在行動裝置上也不會觸發，因此點擊外部關閉後，再次點擊按鈕可能無法重新開啟。建議在行動裝置上使用 click 事件來控制 Popover，並確保 PopoverTrigger 的點擊行為正確。

**判斷依據**：handleMouseEnter 和 handleMouseLeave 在 isMobile 為 true 時直接 return，不會改變 isOpen 狀態。Popover 的 open 屬性由 isOpen 控制，因此行動裝置上只能依賴 PopoverTrigger 的點擊來觸發 onOpenChange。但 PopoverTrigger 包著 Button，Button 的點擊事件可能與 Popover 的開啟邏輯衝突，導致無法正常開啟。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:73</code> 鍵盤使用者無法操作 Popover</summary>

PopoverTrigger 包著 Button，但 Button 沒有設定 onClick 處理常式，而是依賴 Popover 的 onOpenChange。鍵盤使用者聚焦到 Button 後按 Enter 或 Space 會觸發 Button 的點擊事件，但 Popover 可能不會因此開啟，因為 PopoverTrigger 的 asChild 會將事件處理器傳遞給 Button，但 Button 本身沒有 onClick，可能導致事件無法正確觸發 Popover 的開啟。建議明確設定 Button 的 onClick 來切換 isOpen，或確保 PopoverTrigger 的事件處理能正確傳遞。

**判斷依據**：Button 沒有 onClick 屬性，僅依賴 PopoverTrigger 的 asChild 傳遞事件。鍵盤操作時，Button 的點擊事件可能不會觸發 Popover 的開啟，導致鍵盤使用者無法存取隱藏的 badges。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 合併權重與群組標示可能造成視覺混淆</summary>

原本的實作中，權重（如 80%）和群組標示（如 (group)）是分開的 badge，現在合併成單一 label，例如「Value 80% (group)」。這可能讓使用者難以快速區分權重和群組狀態，且如果 label 過長，在有限的空間中可能被截斷。建議保留原本的分開顯示方式，或提供更清楚的視覺區隔。

**判斷依據**：原本的程式碼將權重和群組標示分別顯示在不同的 Badge 中，現在合併成一個字串。這可能影響可讀性，特別是在權重和群組標示同時存在時。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:42</code> items 陣列變動時 Popover 狀態未重置</summary>

當 items 陣列變動（例如從有 hidden items 變成沒有）時，isOpen 狀態可能保持 true，導致 Popover 在沒有 hidden items 時仍然顯示。雖然元件在 items.length === 0 時會回傳 null，但當 hiddenItems 從有變無時，Popover 可能仍然開啟。建議在 items 或 hiddenItems 變化時重置 isOpen。

**判斷依據**：isOpen 狀態沒有在 items 或 hiddenItems 變化時重置，可能導致 Popover 在沒有 hidden items 時仍然顯示。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9759 (cache hit 8192) ｜ completion tokens 1382 ｜ PR #8</sub>