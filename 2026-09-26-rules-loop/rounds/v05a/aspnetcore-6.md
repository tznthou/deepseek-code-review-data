<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，並更新相關程式碼與測試。主要風險在於移除 SignOutSessionStateManager 後，登出流程的 CSRF 防護完全依賴 HistoryEntryState，若瀏覽器不支援或狀態遺失，可能導致登出失敗或安全疑慮。此外，AccessTokenNotAvailableException.Redirect() 的變更可能因 InteractiveRequestUrl 為 null 而拋出例外。建議確認這些行為變更的相容性與測試覆蓋。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出 CSRF 防護僅依賴 HistoryEntryState，可能導致登出失敗或安全風險 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38` | Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290` | 新增的 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出 CSRF 防護僅依賴 HistoryEntryState，可能導致登出失敗或安全風險</summary>

移除了 SignOutSessionStateManager 後，登出驗證僅檢查 `ValidateSignOutRequestState()`，該方法依賴 `Navigation.HistoryEntryState`。若瀏覽器不支援 History API 或狀態遺失（例如使用者直接輸入登出 URL），`HistoryEntryState` 可能為 null，導致驗證失敗並導向登出失敗頁面。這可能破壞直接登出連結的使用情境，且若攻擊者能偽造 HistoryEntryState，可能繞過 CSRF 防護。建議確認此變更的相容性，並考慮保留某種後備驗證機制。

**判斷依據**：diff 中移除了原本的 `(Navigation.HistoryEntryState == null && !await SignOutManager.ValidateSignOutState())` 條件，改為僅依賴 `ValidateSignOutRequestState()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38</code> Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 `NavigateToLogin`，否則使用 `RedirectUrl`。現在改為只要 `InteractionOptions != null` 就呼叫 `NavigateToLogin(_tokenResult.InteractiveRequestUrl, ...)`，但 `InteractiveRequestUrl` 可能為 null（例如舊版建立的 AccessTokenResult 只設定 RedirectUrl）。這會導致 NullReferenceException。建議檢查 `InteractiveRequestUrl` 是否為 null，或確保所有建構路徑都會設定該屬性。

**判斷依據**：diff 中條件從 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 改為僅 `_tokenResult.InteractionOptions != null`，且 `InteractiveRequestUrl` 屬性可能為 null（參見 AccessTokenResult 的建構子）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290</code> 新增的 Task.Yield() 可能造成不必要的延遲</summary>

在取得 AuthenticationState 之前新增了 `await Task.Yield();`，這會強制非同步切換，可能只是為了避免同步上下文問題，但若無明確理由，可能增加延遲。建議確認其必要性，或移除。

**判斷依據**：diff 中新增了 `await Task.Yield();` 及註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16873 (cache hit 14720) ｜ completion tokens 939 ｜ PR #6</sub>