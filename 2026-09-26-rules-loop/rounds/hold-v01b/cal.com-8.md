<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 UserListTable 中的多個 Badge 列表改為使用新的 LimitedBadges 元件，以限制顯示數量並提供 hover/click popover 顯示其餘項目。主要風險在於 LimitedBadges 的 popover 互動在桌面端依賴 mouseenter/mouseleave，可能導致無法透過鍵盤操作或觸控裝置無法使用；此外，在 UserListTable 中將原本分開的權重與群組標記合併為單一 label，可能造成視覺與語意上的回歸。整體而言，重構方向合理，但需修正可及性與視覺呈現問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:68` | Popover 在桌面端僅依賴 mouseenter/mouseleave，缺乏鍵盤與觸控支援 | 0.80 |
| ⚠️ | Major | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badges 的 label 合併了權重與群組標記，可能造成視覺與語意回歸 | 0.75 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:82` | PopoverContent 的 onMouseEnter/onMouseLeave 可能導致 popover 意外關閉 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:42` | items 陣列在 useMemo 依賴中可能導致不必要的重新計算 | 0.65 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:249` | 硬編碼的 " (group)" 字串未使用 i18n | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:68</code> Popover 在桌面端僅依賴 mouseenter/mouseleave，缺乏鍵盤與觸控支援</summary>

在桌面端，Popover 的開啟與關閉僅由 Button 和 PopoverContent 上的 onMouseEnter/onMouseLeave 控制。這會導致：
1. 鍵盤使用者無法聚焦到觸發按鈕並開啟 popover（除非 PopoverTrigger 本身有處理，但此處未提供）。
2. 觸控裝置（如平板）沒有 hover 事件，使用者可能無法查看隱藏的 badges。
建議使用 Popover 的 trigger 屬性（如 click）或確保 Button 可聚焦並處理鍵盤事件，或提供明確的點擊切換。

**判斷依據**：在 LimitedBadges 元件中，PopoverTrigger 內的 Button 僅設置了 onMouseEnter 和 onMouseLeave，沒有 onClick 或鍵盤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badges 的 label 合併了權重與群組標記，可能造成視覺與語意回歸</summary>

原本的實作中，權重（如 80%）會顯示在獨立的 Badge 中，且群組選項使用 orange variant 並有視覺分隔。現在將權重與群組標記直接附加到 label 字串中，例如 "Value 80% (group)"，這可能導致：
1. 權重不再有獨立的視覺樣式（如背景色），可能降低可讀性。
2. 群組標記 "(group)" 是硬編碼的英文，未使用 i18n，可能導致在地化問題。
3. 若 value 本身包含空格，label 的組合可能產生不必要的空白。
建議保留原本的雙 Badge 結構，或至少將權重與群組標記分開呈現，並使用翻譯。

**判斷依據**：在 UserListTable 的 attribute cell 中，原本的程式碼使用兩個 Badge 分別顯示 value 和 weight，且群組選項使用 orange variant；新程式碼將所有資訊合併為單一 label。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:82</code> PopoverContent 的 onMouseEnter/onMouseLeave 可能導致 popover 意外關閉</summary>

PopoverContent 上設置了 onMouseEnter={handleMouseEnter} 和 onMouseLeave={handleMouseLeave}。當滑鼠從觸發按鈕移動到 popover 內容時，會先觸發按鈕的 mouseleave（關閉 popover），然後才觸發內容的 mouseenter（重新開啟），可能造成閃爍。此外，若 popover 內容與按鈕之間有間隙，mouseleave 可能導致 popover 關閉而無法進入內容。建議使用 Popover 內建的 hover 模式或增加延遲關閉。

**判斷依據**：PopoverContent 上的事件處理與 Button 上的相同，但沒有考慮移動過程中的事件順序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:42</code> items 陣列在 useMemo 依賴中可能導致不必要的重新計算</summary>

useMemo 的依賴陣列包含 items，但 items 是從 props 傳入的陣列。如果父元件每次 render 都建立新的陣列（例如在 UserListTable 中使用 map 產生），則 useMemo 會失效，導致每次 render 都重新 slice。這可能造成效能影響，尤其是在大型表格中。建議使用 useMemo 時考慮 items 的參考穩定性，或使用 useRef 保存上一次的 items 並進行淺比較。

**判斷依據**：在 UserListTable 中，傳入 LimitedBadges 的 items 是透過 map 產生的新陣列，因此每次 render 都會不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:249</code> 硬編碼的 " (group)" 字串未使用 i18n</summary>

在合併 label 時，使用了硬編碼的 " (group)" 來表示群組選項。這可能導致在地化問題，因為其他文字都使用 t() 進行翻譯。建議使用翻譯鍵或至少使用更通用的符號。

**判斷依據**：在 UserListTable 的 attribute cell 中，直接賦值 " (group)" 給 groupIndicator。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9759 (cache hit 9728) ｜ completion tokens 1544 ｜ PR #8</sub>