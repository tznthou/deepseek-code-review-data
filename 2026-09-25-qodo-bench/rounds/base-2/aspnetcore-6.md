<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。主要風險在於移除 API 可能造成使用者的編譯中斷，以及 ProcessLogOut 中新增的 Task.Yield() 可能引入非預期的非同步行為。整體而言，變更範圍明確且多數移除符合預期，但建議確認所有內部使用均已更新，並評估對下游使用者的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能造成非預期的非同步行為 | 0.75 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect 方法中可能使用 null 的 InteractiveRequestUrl | 0.70 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 移除 SignOutSessionStateManager 後，登出狀態驗證邏輯可能不完整 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能造成非預期的非同步行為</summary>

在 ProcessLogOut 中新增 `await Task.Yield();` 可能改變執行流程，特別是在驗證登出狀態後、取得驗證狀態前。此舉可能引入競態條件或延遲，且未提供明確理由。建議移除或提供詳細說明，並確保有對應測試涵蓋此行為。

**判斷依據**：diff 中新增的兩行，位於 ProcessLogOut 方法內，緊接在 AuthenticationState.ReturnUrl = returnUrl; 之後。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect 方法中可能使用 null 的 InteractiveRequestUrl</summary>

在 `Redirect()` 方法中，條件從 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 改為僅檢查 `_tokenResult.InteractionOptions != null`，然後在 else 分支中使用 `_tokenResult.InteractiveRequestUrl!`。若 `InteractiveRequestUrl` 為 null，將導致 NullReferenceException。建議保留 null 檢查或確保該屬性在 InteractionOptions 存在時必定非 null。

**判斷依據**：diff 中條件判斷的修改，以及 else 分支中對 InteractiveRequestUrl 的使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 移除 SignOutSessionStateManager 後，登出狀態驗證邏輯可能不完整</summary>

原本的登出流程會同時檢查 HistoryEntryState 和 SignOutSessionStateManager，現在僅依賴 HistoryEntryState。若某些用戶端或情境未正確設定 HistoryEntryState，可能導致登出驗證失敗或安全漏洞。建議確認所有登出路徑都已更新為使用 HistoryEntryState。

**判斷依據**：diff 中刪除了原本包含 SignOutManager.ValidateSignOutState() 的條件分支。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14754 (cache hit 14720) ｜ completion tokens 916 ｜ PR #6</sub>