<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。整體變更符合移除過時 API 的目標，但需注意 AccessTokenNotAvailableException.Redirect() 的邏輯變更可能導致 NullReferenceException，以及 RemoteAuthenticatorViewCore 中新增的 Task.Yield() 可能影響登出行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.90 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能造成登出流程的競態或延遲 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

在 `Redirect()` 方法中，原本的邏輯是當 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時呼叫 `NavigateToLogin`，否則使用 `_tokenResult.RedirectUrl`。現在改為只要 `InteractionOptions != null` 就呼叫 `NavigateToLogin`，但若 `InteractiveRequestUrl` 為 null，`NavigateToLogin` 內部可能會拋出 NullReferenceException。此外，else 分支改為使用 `InteractiveRequestUrl`，但該屬性可能為 null，導致 `NavigateTo` 拋出例外。建議保留對 `InteractiveRequestUrl` 的 null 檢查，或確保在建構 `AccessTokenResult` 時該屬性必不為 null。

**判斷依據**：diff 中刪除了 `_tokenResult.InteractiveRequestUrl != null` 的條件，且 else 分支使用 `_tokenResult.InteractiveRequestUrl!`，但該屬性在 `AccessTokenResult` 中可能為 null（例如使用舊建構函式時）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能造成登出流程的競態或延遲</summary>

在 `ProcessLogOut` 中，於取得驗證狀態前新增了 `await Task.Yield();`。這可能導致登出流程延遲，且若 `AuthenticationProvider.GetAuthenticationStateAsync()` 依賴某些同步狀態，可能引入競態。建議移除或提供明確理由。

**判斷依據**：diff 中新增了 `await Task.Yield();`，但未提供足夠的上下文說明其必要性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14718 (cache hit 1408) ｜ completion tokens 752 ｜ PR #6</sub>