<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 UserListTable 與 ResponseValueCell 中的 badge 顯示邏輯抽成共用的 LimitedBadges 元件，並限制最多顯示 2 個 badge，其餘以 hover/click popover 呈現。整體結構合理，但存在幾個需要修正的問題：LimitedBadges 的 hover 互動在桌面端可能因 popover 與 trigger 之間的間隙而意外關閉；在 UserListTable 中，屬性 badge 的權重與群組標記被合併為單一 label，可能造成視覺混淆；此外，LimitedBadges 的 key 使用 label 可能導致重複 key 的 React 警告。建議優先處理 hover 互動與 label 合併問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:75` | Popover hover 互動可能因間隙而意外關閉 | 0.80 |
| ⚠️ | Major | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 的權重與群組標記合併為單一 label，可能造成視覺混淆 | 0.75 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:69` | 使用 label 作為 key 可能導致重複 key 警告 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:88` | hiddenItems 的 span 缺少 onClick 處理，可能導致點擊無反應 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:75</code> Popover hover 互動可能因間隙而意外關閉</summary>

在桌面端，Popover 的開啟與關閉依賴於 trigger 與 content 的 onMouseEnter/onMouseLeave。然而，PopoverContent 與 trigger 之間可能存在視覺間隙（例如 margin 或定位偏移），當滑鼠移動到間隙時，會觸發 mouseleave 而關閉 popover，導致使用者無法將滑鼠移至內容上。建議使用 Radix Popover 的內建 hover 支援（如 `openOnHover` 或 `hoverable` 屬性），或加入延遲關閉機制。

**判斷依據**：LimitedBadges.tsx 第 75-76 行，trigger 的 onMouseEnter/onMouseLeave 直接控制 isOpen，但未處理間隙問題。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 的權重與群組標記合併為單一 label，可能造成視覺混淆</summary>

原本的實作將權重顯示為獨立的 badge（帶有不同背景色），並以橘色 badge 表示群組選項。現在將權重與群組標記直接附加在 label 文字中（例如 "選項 80% (group)"），可能讓使用者難以快速區分權重與群組狀態，且喪失了原有的視覺提示。建議保留原有的雙 badge 設計，或至少將權重以不同樣式呈現。

**判斷依據**：UserListTable.tsx 第 260-262 行，將 weight 與 groupIndicator 直接串接至 label。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:69</code> 使用 label 作為 key 可能導致重複 key 警告</summary>

在 visibleItems 與 hiddenItems 的 map 中，使用 item.label 作為 key。如果兩個 badge 具有相同的 label（例如多個團隊同名或屬性值相同），React 會發出重複 key 的警告，並可能導致渲染錯誤。建議使用更穩定的唯一識別碼（如 id 或 index 與 label 的組合）。

**判斷依據**：LimitedBadges.tsx 第 58 行，key={item.label}。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:88</code> hiddenItems 的 span 缺少 onClick 處理，可能導致點擊無反應</summary>

在 popover 中，hiddenItems 的 span 元素沒有 onClick 處理，但 BadgeItem 型別允許 onClick。如果未來傳入具有 onClick 的項目，點擊將不會觸發任何動作。建議為 span 加上 onClick={item.onClick}，或明確限制此處不支援點擊。

**判斷依據**：LimitedBadges.tsx 第 88-92 行，span 未綁定 onClick。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12659 (cache hit 12544) ｜ completion tokens 1133 ｜ PR #8</sub>