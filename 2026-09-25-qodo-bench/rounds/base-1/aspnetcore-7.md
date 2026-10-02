<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 JS 根元件初始化邏輯，使其在電路重啟時能重新初始化，並調整了相關測試。主要風險在於全域狀態（hasInitializedJsComponents）可能導致多渲染器情境下初始化被跳過，以及移除測試專用設定後可能影響其他測試的隔離性。建議先確認多渲染器支援需求，並補強測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139` | hasInitializedJsComponents 全域旗標可能導致初始化被跳過 | 0.80 |
| 🔸 | Minor | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 多渲染器情境下 manager 被覆寫但未處理舊 manager | 0.60 |
| 🔸 | Minor | `src/Components/test/testassets/Components.TestServer/Program.cs:26` | 移除測試專用設定可能影響其他測試隔離性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139</code> hasInitializedJsComponents 全域旗標可能導致初始化被跳過</summary>

`hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

**判斷依據**：diff 中新增了 `let hasInitializedJsComponents = false;`，並在 `enableJSRootComponents` 內以 `if (!hasInitializedJsComponents)` 包住初始化迴圈，最後設為 `true`。此旗標為模組層級，跨渲染器共用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 多渲染器情境下 manager 被覆寫但未處理舊 manager</summary>

當 `currentRendererId !== rendererId` 時，程式會直接覆寫 `manager` 與 `currentRendererId`，但未對舊的 `manager` 做任何處理。雖然註解提到舊的 manager 已失效，但若舊渲染器仍存活（例如同時存在多個電路），可能導致舊渲染器的後續呼叫使用到錯誤的 manager。

建議確認此情境是否可能發生，若可能，應考慮以 Map 管理多個 manager，或明確禁止多渲染器同時啟用。

**判斷依據**：diff 中新增了 `currentRendererId = rendererId;` 與 `manager = managerInstance;`，且條件判斷改為 `if (manager && currentRendererId === rendererId)`，允許不同 rendererId 時覆寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/test/testassets/Components.TestServer/Program.cs:26</code> 移除測試專用設定可能影響其他測試隔離性</summary>

原本有一個獨立的測試主機設定（`Razor Component Endpoints with JS Root Component`）用於動態 JS 根元件測試，現在被移除，並將 `RegisterForJavaScript` 直接加入 `RazorComponentEndpointsStartup`。這可能導致所有使用該 startup 的測試都註冊了此動態根元件，若其他測試未預期此行為，可能造成干擾。

建議確認此變更是否會影響其他測試，或考慮使用條件式註冊（例如透過 configuration 控制）。

**判斷依據**：diff 中移除了 `["Razor Component Endpoints with JS Root Component"]` 這一行，並在 `RazorComponentEndpointsStartup.cs` 中將 `RegisterForJavaScript` 改為無條件執行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4276 (cache hit 1536) ｜ completion tokens 1148 ｜ PR #7</sub>