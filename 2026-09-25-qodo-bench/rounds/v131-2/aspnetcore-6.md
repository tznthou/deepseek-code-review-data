<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等。整體而言，移除動作符合預期，但需注意 RemoteAuthenticatorViewCore 中 ProcessLogOut 的邏輯變更：移除了 SignOutManager 的驗證，並新增 Task.Yield()，可能影響登出流程的驗證與時序。此外，AccessTokenNotAvailableException.Redirect 的變更可能導致 null 參考例外。建議確認這些行為變更的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出驗證邏輯變更可能削弱 CSRF 防護 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出例外 | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增 Task.Yield() 可能影響登出流程時序 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出驗證邏輯變更可能削弱 CSRF 防護</summary>

原本的登出流程會先驗證 SignOutSessionStateManager 的狀態（透過 sessionStorage 中的 SignOutState），現在改為只呼叫 ValidateSignOutRequestState()。若 ValidateSignOutRequestState() 的實作未涵蓋原本 SignOutManager 的驗證，可能導致 CSRF 防護失效。請確認 ValidateSignOutRequestState() 是否完整取代原本的驗證邏輯，並確保登出請求仍受到保護。

**判斷依據**：diff 中移除了對 SignOutManager.ValidateSignOutState() 的呼叫，並將條件簡化為只呼叫 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出例外</summary>

原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 RedirectUrl。現在改為只要 InteractionOptions 不為 null 就呼叫 NavigateToLogin，但若 InteractiveRequestUrl 為 null，可能導致 NullReferenceException。請確認 InteractiveRequestUrl 在 InteractionOptions 存在時必定有值，或加入 null 檢查。

**判斷依據**：diff 中移除了對 InteractiveRequestUrl 的 null 檢查，並在 else 分支改用 InteractiveRequestUrl。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增 Task.Yield() 可能影響登出流程時序</summary>

在取得 AuthenticationState 之前新增 `await Task.Yield();`，可能是為了避免同步上下文問題，但可能導致不必要的延遲或行為改變。請確認此變更的必要性，並考慮是否應在特定條件下才執行。

**判斷依據**：diff 中新增了 `await Task.Yield();` 於取得 AuthenticationState 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14718 (cache hit 14592) ｜ completion tokens 842 ｜ PR #6</sub>