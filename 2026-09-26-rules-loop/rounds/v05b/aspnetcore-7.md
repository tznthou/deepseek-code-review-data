<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化，主要修改了 enableJSRootComponents 的邏輯，並調整了相關測試。主要風險在於全域變數 hasInitializedJsComponents 可能導致多個 renderer 共用狀態時初始化被跳過，以及 currentRendererId 的比較邏輯在多 host 情境下可能誤判。建議先釐清多 renderer 的支援範圍，並考慮將狀態改為 per-renderer 管理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:15` | 全域 hasInitializedJsComponents 可能導致多 renderer 初始化被跳過 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | currentRendererId 比較邏輯可能誤判多 host 情境 | 0.60 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 未處理 manager 為 undefined 但 currentRendererId 已設定的情況 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:15</code> 全域 hasInitializedJsComponents 可能導致多 renderer 初始化被跳過</summary>

`hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 true，後續任何 renderer 呼叫 `enableJSRootComponents` 都不會再執行初始化。若頁面上同時存在多個不同 renderer（例如多個 circuit 或不同 renderer type），第二個 renderer 的 JS components 將不會被初始化，導致功能失效。

失敗情境：頁面同時掛載兩個 InteractiveServer 元件（不同 circuit），第一個 circuit 建立時初始化成功，第二個 circuit 建立時因 `hasInitializedJsComponents` 已為 true 而跳過初始化，第二個 circuit 中的 dynamic root components 無法運作。

建議：將 `hasInitializedJsComponents` 改為以 rendererId 為 key 的 Map 或 Set，追蹤每個 renderer 是否已初始化，或考慮將狀態存放在 manager 物件中。

**判斷依據**：diff 中新增了全域變數 `let hasInitializedJsComponents = false;`，並在 `enableJSRootComponents` 中以 `if (!hasInitializedJsComponents)` 包住初始化邏輯，最後設為 true。此變數為模組層級，跨 renderer 共用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> currentRendererId 比較邏輯可能誤判多 host 情境</summary>

原本的檢查是 `if (manager)`，現在改為 `if (manager && currentRendererId === rendererId)`。若不同 renderer type（例如 Server 與 WebAssembly）同時存在，且 rendererId 恰好相同（例如都是 0），則第二次呼叫會拋出錯誤，但實際上這是多 host 情境，應允許各自初始化。

失敗情境：頁面同時使用 Server 和 WebAssembly renderer，兩者 rendererId 均為 0，第二個 renderer 啟用時會觸發例外。

建議：若需支援多 host，應改為檢查 manager 是否已存在且 rendererId 不同，或使用更精確的判斷條件。

**判斷依據**：diff 中將條件從 `if (manager)` 改為 `if (manager && currentRendererId === rendererId)`，但 rendererId 在不同 renderer type 間可能重複。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 未處理 manager 為 undefined 但 currentRendererId 已設定的情況</summary>

若 `manager` 為 undefined 但 `currentRendererId` 已設定（例如先前呼叫失敗或 manager 被清除），則條件 `manager && currentRendererId === rendererId` 為 false，程式會繼續執行並覆寫 `currentRendererId` 和 `manager`，可能導致狀態不一致。

失敗情境：某次呼叫因例外中斷，`manager` 未賦值但 `currentRendererId` 已更新，後續呼叫可能跳過初始化或錯誤地覆寫。

建議：在更新狀態前先檢查並處理不一致的狀態，或將狀態更新與初始化邏輯分離。

**判斷依據**：diff 中在條件判斷後直接賦值，未考慮 manager 為 undefined 但 currentRendererId 已存在的情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6395 (cache hit 6272) ｜ completion tokens 1091 ｜ PR #7</sub>