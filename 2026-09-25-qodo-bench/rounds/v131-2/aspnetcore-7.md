<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 JS 端 root components 的初始化邏輯，使其在 circuit 重啟時能重新初始化，並將相關 E2E 測試合併至 StatePersistenceTest。主要風險在於全域狀態（manager、currentRendererId、hasInitializedJsComponents）的管理，可能導致多 host 或多次初始化時的行為不一致。最需先確認的是當不同 renderer 類型（如 Server 與 WebAssembly）同時存在時，是否會因 currentRendererId 檢查而錯誤地允許或拒絕初始化。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | 多 host 情境下 currentRendererId 檢查可能失效 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 全域旗標可能導致初始化遺漏 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> 多 host 情境下 currentRendererId 檢查可能失效</summary>

原本的檢查是 `if (manager)`，只要 manager 已存在就拋錯，避免多 host 同時啟用。現在改為 `if (manager && currentRendererId === rendererId)`，這表示如果兩個不同的 renderer（例如 Server 與 WebAssembly）同時存在，且 rendererId 不同，則不會拋錯，而是會覆寫 manager 與 currentRendererId。這可能導致後續呼叫使用到錯誤的 manager，或造成動態 root components 的行為不一致。

建議：若確定不支援多 host，應保留原本的嚴格檢查（只要 manager 已存在就拋錯），或明確處理多 host 情境（例如使用 Map 以 rendererId 為鍵儲存 manager）。

**判斷依據**：diff 中將原本的 `if (manager)` 改為 `if (manager && currentRendererId === rendererId)`，且註解提到「A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. This is a multi-host scenario which is not supported for dynamic root components.」但程式碼並未阻止此情境，反而允許覆寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 全域旗標可能導致初始化遺漏</summary>

新增的 `hasInitializedJsComponents` 旗標用於確保初始化只執行一次。但在 circuit 重啟後，新的 manager 可能帶有不同的 jsComponentInitializers 或 jsComponentParameters，若旗標已為 true，則不會重新執行初始化，可能導致新的 component 未正確初始化。

建議：確認 circuit 重啟後是否會傳入不同的 initializers；若會，則應考慮以 rendererId 或 manager 為單位記錄初始化狀態，而非使用單一全域旗標。

**判斷依據**：diff 中新增 `let hasInitializedJsComponents = false;` 並在 `enableJSRootComponents` 中使用，但未考慮不同 manager 可能帶有不同的初始化需求。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4240 (cache hit 4224) ｜ completion tokens 746 ｜ PR #7</sub>