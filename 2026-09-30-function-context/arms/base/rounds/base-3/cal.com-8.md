<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個表格中的 badge 顯示改為使用新的 LimitedBadges 元件，限制最多顯示 2 個 badge，其餘以 hover/click popover 呈現。主要風險在於新元件中 hover 與 click 的互動可能導致 popover 無法正常關閉，以及將原本分開的 badge 合併為單一 label 後可能造成資訊遺失或樣式不一致。建議優先修正 popover 的互動邏輯，並確認合併 label 的顯示方式符合產品需求。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:69` | Popover 的 hover 與 click 互動可能導致無法關閉 | 0.80 |
| ⚠️ | Major | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 合併 label 可能造成資訊遺失 | 0.75 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:44` | maxVisible 未限制最小值，可能導致顯示異常 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:72` | Popover 內容的 hover 處理可能造成閃爍 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:69</code> Popover 的 hover 與 click 互動可能導致無法關閉</summary>

在桌面端，Popover 的開啟由 onMouseEnter 觸發，關閉由 onMouseLeave 觸發。但 Popover 本身也受 onOpenChange 控制，當使用者點擊 trigger 按鈕時，Popover 會切換 open 狀態，但 mouse enter/leave 事件可能不會如預期觸發，導致 popover 卡在開啟狀態。建議移除自訂的 mouse enter/leave 處理，改用 Popover 內建的 hover 模式（例如設定 trigger="hover"），或明確處理 click 與 hover 的狀態轉換。

**判斷依據**：在 LimitedBadges.tsx 中，PopoverTrigger 的 Button 同時設定了 onMouseEnter 和 onMouseLeave，而 Popover 的 open 狀態由 isOpen state 控制，且 Popover 有 onOpenChange={setIsOpen}。當使用者點擊按鈕時，會觸發 onOpenChange 切換狀態，但 mouse enter/leave 事件可能不會再次觸發，導致狀態不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 合併 label 可能造成資訊遺失</summary>

原本屬性值與權重是分開的兩個 badge，現在合併成單一 label，例如原本顯示為 [屬性值] [權重%]，現在變成 [屬性值 權重%]。這可能導致使用者難以區分屬性值和權重，且若屬性值本身包含空格，合併後的字串可能造成混淆。建議保留原本的分開顯示方式，或在 LimitedBadges 中支援多個 badge 的組合。

**判斷依據**：在 UserListTable.tsx 的 generateAttributeColumns 中，原本的程式碼使用兩個 Badge 分別顯示 attributeValue.value 和 suffix（權重），現在改為將兩者合併成單一 label 傳入 LimitedBadges。這改變了視覺呈現，可能影響使用者對資料的理解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:44</code> maxVisible 未限制最小值，可能導致顯示異常</summary>

maxVisible 是外部傳入的 prop，若傳入負數或 0，visibleItems 會是空陣列，而 hiddenItems 會包含所有項目，導致只顯示 +N 的 badge，但點開 popover 後所有項目都在隱藏區。建議加上 maxVisible 的最小值限制（例如 Math.max(1, maxVisible)）。

**判斷依據**：在 LimitedBadges.tsx 中，maxVisible 沒有被驗證，直接使用 slice。若呼叫端傳入 0 或負數，會造成顯示邏輯錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:72</code> Popover 內容的 hover 處理可能造成閃爍</summary>

PopoverContent 上也設定了 onMouseEnter 和 onMouseLeave，當滑鼠從 trigger 移動到 popover 內容時，可能會因為 mouseleave 觸發關閉，然後 mouseenter 又開啟，造成閃爍。建議使用 Popover 的 hover 模式或設定適當的 delay。

**判斷依據**：在 LimitedBadges.tsx 中，PopoverContent 上設定了與 trigger 相同的 mouse enter/leave 處理，但沒有考慮到從 trigger 移動到 content 的過渡，可能導致 popover 關閉後又立即開啟。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8320 (cache hit 8192) ｜ completion tokens 1210 ｜ PR #8</sub>