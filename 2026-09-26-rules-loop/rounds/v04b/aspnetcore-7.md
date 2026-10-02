<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整 JS root components 的初始化邏輯，使其在 circuit 重啟時能重新初始化，並將相關 E2E 測試合併至 StatePersistenceTest.cs。主要風險在於 enableJSRootComponents 的條件判斷與全域狀態管理，可能導致多 host 情境下的錯誤行為或初始化遺漏。建議優先確認 rendererId 的比較邏輯與 hasInitializedJsComponents 的重設時機。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | enableJSRootComponents 的條件判斷可能導致多 host 情境下錯誤拋出例外 | 0.80 |
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 全域旗標可能導致初始化遺漏 | 0.70 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:145` | 迴圈內未使用大括號可能違反專案規範 R17 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282` | 測試方法未遵循 Arrange-Act-Assert 模式（R06） | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> enableJSRootComponents 的條件判斷可能導致多 host 情境下錯誤拋出例外</summary>

原邏輯僅檢查 manager 是否存在，現在改為同時檢查 currentRendererId === rendererId。若不同 renderer type（例如 Server 與 WebAssembly）同時存在，且第一個 renderer 已初始化，第二個 renderer 呼叫時會因 manager 存在但 rendererId 不同而拋出例外。但註解說明此為不支援的多 host 情境，因此行為可能符合預期。然而，若同一 renderer type 但不同 rendererId（例如多個 circuit）同時存在，此條件會允許覆寫 manager，可能導致舊 circuit 的 manager 被覆蓋，造成後續操作錯誤。建議確認是否應改為僅在 manager 存在且 rendererId 不同時拋出例外，或明確限制單一 renderer type。

**判斷依據**：diff 中第 121 行新增條件 currentRendererId === rendererId，且後續指派 currentRendererId = rendererId; 與 manager = managerInstance; 可能覆寫既有 manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 全域旗標可能導致初始化遺漏</summary>

新增 hasInitializedJsComponents 旗標，僅在第一次啟用時執行初始化。若同一頁面有多個 renderer type（例如 Server 與 WebAssembly），且第一個 renderer 初始化後，第二個 renderer 啟用時將不會執行初始化，即使其 jsComponentInitializers 不同。這可能導致第二個 renderer 的 JS 元件未正確初始化。建議將旗標改為以 rendererId 為鍵的集合，或確認此情境不支援。

**判斷依據**：diff 中第 135 行新增條件，且 hasInitializedJsComponents 為模組層級變數，未依 rendererId 區分。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:145</code> 迴圈內未使用大括號可能違反專案規範 R17</summary>

在 for 迴圈內，單行陳述式未使用大括號。雖然 TypeScript 語法允許，但專案規範 R17 要求所有控制流程陳述式使用大括號，以預防潛在錯誤。建議加上大括號。

**判斷依據**：diff 中第 139-140 行顯示 for 迴圈內單行陳述式未使用大括號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282</code> 測試方法未遵循 Arrange-Act-Assert 模式（R06）</summary>

新增的測試方法 PersistentStateIsSupportedInDynamicJSRoots 未使用 Arrange-Act-Assert 註解分隔測試階段。雖然專案規範 R06 要求測試方法使用此模式，但此測試為 E2E 測試，可能不適用。建議確認是否需遵循。

**判斷依據**：diff 中新增的測試方法未包含 Arrange/Act/Assert 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5226 (cache hit 5120) ｜ completion tokens 1233 ｜ PR #7</sub>