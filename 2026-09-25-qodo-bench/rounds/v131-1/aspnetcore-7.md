<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 JS 端動態根元件的初始化邏輯，使其在相同 renderer 重新啟用時（如 circuit 重啟）能正確更新 manager，並避免重複執行初始化。同時調整了相關測試與測試伺服器設定。主要風險在於全域狀態 `hasInitializedJsComponents` 在多 renderer 並存時可能導致初始化被跳過，以及 `currentRendererId` 的比較邏輯可能無法正確處理不同 renderer 的切換。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | 多 renderer 並存時初始化可能被跳過 | 0.80 |
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | renderer 切換時可能錯誤拋出例外 | 0.75 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 未更新 jsComponentParametersByIdentifier | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> 多 renderer 並存時初始化可能被跳過</summary>

`hasInitializedJsComponents` 是全域變數，一旦設為 true，之後任何 renderer 呼叫 `enableJSRootComponents` 都不會再執行初始化。若頁面同時存在多個不同 renderer（例如一個 Server 和一個 WebAssembly），且第一個 renderer 初始化後，第二個 renderer 的 JS 元件將不會被初始化，導致功能失效。

建議將 `hasInitializedJsComponents` 改為以 rendererId 為鍵的集合，或將初始化邏輯綁定到每個 manager 實例。

**判斷依據**：diff 中新增了全域變數 `let hasInitializedJsComponents = false;`，並在 `enableJSRootComponents` 內以 `if (!hasInitializedJsComponents)` 包裹初始化邏輯，最後設為 true。此變數未與 rendererId 關聯，因此跨 renderer 共用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> renderer 切換時可能錯誤拋出例外</summary>

條件 `if (manager && currentRendererId === rendererId)` 只在 manager 存在且 rendererId 相同時拋出例外。若 manager 存在但 rendererId 不同（例如從 Server 切換到 WebAssembly），則不會拋出例外，而是直接覆寫 manager 和 currentRendererId。這可能導致舊 manager 的資源未被正確處理，或新舊 manager 狀態混亂。

建議明確處理 rendererId 不同的情況，例如記錄警告或採取其他措施。

**判斷依據**：diff 中條件從 `if (manager)` 改為 `if (manager && currentRendererId === rendererId)`，但未處理 manager 存在且 rendererId 不同的分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 未更新 jsComponentParametersByIdentifier</summary>

在重新啟用時，程式碼更新了 `manager` 和 `currentRendererId`，但未更新 `jsComponentParametersByIdentifier`。若新的 renderer 提供了不同的參數，舊參數仍會被使用，可能導致元件初始化時使用過時資料。

建議在重新啟用時一併更新 `jsComponentParametersByIdentifier`。

**判斷依據**：diff 中原本有 `jsComponentParametersByIdentifier = jsComponentParameters;`，但被移除，且未在重新啟用路徑中重新賦值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4240 (cache hit 1408) ｜ completion tokens 948 ｜ PR #7</sub>