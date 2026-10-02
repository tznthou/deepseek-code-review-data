<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新了相關的 PublicAPI.Unshipped.txt 檔案。整體而言，移除動作符合預期，但需注意 RemoteAuthenticatorViewCore 中 ProcessLogOut 的邏輯變更可能影響登出流程，且 AccessTokenNotAvailableException.Redirect 的修改可能導致 NullReferenceException。建議確認這些變更的相容性與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | ProcessLogOut 移除 SignOutManager 驗證可能導致登出流程異常 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增的 Task.Yield() 可能影響登出流程的時序 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> ProcessLogOut 移除 SignOutManager 驗證可能導致登出流程異常</summary>

原本的程式碼在 Navigation.HistoryEntryState 為 null 時會使用 SignOutManager.ValidateSignOutState() 進行驗證，現在完全依賴 ValidateSignOutRequestState()。如果某些舊版用戶端或情境下 HistoryEntryState 為 null 且未設定正確的狀態，登出請求可能被錯誤拒絕或允許。建議確認 ValidateSignOutRequestState() 的實作是否涵蓋所有舊有情境，並補充對應的測試。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為只呼叫 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect 方法可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本的程式碼在 _tokenResult.InteractionOptions 為 null 時使用 _tokenResult.RedirectUrl，現在改為使用 _tokenResult.InteractiveRequestUrl。如果 InteractiveRequestUrl 為 null（例如舊版建立的 AccessTokenResult 物件），則會傳遞 null 給 NavigateTo，可能導致 NullReferenceException。建議加入 null 檢查或確保 InteractiveRequestUrl 永遠有值。

**判斷依據**：diff 中將原本的 _tokenResult.RedirectUrl! 改為 _tokenResult.InteractiveRequestUrl!，但未見對 InteractiveRequestUrl 的 null 防護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增的 Task.Yield() 可能影響登出流程的時序</summary>

在取得 AuthenticationState 之前加入 await Task.Yield()，可能是為了避免同步阻塞，但這會讓登出流程多一個非同步點。如果後續程式碼依賴同步執行，可能造成行為差異。建議確認此變更的必要性，並補充測試。

**判斷依據**：diff 中新增了 await Task.Yield(); 這一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16949 (cache hit 16896) ｜ completion tokens 821 ｜ PR #6</sub>