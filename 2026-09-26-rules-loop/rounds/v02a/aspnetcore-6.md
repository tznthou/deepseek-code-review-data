<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為 Obsolete 的 API，包含 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關測試與 PublicAPI 檔案。整體變更方向合理，但需注意 RemoteAuthenticatorViewCore 中移除 SignOutManager 後，登出流程的 CSRF 防護是否仍完整，以及 AccessTokenNotAvailableException.Redirect() 的邏輯變更是否可能造成 NullReferenceException。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 移除 SignOutManager 後，登出流程的 CSRF 防護可能失效 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect() 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.70 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增的 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 移除 SignOutManager 後，登出流程的 CSRF 防護可能失效</summary>

原本的登出流程會檢查 Navigation.HistoryEntryState 或 SignOutManager.ValidateSignOutState()，以確保登出請求是由頁面內部發起。移除 SignOutManager 後，只依賴 Navigation.HistoryEntryState，但若瀏覽器不支援 HistoryEntryState 或狀態遺失，可能導致 CSRF 防護被繞過。建議確認 ValidateSignOutRequestState() 的實作是否已涵蓋所有情況，或保留 SignOutManager 作為備援。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為只檢查 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect() 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本的程式碼在 InteractionOptions 為 null 時使用 RedirectUrl，但現在改為使用 InteractiveRequestUrl。若 InteractiveRequestUrl 為 null（例如舊版程式碼建立的 AccessTokenResult），則會傳遞 null 給 NavigateTo，可能導致例外。建議加入 null 檢查或保留 RedirectUrl 作為 fallback。

**判斷依據**：diff 中將原本的 `_navigation.NavigateTo(_tokenResult.RedirectUrl!)` 改為 `_navigation.NavigateTo(_tokenResult.InteractiveRequestUrl!)`，但未檢查 InteractiveRequestUrl 是否為 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增的 Task.Yield() 可能造成不必要的延遲</summary>

在 ProcessLogOut 中新增 `await Task.Yield();` 並附註「Ensure we're authenticated before proceeding with sign-out」，但此延遲的目的不明確，且可能影響效能。若只是為了讓 AuthenticationState 更新，應考慮更明確的同步機制。

**判斷依據**：diff 中新增了 `await Task.Yield();` 及註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16939 (cache hit 1536) ｜ completion tokens 816 ｜ PR #6</sub>