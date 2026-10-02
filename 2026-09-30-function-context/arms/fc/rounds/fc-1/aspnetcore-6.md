<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，並調整登出流程以完全依賴 HistoryEntryState。主要風險在於登出流程的變更：新增的 `await Task.Yield()` 可能引入競態，且移除 SignOutSessionStateManager 後，若 HistoryEntryState 為 null 或格式不符，登出將直接失敗。此外，AccessTokenNotAvailableException.Redirect 的變更可能導致在特定條件下使用 null URL 進行導航。整體而言，移除過時 API 是合理的，但登出流程的變更需要更仔細的驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 登出流程中新增的 Task.Yield 可能引入競態 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出流程完全依賴 HistoryEntryState，可能導致登出失敗 | 0.75 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect 方法可能使用 null 的 InteractiveRequestUrl | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 登出流程中新增的 Task.Yield 可能引入競態</summary>

在 `ProcessLogOut` 中，於驗證登出狀態後、取得驗證狀態前新增了 `await Task.Yield()`。這會讓出執行緒，可能導致後續的 `AuthenticationProvider.GetAuthenticationStateAsync()` 讀取到不一致的狀態。例如，若使用者在 `Task.Yield()` 期間登入或登出，可能導致登出流程使用過時的驗證狀態。建議移除 `Task.Yield()`，或說明其必要性並確保狀態一致性。

**判斷依據**：diff 中新增了 `await Task.Yield();`，且前後文顯示此處原本直接取得驗證狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出流程完全依賴 HistoryEntryState，可能導致登出失敗</summary>

原本的登出流程在 `Navigation.HistoryEntryState` 為 null 時會 fallback 到 `SignOutManager.ValidateSignOutState()`。移除 `SignOutSessionStateManager` 後，若 `HistoryEntryState` 為 null（例如使用者直接輸入登出 URL），`ValidateSignOutRequestState()` 可能回傳 false，導致登出失敗並導向失敗頁面。這可能破壞向後相容性。建議確認 `ValidateSignOutRequestState()` 對 null 的處理，或保留某種 fallback 機制。

**判斷依據**：diff 中移除了原本的 fallback 邏輯，改為直接呼叫 `ValidateSignOutRequestState()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect 方法可能使用 null 的 InteractiveRequestUrl</summary>

在 `Redirect` 方法中，原本的條件是 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null`，現在改為只檢查 `_tokenResult.InteractionOptions != null`。若 `InteractionOptions` 不為 null 但 `InteractiveRequestUrl` 為 null，則會呼叫 `_navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, ...)`，可能導致 null 參數例外。建議保留對 `InteractiveRequestUrl` 的 null 檢查，或確保兩者同時存在。

**判斷依據**：diff 中移除了 `&& _tokenResult.InteractiveRequestUrl != null` 條件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 18451 (cache hit 1536) ｜ completion tokens 1032 ｜ PR #6</sub>