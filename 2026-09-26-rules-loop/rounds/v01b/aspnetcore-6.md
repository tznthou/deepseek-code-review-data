<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新了相關的 PublicAPI.Unshipped.txt 檔案。整體而言，移除動作符合預期，但需注意 RemoteAuthenticatorViewCore 中登出流程的變更可能引入行為差異，且 AccessTokenNotAvailableException.Redirect 的修改可能導致 NullReferenceException。建議確認這些變更的相容性與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出流程移除 SignOutSessionStateManager 後可能導致 CSRF 驗證失效 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增的 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出流程移除 SignOutSessionStateManager 後可能導致 CSRF 驗證失效</summary>

原本的登出流程會先檢查 Navigation.HistoryEntryState 是否存在，若不存在則使用 SignOutSessionStateManager.ValidateSignOutState() 進行驗證。移除後，僅依賴 ValidateSignOutRequestState()，但該方法可能只檢查 HistoryEntryState，若使用者直接導航至登出頁面（無 HistoryEntryState），將無法驗證登出請求的合法性，可能導致 CSRF 攻擊。建議確認 ValidateSignOutRequestState() 的實作是否涵蓋所有情境，或保留某種形式的 session state 驗證。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為只呼叫 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本的程式碼在 _tokenResult.InteractionOptions 為 null 時，使用 _tokenResult.RedirectUrl 進行導航，但該屬性已移除。現在改為使用 _tokenResult.InteractiveRequestUrl，但若該屬性為 null（例如舊版建立的 AccessTokenResult 未設定），則會傳遞 null 給 NavigateTo，可能導致 NullReferenceException。建議加入 null 檢查或確保所有建立 AccessTokenResult 的地方都設定 InteractiveRequestUrl。

**判斷依據**：diff 中將原本的 _tokenResult.RedirectUrl! 改為 _tokenResult.InteractiveRequestUrl!，但未檢查 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增的 Task.Yield() 可能造成不必要的延遲</summary>

在取得 AuthenticationState 之前加入 await Task.Yield()，可能是為了避免同步上下文問題，但若無明確理由，可能只是增加延遲。建議確認此變更的必要性，或移除。

**判斷依據**：diff 中新增了 await Task.Yield(); 這一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16939 (cache hit 16896) ｜ completion tokens 830 ｜ PR #6</sub>