<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包含 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關程式碼與測試。整體而言是合理的清理，但需注意 RemoteAuthenticatorViewCore 中新增的 Task.Yield() 可能引入非預期的行為變化，且 AccessTokenNotAvailableException.Redirect() 的修改可能導致 NullReferenceException。建議確認這些變更的意圖與影響。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能改變登出流程的時序 | 0.75 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 `_tokenResult.RedirectUrl!`。修改後，當 `InteractionOptions != null` 但 `InteractiveRequestUrl` 為 null 時，會直接傳遞 null 給 NavigateToLogin，可能導致 NullReferenceException。建議保留 null 檢查或提供替代邏輯。

**判斷依據**：diff 中刪除了 `_tokenResult.InteractiveRequestUrl != null` 的條件，並在 else 分支改用 `_tokenResult.InteractiveRequestUrl!`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能改變登出流程的時序</summary>

在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能導致後續的 AuthenticationState 取得延遲，或與其他非同步操作產生競態。若此變更非為了解決特定問題，建議移除；若為必要，請補充說明原因並確保測試涵蓋此情境。

**判斷依據**：diff 中新增的兩行：`// Ensure we're authenticated before proceeding with sign-out` 與 `await Task.Yield();`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14754 (cache hit 1536) ｜ completion tokens 675 ｜ PR #6</sub>