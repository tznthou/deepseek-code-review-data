<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化。主要變更包括：在 enableJSRootComponents 中新增 rendererId 參數與 currentRendererId 追蹤，並以 hasInitializedJsComponents 旗標避免重複初始化；同時調整測試與測試伺服器設定。整體風險中等，需注意多主機情境下的行為、全域狀態管理，以及測試覆蓋是否足夠。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 多主機情境下 currentRendererId 可能被覆寫，導致錯誤的 manager 被使用 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 全域旗標可能導致不同 renderer 之間初始化遺漏 | 0.70 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:137` | jsComponentParametersByIdentifier 不再被更新，可能導致參數過時 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282` | 測試方法缺少 Arrange-Act-Assert 註解 | 0.60 |
| 🔸 | Minor | `src/Components/test/testassets/Components.TestServer/Program.cs:26` | 移除測試伺服器設定可能影響其他測試 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 多主機情境下 currentRendererId 可能被覆寫，導致錯誤的 manager 被使用</summary>

在 enableJSRootComponents 中，當 manager 已存在且 currentRendererId 與新的 rendererId 不同時，程式碼會直接覆寫 currentRendererId 和 manager，而不會拋出錯誤。這可能導致多主機（例如同時使用 Server 和 WebAssembly）時，後呼叫的 renderer 覆蓋先前的 manager，造成動態 root components 操作指向錯誤的 .NET 物件。

建議：在多主機情境下應拋出錯誤或明確處理，而非靜默覆寫。

**判斷依據**：diff 中新增的 currentRendererId 與 manager 指派，且註解提到多主機情境不支援，但程式碼未阻止覆寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 全域旗標可能導致不同 renderer 之間初始化遺漏</summary>

hasInitializedJsComponents 是模組層級的全域變數，一旦設為 true，後續不同 renderer 的 enableJSRootComponents 呼叫將不會執行初始化。若不同 renderer 需要不同的初始化邏輯或參數，這可能造成問題。

建議：考慮將初始化狀態與 rendererId 關聯，或確認所有 renderer 共用相同的初始化需求。

**判斷依據**：diff 中新增的 hasInitializedJsComponents 旗標與條件判斷。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:137</code> jsComponentParametersByIdentifier 不再被更新，可能導致參數過時</summary>

原本 enableJSRootComponents 會更新 jsComponentParametersByIdentifier，但修改後移除了該指派。若後續呼叫使用不同的 jsComponentParameters，全域變數將保留舊值，可能導致初始化時使用錯誤的參數。

建議：確認是否需要在每次啟用時更新參數，或明確保留舊值。

**判斷依據**：diff 中移除了 jsComponentParametersByIdentifier = jsComponentParameters; 這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282</code> 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 PersistentStateIsSupportedInDynamicJSRoots 未包含 // Arrange、// Act、// Assert 註解，違反專案規範 R06。

建議：加入明確的 AAA 註解以提升可讀性。

**判斷依據**：diff 中新增的測試方法，未見 AAA 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/testassets/Components.TestServer/Program.cs:26</code> 移除測試伺服器設定可能影響其他測試</summary>

移除了 "Razor Component Endpoints with JS Root Component" 的伺服器設定，並將 RegisterForJavaScript 改為無條件註冊。這可能影響依賴該設定的其他測試或情境。

建議：確認所有相關測試已更新，且無其他測試依賴此設定。

**判斷依據**：diff 中刪除了該行，並在 RazorComponentEndpointsStartup.cs 中移除了條件判斷。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6461 (cache hit 1536) ｜ completion tokens 1255 ｜ PR #7</sub>