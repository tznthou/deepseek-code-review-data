<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。主要風險在於移除 API 可能造成下游使用者的編譯中斷，以及 RemoteAuthenticatorViewCore 中登出流程的邏輯變更是否正確。整體而言，變更範圍明確且多數為刪除，但需確認登出流程的修改不會引入安全性或功能回歸。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 登出流程中新增的 Task.Yield() 可能造成非預期的非同步行為 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect 方法中改用 InteractiveRequestUrl 可能導致 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出流程移除 SignOutSessionStateManager 後可能遺失 CSRF 保護 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 登出流程中新增的 Task.Yield() 可能造成非預期的非同步行為</summary>

在 `ProcessLogOut` 方法中，於取得驗證狀態前新增了 `await Task.Yield();`。此舉會強制讓出執行緒，可能導致後續的 `AuthenticationProvider.GetAuthenticationStateAsync()` 在不同的同步內容中執行。若 `AuthenticationProvider` 依賴特定的同步內容（例如 Blazor 的 SynchronizationContext），可能造成狀態不一致或死鎖。建議移除該行，或提供明確的註解說明其必要性。

**判斷依據**：diff 中新增了 `await Task.Yield();` 於 `AuthenticationProvider.GetAuthenticationStateAsync()` 之前，且無任何註解說明其目的。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect 方法中改用 InteractiveRequestUrl 可能導致 NullReferenceException</summary>

在 `Redirect` 方法中，原本使用 `_tokenResult.RedirectUrl!`，現在改為 `_tokenResult.InteractiveRequestUrl!`。但 `InteractiveRequestUrl` 可能為 null（例如當 `InteractionOptions` 為 null 且 `InteractiveRequestUrl` 未設定時），使用 null-forgiving 運算子會隱藏潛在的 null 問題，並在執行時拋出 `NullReferenceException`。建議檢查 `InteractiveRequestUrl` 是否為 null，並提供明確的錯誤處理或回退機制。

**判斷依據**：diff 中將 `_tokenResult.RedirectUrl!` 改為 `_tokenResult.InteractiveRequestUrl!`，但未檢查 `InteractiveRequestUrl` 是否為 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出流程移除 SignOutSessionStateManager 後可能遺失 CSRF 保護</summary>

原本的登出流程會透過 `SignOutSessionStateManager.ValidateSignOutState()` 驗證登出請求是否來自頁面內部，以提供 CSRF 保護。移除後僅依賴 `ValidateSignOutRequestState()`，但該方法可能只檢查 `HistoryEntryState`，若攻擊者能偽造 `HistoryEntryState`，可能繞過保護。建議確認 `ValidateSignOutRequestState()` 的實作是否足夠安全，或保留某種形式的 CSRF 防護。

**判斷依據**：diff 中移除了 `SignOutManager.ValidateSignOutState()` 的呼叫，僅保留 `ValidateSignOutRequestState()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16939 (cache hit 14720) ｜ completion tokens 947 ｜ PR #6</sub>