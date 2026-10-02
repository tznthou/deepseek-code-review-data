<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個表格中的 badge 顯示邏輯抽成共用的 LimitedBadges 元件，並在 UserListTable 中套用，同時進行了型別強化與程式碼整理。主要風險在於 LimitedBadges 的 hover 行為在桌面端可能造成 Popover 閃爍或無法點擊內容，且鍵盤可及性不足；此外，屬性欄位將權重與群組標記合併為單一 badge，可能影響視覺清晰度。建議先修正 hover 互動與可及性問題，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:72` | Popover 在桌面端 hover 時可能閃爍或無法點擊內容 | 0.80 |
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:72` | 鍵盤使用者無法操作 Popover | 0.75 |
| 🔸 | Minor | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 合併權重與群組標記，可能影響可讀性 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:69` | Badge 的 key 使用 label，可能因重複而導致 React 警告 | 0.65 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:69` | Badge 的 onClick 可能導致非互動元素可點擊 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:72</code> Popover 在桌面端 hover 時可能閃爍或無法點擊內容</summary>

在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

**判斷依據**：diff 中 PopoverTrigger 的 Button 和 PopoverContent 都設定了 onMouseEnter/onMouseLeave，但未見延遲或 hover intent 處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:72</code> 鍵盤使用者無法操作 Popover</summary>

Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

**判斷依據**：diff 中 PopoverTrigger 的 Button 沒有 onClick 或 onKeyDown 處理，PopoverContent 內的 span 沒有 tabIndex 或 role。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 合併權重與群組標記，可能影響可讀性</summary>

原本權重以獨立 badge 顯示，現在合併到 label 中，例如 'Value 80% (group)'，可能讓使用者難以快速區分權重與群組狀態。建議保留分離的 badge 或使用更明確的視覺區分。

**判斷依據**：diff 中將原本的兩個 badge 合併為單一 label，且 groupIndicator 以文字 '(group)' 呈現。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:69</code> Badge 的 key 使用 label，可能因重複而導致 React 警告</summary>

visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

**判斷依據**：diff 中 key={item.label}，但 items 可能包含相同 label。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:69</code> Badge 的 onClick 可能導致非互動元素可點擊</summary>

Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

**判斷依據**：diff 中 Badge 傳入 onClick，但 Badge 可能不是可點擊元素。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8320 (cache hit 1536) ｜ completion tokens 1173 ｜ PR #8</sub>