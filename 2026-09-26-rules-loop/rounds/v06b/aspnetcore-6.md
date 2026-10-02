<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除多個已標記為過時的 API，並更新相關程式碼與測試。主要風險在於移除 SignOutSessionStateManager 後，登出流程的 CSRF 防護改為完全依賴 HistoryEntryState，可能影響舊版用戶端或特定情境下的安全性。此外，AccessTokenNotAvailableException.Redirect() 的變更可能導致在缺少 InteractiveRequestUrl 時導航至 null。整體而言，移除動作合理，但需確認相容性與邊界情況。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281` | 登出 CSRF 防護僅依賴 HistoryEntryState，可能降低安全性 | 0.80 |
| ⚠️ | Major | `src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44` | Redirect() 可能導航至 null URL | 0.75 |
| 🔸 | Minor | `src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291` | 新增 Task.Yield() 可能造成不必要的延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281</code> 登出 CSRF 防護僅依賴 HistoryEntryState，可能降低安全性</summary>

移除 SignOutSessionStateManager 後，登出驗證僅檢查 HistoryEntryState。若用戶端不支援 HistoryEntryState（例如舊版瀏覽器或某些 WebView），登出請求將被視為無效，導致登出失敗。此外，若攻擊者能操控 HistoryEntryState（例如透過 XSS），可能繞過 CSRF 防護。建議保留某種伺服器端或 sessionStorage 的驗證機制，或確認所有支援的用戶端均能正確設定 HistoryEntryState。

**判斷依據**：diff 中移除了 SignOutManager 的注入與使用，並將條件簡化為僅檢查 ValidateSignOutRequestState()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44</code> Redirect() 可能導航至 null URL</summary>

在 else 分支中，原本使用 RedirectUrl（可能為 null 但已標記為過時），現在改用 InteractiveRequestUrl。若 InteractiveRequestUrl 為 null（例如舊版程式碼建立的 AccessTokenResult 未設定此屬性），則 NavigateTo 會收到 null，可能導致例外或未定義行為。建議加入 null 檢查或確保所有建立 AccessTokenResult 的路徑都設定 InteractiveRequestUrl。

**判斷依據**：diff 顯示將 _tokenResult.RedirectUrl! 改為 _tokenResult.InteractiveRequestUrl!，但未檢查 null。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291</code> 新增 Task.Yield() 可能造成不必要的延遲</summary>

在取得 AuthenticationState 之前加入 await Task.Yield()，可能是為了避免同步上下文問題，但若無明確理由，可能只是增加延遲。建議確認此變更的必要性，或移除。

**判斷依據**：diff 中新增此行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16929 (cache hit 16896) ｜ completion tokens 762 ｜ PR #6</sub>