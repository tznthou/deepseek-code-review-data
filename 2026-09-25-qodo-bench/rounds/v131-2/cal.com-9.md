<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 sortHosts 函式在移動時邏輯被意外修改（priority 排序方向反轉），可能導致主持人排序錯誤。此外，部分 import 路徑改為相對路徑，增加未來維護成本，且缺少測試來驗證排序行為。建議先修正 sortHosts 邏輯並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式邏輯在移動時被意外修改 | 0.95 |
| ⚠️ | Major | `apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3` | 使用相對路徑導入跨 package 的模組 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:235` | JSX 縮排不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式邏輯在移動時被意外修改</summary>

在將 sortHosts 從 HostEditDialogs.tsx 移至 hostGroupUtils.ts 時，priority 排序方向被反轉。原程式碼在 isRRWeightsEnabled 為 true 且 weight 相等時回傳 `priorityB - priorityA`（降冪），新程式碼回傳 `priorityA - priorityB`（升冪）。這會導致主持人排序結果相反，可能影響 round-robin 或優先級分配的正確性。

建議修正為：
```ts
if (weightA === weightB) {
  return priorityB - priorityA;
}
```

**判斷依據**：diff 中新增的 sortHosts 函式內，`return priorityA - priorityB;` 與原 HostEditDialogs.tsx 中刪除的 `return priorityB - priorityA;` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/components/apps/DestinationCalendarSettingsWebWrapper.tsx:3</code> 使用相對路徑導入跨 package 的模組</summary>

此檔案從 packages/platform/atoms 移至 apps/web/components/apps 後，使用相對路徑 `../../../../packages/platform/atoms/src/components/atoms-wrapper` 和 `../../../../packages/platform/atoms/destination-calendar/DestinationCalendar` 導入。這會造成深層耦合，且未來若移動檔案或調整目錄結構，路徑容易失效。建議改用 package alias（如 `@calcom/atoms/...`）或絕對路徑。

**判斷依據**：diff 中新增的相對路徑導入，跨越了多個目錄層級。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:235</code> JSX 縮排不一致</summary>

在 tabMap 的 setup 和 availability 屬性中，JSX 元素的縮排從原本的 6 空格改為 8 空格，與其他屬性（如 team）不一致。這可能是無意的格式變更，建議統一縮排以維持可讀性。

**判斷依據**：diff 中顯示縮排從 6 空格改為 8 空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12096 (cache hit 12032) ｜ completion tokens 904 ｜ PR #9</sub>