<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化。主要變更在 `JSRootComponents.ts` 中新增 `rendererId` 參數與 `hasInitializedJsComponents` 旗標，以區分不同 renderer 並避免重複初始化。同時調整了測試結構，將原本獨立的測試類別合併至 `StatePersistenceTest.cs`，並移除測試伺服器中的條件註冊。整體風險中等，需注意 `enableJSRootComponents` 的邏輯變更是否會在多 host 情境下造成非預期行為，以及測試覆蓋是否足夠。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | 多 host 情境下可能錯誤地允許重新初始化 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | `hasInitializedJsComponents` 旗標可能導致初始化遺漏 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282` | 測試方法缺少 Arrange-Act-Assert 註解 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> 多 host 情境下可能錯誤地允許重新初始化</summary>

原本的檢查 `if (manager)` 會在任何重複呼叫時拋出錯誤，但新邏輯改為 `if (manager && currentRendererId === rendererId)`，這表示當 `manager` 已存在但 `currentRendererId` 與新的 `rendererId` 不同時，不會拋出錯誤，而是繼續執行並覆寫 `manager` 與 `currentRendererId`。這可能導致多 host 情境（例如同時使用 Server 與 WebAssembly renderer）下，後啟動的 renderer 覆蓋先前的 manager，造成動態 root component 的行為異常。建議確認此情境是否為預期支援，若不支援則應保留拋出錯誤的邏輯。

**判斷依據**：diff 中將原本的 `if (manager)` 改為 `if (manager && currentRendererId === rendererId)`，且後續直接指派 `currentRendererId = rendererId; manager = managerInstance;`，未對不同 rendererId 的情況做任何防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> `hasInitializedJsComponents` 旗標可能導致初始化遺漏</summary>

新增的 `hasInitializedJsComponents` 旗標在第一次初始化後設為 `true`，之後即使 `jsComponentInitializers` 內容改變（例如新增了需要初始化的 component type），也不會再執行初始化。若此函式可能在不同時間點被呼叫且 initializer 集合可能動態增加，則此旗標可能造成部分 component 未初始化。建議確認 initializer 集合是否在應用程式生命週期內固定不變，或考慮改為追蹤已初始化的 identifier。

**判斷依據**：diff 中新增 `hasInitializedJsComponents` 變數，並在初始化迴圈後設為 `true`，之後的呼叫將跳過初始化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282</code> 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 `PersistentStateIsSupportedInDynamicJSRoots` 未包含 `// Arrange`、`// Act`、`// Assert` 等結構化註解，違反專案規範 R06。建議補上對應註解以提升可讀性與一致性。

**判斷依據**：diff 中新增的測試方法沒有 AAA 註解，而其他測試方法（如 `StateIsProvidedEveryTimeACircuitGetsCreated`）有使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6451 (cache hit 6400) ｜ completion tokens 1301 ｜ PR #7</sub>