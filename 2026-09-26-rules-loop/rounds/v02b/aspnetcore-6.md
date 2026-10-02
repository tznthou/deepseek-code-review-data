<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除多個已標記為過時的 Blazor API，並更新相關程式碼與測試。主要風險在於 `AccessTokenNotAvailableException.Redirect()` 的邏輯變更可能導致 `InteractiveRequestUrl` 為 null 時拋出 `ArgumentNullException`，以及 `RemoteAuthenticatorViewCore.ProcessLogOut` 中新增的 `await Task.Yield()` 可能造成非預期的非同步行為。整體而言，移除過時 API 的方向正確，但需確認上述兩處的相容性與正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect() 可能傳入 null 給 NavigateTo，導致 ArgumentNullException | 0.90 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 await Task.Yield() 可能造成非預期的非同步行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect() 可能傳入 null 給 NavigateTo，導致 ArgumentNullException</summary>

在 `Redirect()` 方法中，原本的邏輯是當 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時呼叫 `NavigateToLogin`，否則使用 `_tokenResult.RedirectUrl`。修改後，條件簡化為只檢查 `InteractionOptions != null`，並在 else 分支直接使用 `_tokenResult.InteractiveRequestUrl!`。如果 `InteractionOptions` 為 null 且 `InteractiveRequestUrl` 也為 null（例如舊版程式碼建立的 `AccessTokenResult` 只設定 `RedirectUrl`），則會傳入 null 給 `NavigateTo`，可能導致 `ArgumentNullException`。建議保留對 `InteractiveRequestUrl` 的 null 檢查，或提供明確的 fallback 邏輯。

**判斷依據**：diff 中 `AccessTokenNotAvailableException.cs` 的變更：原本的 `if (_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null)` 改為 `if (_tokenResult.InteractionOptions != null)`，且 else 分支由 `_navigation.NavigateTo(_tokenResult.RedirectUrl!)` 改為 `_navigation.NavigateTo(_tokenResult.InteractiveRequestUrl!)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 await Task.Yield() 可能造成非預期的非同步行為</summary>

在 `ProcessLogOut` 方法中，於取得 authentication state 之前新增了 `await Task.Yield();`。此舉可能改變方法的執行時序，特別是在 Blazor 的同步渲染上下文中，可能導致後續的 `Navigation.NavigateTo` 等操作延遲到非同步上下文中執行，進而影響元件狀態或產生競態。若無明確理由，建議移除或提供註解說明其必要性。

**判斷依據**：diff 中 `RemoteAuthenticatorViewCore.cs` 的變更：在 `AuthenticationState.ReturnUrl = returnUrl;` 之後新增了 `await Task.Yield();`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16939 (cache hit 16896) ｜ completion tokens 782 ｜ PR #6</sub>