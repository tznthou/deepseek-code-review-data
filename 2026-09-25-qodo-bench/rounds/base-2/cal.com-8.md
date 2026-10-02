<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個表格中的 badge 顯示邏輯抽成共用的 LimitedBadges 元件，並在 UserListTable 中套用，同時進行型別標註與程式碼整理。主要風險在於 LimitedBadges 的 hover 互動在桌面端可能造成 Popover 閃爍或無法點擊內容，且鍵盤無障礙性不足；此外，在 UserListTable 中將原本分開的權重與群組標記合併為單一 badge，可能影響視覺清晰度。建議先處理 hover 互動與無障礙問題，再考慮合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:73` | Popover 在桌面端 hover 時可能閃爍或無法點擊內容 | 0.80 |
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:79` | Popover 缺乏鍵盤無障礙支援 | 0.75 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 合併權重與群組標記可能降低可讀性 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:44` | maxVisible 為 0 或負數時行為未定義 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:73</code> Popover 在桌面端 hover 時可能閃爍或無法點擊內容</summary>

在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

**判斷依據**：diff 中 PopoverTrigger 和 PopoverContent 都設定了 onMouseEnter/onMouseLeave，但未見延遲或 hover intent 處理，可能導致間隙問題。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:79</code> Popover 缺乏鍵盤無障礙支援</summary>

觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

**判斷依據**：diff 中僅有 aria-label，未見 onClick 或 onKeyDown 處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 合併權重與群組標記可能降低可讀性</summary>

原本權重以獨立 badge 顯示，群組以橘色 badge 區分，現在合併為單一 label（例如 "Value 80% (group)"），可能讓使用者難以快速區分。建議保留視覺區分，或提供 tooltip 說明。

**判斷依據**：diff 中將原本分開的 Badge 合併為單一 label 字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:44</code> maxVisible 為 0 或負數時行為未定義</summary>

若 maxVisible 傳入 0 或負數，visibleItems 會是空陣列，hiddenItems 會包含所有項目，但 UI 仍會顯示 +N 按鈕，可能造成困惑。建議加上 prop 驗證或限制最小值為 1。

**判斷依據**：diff 中未對 maxVisible 做任何檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8320 (cache hit 8192) ｜ completion tokens 1143 ｜ PR #8</sub>