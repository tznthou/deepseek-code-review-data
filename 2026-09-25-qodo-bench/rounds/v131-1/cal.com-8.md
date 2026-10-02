<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 UserListTable 中的多個 Badge 顯示邏輯抽換為新的 LimitedBadges 元件，並在 ResponseValueCell 中重複使用。主要風險在於 LimitedBadges 的 Popover 互動可能導致點擊事件無法觸發、鍵盤可訪問性不足，以及 label 拼接方式可能造成顯示問題。整體而言，重構方向合理，但需修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:73` | Popover 的 hover 觸發可能導致點擊事件無法觸發 | 0.85 |
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:76` | Popover 觸發按鈕缺少鍵盤可訪問性 | 0.80 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 的 label 拼接可能導致顯示問題 | 0.70 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:389` | teams 欄位的 LimitedBadges 可能遺失點擊過濾功能 | 0.65 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:518` | useMemo 依賴陣列缺少 dispatch 和 tablePermissions | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:73</code> Popover 的 hover 觸發可能導致點擊事件無法觸發</summary>

在桌面端，Popover 的開啟依賴於 onMouseEnter 和 onMouseLeave。當使用者將滑鼠移到觸發按鈕上時，Popover 會開啟，但當滑鼠移入 PopoverContent 時，由於 onMouseLeave 觸發，Popover 會立即關閉，導致使用者無法點擊隱藏項目。這是因為 PopoverContent 的 onMouseEnter 和 onMouseLeave 雖然有設定，但可能因為事件傳遞或元件結構問題而無法正確維持開啟狀態。建議改用 Radix Popover 的 hover 模式或使用延遲關閉機制，確保滑鼠在 PopoverContent 上時不會關閉。

**判斷依據**：LimitedBadges.tsx 第 73-74 行，PopoverTrigger 上的 onMouseEnter/onMouseLeave 處理，但 PopoverContent 上的相同處理可能無法阻止關閉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:76</code> Popover 觸發按鈕缺少鍵盤可訪問性</summary>

PopoverTrigger 使用 Button 元件，但未設定 onClick 或 keyboard 事件來開啟 Popover。依賴 hover 的互動方式對鍵盤使用者不友善，且可能無法透過 Tab 鍵聚焦並開啟。建議加入 onClick 處理，或使用 Popover 的 trigger 屬性設定為 click 或 both。

**判斷依據**：LimitedBadges.tsx 第 76-81 行，Button 僅有 onMouseEnter/onMouseLeave，無 onClick 或鍵盤事件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 的 label 拼接可能導致顯示問題</summary>

在 generateAttributeColumns 中，label 由 attributeValue.value、weight 和 groupIndicator 拼接而成，例如 "value 100% (group)"。這可能導致顯示不美觀，且若 value 本身包含空格或特殊字元，可能造成誤解。建議使用更結構化的方式呈現，例如在 Badge 內使用多個元素或 tooltip。

**判斷依據**：UserListTable.tsx 第 250-252 行，label 拼接邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:389</code> teams 欄位的 LimitedBadges 可能遺失點擊過濾功能</summary>

原本 teams 的 Badge 有 onClick 來設定過濾條件，現在改為 LimitedBadges 的 items 中傳入 onClick。但 LimitedBadges 的 Badge 元件是否有正確傳遞 onClick？在 LimitedBadges 中，Badge 的 onClick 是直接傳入的，但若 Badge 元件不支援 onClick，則功能會失效。需確認 Badge 元件的 props 是否包含 onClick。

**判斷依據**：UserListTable.tsx 第 382-384 行，onClick 傳入 items。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:518</code> useMemo 依賴陣列缺少 dispatch 和 tablePermissions</summary>

在 useMemo 的依賴陣列中，未包含 dispatch 和 tablePermissions。雖然 dispatch 是穩定的，但 tablePermissions 可能來自 props 或 state，若其值改變，columns 不會重新生成，可能導致權限相關的 cell 內容過時。建議將 tablePermissions 加入依賴陣列。

**判斷依據**：UserListTable.tsx 第 515 行，依賴陣列缺少 tablePermissions。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8284 (cache hit 1408) ｜ completion tokens 1354 ｜ PR #8</sub>