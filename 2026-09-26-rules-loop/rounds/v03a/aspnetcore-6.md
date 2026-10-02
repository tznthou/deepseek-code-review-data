<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新了對應的 PublicAPI.Unshipped.txt 與測試。主要風險在於移除 API 後可能造成下游使用者的編譯中斷，以及 RemoteAuthenticatorViewCore 中登出流程的邏輯變更是否正確。整體而言，變更範圍明確且多數為刪除過時程式碼，但需確認登出流程的修改不會引入安全性或功能回歸。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 登出流程中新增的 Task.Yield() 可能造成非預期的非同步行為 | 0.75 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect() 方法中改用 InteractiveRequestUrl 可能導致 NullReferenceException | 0.70 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 移除 SignOutSessionStateManager 後，登出驗證邏輯可能遺漏舊版狀態 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 登出流程中新增的 Task.Yield() 可能造成非預期的非同步行為</summary>

在 ProcessLogOut 方法中新增了 `await Task.Yield();`，這會強制讓出執行緒，可能導致後續的 AuthenticationState 檢查延遲。若此處是為了避免同步上下文問題，應考慮使用 `ConfigureAwait(false)` 或明確說明原因。此外，此變更可能影響登出流程的時序，特別是在 Blazor Server 環境中。

**判斷依據**：diff 中新增了 `await Task.Yield();`，且無對應的註解說明其必要性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect() 方法中改用 InteractiveRequestUrl 可能導致 NullReferenceException</summary>

原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 `_tokenResult.RedirectUrl!`。修改後，條件僅檢查 `InteractionOptions != null`，但若 `InteractiveRequestUrl` 為 null，則會傳入 null 給 NavigateToLogin，可能導致 NullReferenceException。建議保留對 InteractiveRequestUrl 的 null 檢查，或確保該屬性在 InteractionOptions 存在時必定非 null。

**判斷依據**：diff 中移除了 `_tokenResult.InteractiveRequestUrl != null` 的條件，且 else 分支使用 `_tokenResult.InteractiveRequestUrl!` 強制斷言非 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 移除 SignOutSessionStateManager 後，登出驗證邏輯可能遺漏舊版狀態</summary>

原本的登出驗證會同時檢查 HistoryEntryState 與 SignOutSessionStateManager 的狀態，以相容舊版。移除後僅依賴 HistoryEntryState，可能導致使用舊版機制產生的登出請求被拒絕。若此為預期的 breaking change，應在 PR 描述中明確說明。

**判斷依據**：diff 中移除了 `(Navigation.HistoryEntryState != null && !ValidateSignOutRequestState()) || (Navigation.HistoryEntryState == null && !await SignOutManager.ValidateSignOutState())` 的條件，簡化為 `!ValidateSignOutRequestState()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16949 (cache hit 14720) ｜ completion tokens 967 ｜ PR #6</sub>