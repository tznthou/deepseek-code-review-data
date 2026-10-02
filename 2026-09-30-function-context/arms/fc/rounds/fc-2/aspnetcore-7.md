<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化。主要變更包括：在 enableJSRootComponents 中新增 rendererId 參數與 currentRendererId 狀態，以區分不同 renderer 類型；使用 hasInitializedJsComponents 旗標避免重複初始化；移除舊的 StatePersistanceJSRootTest 並將測試移至 StatePersistenceTest；在測試設定中無條件註冊動態 JS root component。整體風險中等，主要疑慮在於多 renderer 情境下的行為、全域狀態管理，以及測試涵蓋範圍。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 多 renderer 情境下可能錯誤覆寫 manager | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 全域旗標可能導致初始化遺漏 | 0.60 |
| 🔸 | Minor | `src/Components/test/testassets/Components.TestServer/RazorComponentEndpointsStartup.cs:54` | 無條件註冊動態 JS root component 可能影響其他測試 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 多 renderer 情境下可能錯誤覆寫 manager</summary>

當不同 renderer 類型（例如 Server 與 WebAssembly）同時存在時，enableJSRootComponents 會以新的 rendererId 覆寫 currentRendererId 與 manager，但舊的 manager 仍可能被其他 renderer 使用。這可能導致動態 root components 被錯誤地綁定到新的 manager，或舊 manager 的呼叫失敗。建議在多 renderer 情境下明確禁止或提供隔離機制。

**判斷依據**：diff 中新增的 currentRendererId 與 manager 指派，但未檢查是否已有其他 renderer 正在使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 全域旗標可能導致初始化遺漏</summary>

hasInitializedJsComponents 為模組層級變數，一旦設為 true，後續不同 renderer 的啟用將不會重新執行初始化。若新的 renderer 需要不同的初始化邏輯或參數，可能無法正確設定。建議將此旗標與 rendererId 關聯，或改為依 renderer 管理初始化狀態。

**判斷依據**：diff 中新增的 hasInitializedJsComponents 旗標，未與 rendererId 綁定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/testassets/Components.TestServer/RazorComponentEndpointsStartup.cs:54</code> 無條件註冊動態 JS root component 可能影響其他測試</summary>

原本僅在設定 RegisterDynamicJSRootComponent 時註冊，現在改為無條件註冊。這可能導致其他使用此 startup 的測試意外載入此 component，增加測試耦合或干擾。建議確認所有使用此 startup 的測試是否預期此行為。

**判斷依據**：diff 中移除了條件判斷，改為直接註冊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5437 (cache hit 5376) ｜ completion tokens 813 ｜ PR #7</sub>