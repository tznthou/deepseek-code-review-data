<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，包括 Router.PreferExactMatches、EditContextDataAnnotationsExtensions 的舊方法、RemoteBrowserFileStreamOptions、WebEventCallbackFactoryEventArgsExtensions、SignOutSessionStateManager 等，並更新相關測試與 PublicAPI 檔案。主要風險在於移除 SignOutSessionStateManager 後，登出流程的 CSRF 防護改為完全依賴 HistoryEntryState，可能影響舊版用戶端或非 SPA 情境；此外，AccessTokenNotAvailableException.Redirect() 的變更可能導致 null 參考例外。整體而言，移除過時 API 是合理的清理，但需確認登出流程的相容性與 null 處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出流程移除 SignOutSessionStateManager 後可能破壞 CSRF 防護 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增的 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出流程移除 SignOutSessionStateManager 後可能破壞 CSRF 防護</summary>

原本的登出驗證會同時檢查 HistoryEntryState 與 SignOutSessionStateManager，現在只依賴 HistoryEntryState。若使用者從舊版用戶端或非 SPA 環境觸發登出，HistoryEntryState 可能為 null，導致登出被視為外部啟動而失敗。建議確認所有支援的登出路徑都會設定 HistoryEntryState，或保留某種向後相容的驗證機制。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為只呼叫 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本在沒有 InteractionOptions 時使用 RedirectUrl，現在改用 InteractiveRequestUrl。但 InteractiveRequestUrl 可能為 null（例如舊版建立的 AccessTokenResult），此時 NavigateTo 會收到 null 參數而拋出例外。建議加入 null 檢查或提供預設行為。

**判斷依據**：diff 中將原本的 `_navigation.NavigateTo(_tokenResult.RedirectUrl!)` 改為 `_navigation.NavigateTo(_tokenResult.InteractiveRequestUrl!)`，但未檢查 InteractiveRequestUrl 是否為 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增的 Task.Yield() 可能造成不必要的延遲</summary>

在取得 AuthenticationState 之前加入 `await Task.Yield()`，可能是為了避免同步上下文問題，但若無明確理由，可能只是增加延遲。建議確認其必要性，或改用 ConfigureAwait(false) 等方式。

**判斷依據**：diff 中新增了 `await Task.Yield();` 這一行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16929 (cache hit 14720) ｜ completion tokens 806 ｜ PR #6</sub>