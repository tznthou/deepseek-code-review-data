<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 marketplace 搜尋狀態從可選的 URL 保留改為一律保留在 URL 查詢參數中，移除了相關的 atom 與 hydration 元件，並將 category 參數改名為 tab。主要風險在於 `useMarketplaceSearchMode` 中條件判斷的邏輯變更（移除否定運算子）可能導致搜尋模式判斷錯誤，以及 `usePluginPageContext` 的 selector 參數型別從函式改為 `any`，違反 R09 並降低型別安全。建議先修正這兩個問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/plugins/marketplace/atoms.ts:43` | 搜尋模式判斷邏輯錯誤：移除否定運算子導致條件相反 | 0.95 |
| ⚠️ | Major | `web/app/components/plugins/plugin-page/context.tsx:51` | [R09] selector 參數型別從函式改為 any，喪失型別安全 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/plugins/marketplace/atoms.ts:43</code> 搜尋模式判斷邏輯錯誤：移除否定運算子導致條件相反</summary>

在 `useMarketplaceSearchMode` 中，原本的條件 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 被改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這會讓「當 activePluginType 屬於有 collections 的類別時」被視為搜尋模式，與原本意圖相反。

**失敗情境**：當使用者選擇一個有 collections 的 plugin 類別（例如某個特定分類）且沒有輸入搜尋文字或 tags 時，原本應顯示一般瀏覽模式，但修改後會錯誤地進入搜尋模式，可能導致 UI 顯示錯誤或資料請求行為改變。

**建議**：恢復否定運算子，改回 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

**判斷依據**：diff 中此行從 `|| (searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))` 改為 `|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/plugin-page/context.tsx:51</code> [R09] selector 參數型別從函式改為 any，喪失型別安全</summary>

`usePluginPageContext` 的 selector 參數型別從原本的 `(value: PluginPageContextValue) => any` 改為 `any`。這違反了 R09（TypeScript Must Avoid any Type Annotations），且會讓呼叫端可以傳入任意值，導致 `useContextSelector` 在執行時期可能收到非函式而拋出錯誤。

**失敗情境**：如果有開發者誤傳入非函式（例如直接傳入一個值），`useContextSelector` 內部嘗試呼叫該值時會拋出 TypeError，造成 runtime crash。

**建議**：保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => unknown` 並在內部檢查型別。

**判斷依據**：diff 中此行從 `export function usePluginPageContext(selector: (value: PluginPageContextValue) => any) {` 改為 `export function usePluginPageContext(selector: any) {`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5851 (cache hit 3072) ｜ completion tokens 863 ｜ PR #9</sub>