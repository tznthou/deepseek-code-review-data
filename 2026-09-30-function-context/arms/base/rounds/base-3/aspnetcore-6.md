<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，並更新相關程式碼與測試。主要風險在於移除 SignOutSessionStateManager 後，登出流程的 CSRF 防護改為完全依賴 HistoryEntryState，若瀏覽器不支援或狀態遺失，可能導致登出失敗或安全疑慮。另外，AccessTokenNotAvailableException.Redirect() 的變更可能造成 NullReferenceException。整體而言，移除過時 API 的方向正確，但需確認登出流程的相容性與錯誤處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出流程移除 SignOutSessionStateManager 後可能喪失 CSRF 防護 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增的 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出流程移除 SignOutSessionStateManager 後可能喪失 CSRF 防護</summary>

原本的登出驗證會同時檢查 HistoryEntryState 與 SignOutSessionStateManager，現在僅依賴 HistoryEntryState。若瀏覽器不支援 History API 或狀態遺失，ValidateSignOutRequestState() 可能回傳 false，導致登出失敗。此外，若攻擊者能操控 HistoryEntryState，可能繞過 CSRF 防護。建議確認 HistoryEntryState 的可靠性，或保留備援機制。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為只檢查 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException</summary>

原本在 RedirectUrl 為 null 時會使用 null-forgiving 運算子，但現在直接使用 InteractiveRequestUrl!。若 InteractiveRequestUrl 為 null，NavigateTo 可能拋出 ArgumentNullException 或導致非預期行為。建議加入 null 檢查或確保該屬性在需要時必定有值。

**判斷依據**：diff 中將原本的 RedirectUrl 改為 InteractiveRequestUrl，且未增加 null 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增的 Task.Yield() 可能造成不必要的延遲</summary>

在取得 AuthenticationState 前加入 await Task.Yield()，可能是為了避免同步阻塞，但若呼叫端已非同步，此舉可能增加延遲。建議確認其必要性，或改用 ConfigureAwait(false) 以提升效能。

**判斷依據**：diff 中新增了 await Task.Yield(); 於取得 AuthenticationState 之前。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 14754 (cache hit 14720) ｜ completion tokens 757 ｜ PR #6</sub>