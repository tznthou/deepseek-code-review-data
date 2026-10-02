<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。主要風險在於移除 API 可能造成下游使用者的編譯中斷，以及 ProcessLogOut 中新增的 Task.Yield() 可能改變非同步行為。整體而言，移除動作符合預期，但需確認無其他內部使用或文件遺漏。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能造成非預期的非同步行為 | 0.70 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect 方法中可能使用 null 的 InteractiveRequestUrl | 0.70 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 移除 SignOutSessionStateManager 後，登出驗證邏輯可能遺漏舊版狀態 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能造成非預期的非同步行為</summary>

在 ProcessLogOut 中新增 `await Task.Yield();` 會強制讓出執行緒，可能改變後續 AuthenticationProvider.GetAuthenticationStateAsync() 的執行時序。若此處是為了避免同步上下文問題，應使用 `ConfigureAwait(false)` 或明確說明原因。建議移除或改用更明確的非同步處理方式。

**判斷依據**：diff 中新增的兩行：`// Ensure we're authenticated before proceeding with sign-out` 和 `await Task.Yield();`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect 方法中可能使用 null 的 InteractiveRequestUrl</summary>

原本的條件是 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null`，現在改為只檢查 `InteractionOptions != null`，但後續使用 `_tokenResult.InteractiveRequestUrl!` 強制斷言非 null。若 `InteractiveRequestUrl` 為 null 而 `InteractionOptions` 不為 null，會導致 NullReferenceException。建議保留 null 檢查或確保兩者同時存在。

**判斷依據**：diff 中條件由 `if (_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null)` 改為 `if (_tokenResult.InteractionOptions != null)`，且 else 分支使用 `_tokenResult.InteractiveRequestUrl!`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 移除 SignOutSessionStateManager 後，登出驗證邏輯可能遺漏舊版狀態</summary>

原本的登出驗證會同時檢查 `Navigation.HistoryEntryState` 和 `SignOutManager.ValidateSignOutState()`，現在只檢查 `ValidateSignOutRequestState()`。若舊版用戶端仍使用 SignOutSessionStateManager 設定 session storage，升級後登出可能失敗。需確認是否有向後相容需求。

**判斷依據**：diff 中刪除了 `if ((Navigation.HistoryEntryState != null && !ValidateSignOutRequestState()) || (Navigation.HistoryEntryState == null && !await SignOutManager.ValidateSignOutState()))`，改為 `if (!ValidateSignOutRequestState())`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16873 (cache hit 16768) ｜ completion tokens 934 ｜ PR #6</sub>