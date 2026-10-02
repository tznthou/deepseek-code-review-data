<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化，主要修改了 enableJSRootComponents 函數，新增 rendererId 參數與 hasInitializedJsComponents 旗標，並調整了測試。整體風險中等，主要問題在於全域狀態管理可能導致多 host 情境下的錯誤，以及測試覆蓋不足。建議優先修正 enableJSRootComponents 中的邏輯，並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126` | enableJSRootComponents 中的條件判斷可能導致多 host 情境下錯誤地拋出例外 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 旗標可能導致不同 renderer 的 initializer 被跳過 | 0.60 |
| 🔸 | Minor | `src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282` | 測試方法缺少 Arrange-Act-Assert 註解 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126</code> enableJSRootComponents 中的條件判斷可能導致多 host 情境下錯誤地拋出例外</summary>

在 `enableJSRootComponents` 中，條件 `if (manager && currentRendererId === rendererId)` 用於偵測重複啟用。然而，當 `manager` 已存在但 `currentRendererId` 與新的 `rendererId` 不同時（例如不同 host 使用不同 renderer），此條件為 false，程式會繼續執行並覆寫 `manager` 和 `currentRendererId`，而不是拋出錯誤。這與註解中「多 host 情境不支援」的意圖相違背。

**失敗情境**：假設頁面上有兩個 host，第一個 host 使用 rendererId=1 啟用了 JS root components，第二個 host 使用 rendererId=2 嘗試啟用。此時 `manager` 已存在，`currentRendererId` 為 1，條件 `manager && currentRendererId === rendererId` 為 false（1 !== 2），因此不會拋出錯誤，而是直接覆寫 `manager` 和 `currentRendererId`，導致第一個 host 的 manager 被丟棄，可能造成第一個 host 的 JS root components 失效。

**建議修法**：將條件改為 `if (manager)`，並在拋出錯誤前檢查 `currentRendererId !== rendererId`，或者直接使用 `if (manager && currentRendererId !== rendererId)` 來拋出錯誤。

**判斷依據**：diff 中新增的條件 `if (manager && currentRendererId === rendererId)` 與註解「A different renderer type...」不一致。當 rendererId 不同時，條件為 false，不會拋出錯誤，而是繼續執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 旗標可能導致不同 renderer 的 initializer 被跳過</summary>

新增的 `hasInitializedJsComponents` 旗標用於避免重複呼叫 initializer。然而，如果同一個頁面上有多個不同 renderer 的 host（例如一個 Server 和一個 WebAssembly），第一個 host 啟用後將旗標設為 true，第二個 host 啟用時會跳過 initializer 的呼叫，即使第二個 host 的 `jsComponentInitializers` 可能包含不同的 initializer。

**失敗情境**：假設頁面上有兩個 host，第一個 host 使用 Server renderer，第二個 host 使用 WebAssembly renderer。第一個 host 啟用時呼叫了 Server 相關的 initializer，並將 `hasInitializedJsComponents` 設為 true。第二個 host 啟用時，由於旗標為 true，不會呼叫 WebAssembly 相關的 initializer，導致 WebAssembly 的 JS root components 無法正確初始化。

**建議修法**：考慮將 `hasInitializedJsComponents` 改為以 rendererId 為 key 的 map，或者將 initializer 的呼叫與 rendererId 綁定。

**判斷依據**：diff 中新增的 `hasInitializedJsComponents` 旗標是全域的，沒有考慮不同 renderer 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282</code> 測試方法缺少 Arrange-Act-Assert 註解</summary>

新增的測試方法 `PersistentStateIsSupportedInDynamicJSRoots` 沒有遵循 repo 規範 R06（Test Methods Must Use Arrange-Act-Assert Pattern with Comments）。該方法直接執行操作，沒有明確的 Arrange、Act、Assert 區塊註解。

**建議修法**：在測試方法中加入 `// Arrange`、`// Act`、`// Assert` 註解，分隔測試的各個階段。

**判斷依據**：diff 中新增的測試方法沒有 Arrange-Act-Assert 註解，違反 R06。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5226 (cache hit 4224) ｜ completion tokens 1562 ｜ PR #7</sub>