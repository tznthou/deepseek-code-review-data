<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 UserListTable 與 ResponseValueCell 中的 badge 顯示邏輯抽成共用的 LimitedBadges 元件，並加入 hover/click popover 來顯示超過上限的項目。整體方向合理，但存在幾個需要修正的問題：LimitedBadges 的 popover 在桌面端僅靠 hover 觸發，可能導致無法點擊隱藏項目；在 UserListTable 的屬性欄位中，原本分開的權重與群組標記被合併成單一 label，可能造成視覺與可讀性回歸；此外，部分型別與可存取性細節需要調整。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/components/ui/LimitedBadges.tsx:73` | Popover 僅靠 hover 觸發，桌面端無法點擊隱藏項目 | 0.85 |
| ⚠️ | Major | `apps/web/modules/users/components/UserTable/UserListTable.tsx:251` | 屬性 badge 的權重與群組標記合併，可能造成視覺回歸 | 0.80 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:82` | Popover 內容中的項目缺少點擊處理 | 0.70 |
| 🔸 | Minor | `apps/web/components/ui/LimitedBadges.tsx:79` | Popover 觸發按鈕缺少可存取性屬性 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/ui/LimitedBadges.tsx:73</code> Popover 僅靠 hover 觸發，桌面端無法點擊隱藏項目</summary>

在桌面端，Popover 的開啟與關閉完全依賴 onMouseEnter/onMouseLeave。當使用者將滑鼠移入觸發按鈕時，popover 會開啟，但當滑鼠移向 popover 內容時，因為 popover 與按鈕之間可能存在間隙，或 popover 本身沒有正確處理 hover 狀態，可能導致 popover 關閉，使用者無法點擊其中的項目。建議改用 click 觸發，或確保 popover 與觸發按鈕之間沒有間隙，並在 popover 上維持 hover 狀態。

**判斷依據**：LimitedBadges.tsx 第 73-74 行，PopoverTrigger 上的 onMouseEnter/onMouseLeave 處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/users/components/UserTable/UserListTable.tsx:251</code> 屬性 badge 的權重與群組標記合併，可能造成視覺回歸</summary>

原本的實作中，權重（如 80%）會顯示在獨立的 badge 中，且群組選項會以橘色 badge 顯示。新的實作將權重與群組標記直接附加在 label 文字中，例如「選項 80% (group)」，這可能導致視覺擁擠，且權重不再有獨立的背景色，可能影響使用者對權重的辨識。建議保留原本的雙 badge 設計，或提供選項讓權重以獨立樣式呈現。

**判斷依據**：UserListTable.tsx 第 246-248 行，將 weight 與 groupIndicator 直接串接至 label。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:82</code> Popover 內容中的項目缺少點擊處理</summary>

在 LimitedBadges 元件中，隱藏項目僅以 span 呈現，沒有 onClick 處理。雖然 BadgeItem 型別有 onClick 屬性，但此處並未使用。若未來需要讓隱藏項目可點擊（例如在 UserListTable 的 teams 欄位中，點擊團隊名稱應觸發篩選），則此處需要加上 onClick 處理。

**判斷依據**：LimitedBadges.tsx 第 82-86 行，隱藏項目僅為 span，無 onClick。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/components/ui/LimitedBadges.tsx:79</code> Popover 觸發按鈕缺少可存取性屬性</summary>

PopoverTrigger 內的 Button 僅有 aria-label，但未設定 aria-haspopup 或 aria-expanded，可能影響螢幕閱讀器使用者。建議加上 aria-haspopup="dialog" 與動態的 aria-expanded。

**判斷依據**：LimitedBadges.tsx 第 68 行，僅有 aria-label。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8284 (cache hit 8192) ｜ completion tokens 1106 ｜ PR #8</sub>