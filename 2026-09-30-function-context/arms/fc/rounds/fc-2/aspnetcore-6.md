<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。主要風險在於移除 API 可能導致使用舊版的使用者編譯失敗，以及 ProcessLogOut 中新增的 Task.Yield() 可能造成非預期的非同步行為。整體而言，變更範圍明確且多數為刪除，但需確認無其他內部相依性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能導致登出流程的非預期延遲 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect 方法可能使用 null 的 InteractiveRequestUrl | 0.75 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能導致登出流程的非預期延遲</summary>

在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能造成登出流程延遲。若 AuthenticationProvider.GetAuthenticationStateAsync 依賴於特定同步內容（例如 Blazor 的 SynchronizationContext），此變更可能導致後續程式碼在錯誤的執行緒上執行，或造成競態。建議移除該行，除非有明確理由需要讓出。

**判斷依據**：diff 中新增的兩行：`// Ensure we're authenticated before proceeding with sign-out` 和 `await Task.Yield();`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect 方法可能使用 null 的 InteractiveRequestUrl</summary>

在 `Redirect()` 方法中，原本的條件是 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null`，現在改為只檢查 `_tokenResult.InteractionOptions != null`，然後直接使用 `_tokenResult.InteractiveRequestUrl!`。如果 `InteractiveRequestUrl` 為 null，會導致 `NavigateToLogin` 收到 null 參數，可能拋出例外。建議保留 null 檢查或使用 null 條件運算子。

**判斷依據**：diff 中將條件從 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 改為 `_tokenResult.InteractionOptions != null`，並在 else 分支使用 `_tokenResult.InteractiveRequestUrl!`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18451 (cache hit 18432) ｜ completion tokens 714 ｜ PR #6</sub>