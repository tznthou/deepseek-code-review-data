<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化。主要變更包括：在 enableJSRootComponents 中新增 rendererId 參數與 hasInitializedJsComponents 旗標，以避免重複初始化；將測試從 StatePersistanceJSRootTest.cs 移至 StatePersistenceTest.cs；並在 RazorComponentEndpointsStartup.cs 中無條件註冊動態 JS root component。整體風險中等，需注意多主機情境下的行為、全域狀態管理，以及測試涵蓋範圍。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | 多主機情境下 rendererId 檢查可能不完整 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:15` | hasInitializedJsComponents 全域旗標可能導致初始化遺漏 | 0.70 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | jsComponentParametersByIdentifier 未在重新初始化時更新 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282` | 測試方法缺少 Arrange-Act-Assert 註解 | 0.50 |
| 🔸 | Minor | `src/Components/test/testassets/Components.TestServer/RazorComponentEndpointsStartup.cs:54` | 無條件註冊動態 JS root component 可能影響其他測試 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> 多主機情境下 rendererId 檢查可能不完整</summary>

在 enableJSRootComponents 中，條件 `if (manager && currentRendererId === rendererId)` 僅在 manager 已存在且 rendererId 相同時拋出錯誤。若 manager 已存在但 rendererId 不同（例如先啟用 Server renderer，再啟用 WebAssembly renderer），則不會拋出錯誤，而是直接覆寫 manager 和 currentRendererId。這可能導致舊 renderer 的 manager 被意外取代，且舊 manager 的資源未正確釋放。建議在 manager 存在且 rendererId 不同時也拋出錯誤，或明確處理多主機情境。

**判斷依據**：diff 中新增的條件僅檢查 rendererId 是否相同，未處理不同 rendererId 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:15</code> hasInitializedJsComponents 全域旗標可能導致初始化遺漏</summary>

hasInitializedJsComponents 是模組層級的全域變數，一旦設為 true，後續即使有新的 renderer 或新的 component 類型需要初始化，也不會再執行初始化邏輯。若未來支援多主機或動態新增 component 類型，此旗標可能導致初始化遺漏。建議考慮將初始化狀態與 renderer 或 component 類型綁定，或提供重置機制。

**判斷依據**：diff 中新增的全域旗標，且初始化邏輯僅在旗標為 false 時執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> jsComponentParametersByIdentifier 未在重新初始化時更新</summary>

在 enableJSRootComponents 中，原本會更新 jsComponentParametersByIdentifier，但修改後僅在首次初始化時設定。若後續呼叫帶有不同的 jsComponentParameters，該變數不會更新，可能導致使用過時的參數。建議確認此變數是否需要在每次啟用時更新。

**判斷依據**：diff 中移除了原本的 `jsComponentParametersByIdentifier = jsComponentParameters;` 指派，且未在別處更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282</code> 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 PersistentStateIsSupportedInDynamicJSRoots 未包含 // Arrange、// Act、// Assert 註解，違反專案規範 R06。建議補上對應的階段註解以提升可讀性。

**判斷依據**：diff 中新增的測試方法，未見 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/testassets/Components.TestServer/RazorComponentEndpointsStartup.cs:54</code> 無條件註冊動態 JS root component 可能影響其他測試</summary>

原本僅在設定 RegisterDynamicJSRootComponent 為 true 時才註冊動態 JS root component，現在改為無條件註冊。這可能導致其他使用 RazorComponentEndpointsStartup 的測試意外載入此 component，增加測試干擾。建議確認此變更是否會影響其他測試情境。

**判斷依據**：diff 中移除了條件判斷，改為直接註冊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6461 (cache hit 6400) ｜ completion tokens 1522 ｜ PR #7</sub>