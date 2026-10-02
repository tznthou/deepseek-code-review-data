<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯的競態與錯誤處理：`confirmHandle` 未處理 mutation 錯誤，可能導致未捕獲的 rejection；`useEffect` 中依賴 `account?.blueskyHandleConfirmed` 但輪詢成功後未更新快取，可能造成重複輪詢；此外 `tsconfig.json` 將 `strict` 改為 `false`，違反專案規範 R16，降低型別安全。整體方向合理，但需修正上述問題後方可合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] TypeScript strict mode disabled | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69` | confirmHandle 未處理 mutation 錯誤，可能導致未捕獲的 rejection | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69` | 輪詢成功後未更新快取，可能導致重複輪詢 | 0.75 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢間隔內可能重複呼叫 confirmHandle | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 達到最大重試次數後呼叫 disableBlueskyMutation 可能造成非預期狀態 | 0.60 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32` | 初始 loading 狀態依賴 account 資料，可能造成閃爍 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] TypeScript strict mode disabled</summary>

將 `strict` 從 `true` 改為 `false` 違反專案規範 R16（TypeScript Files Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的執行時期錯誤。請恢復為 `true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` 改為 `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69</code> confirmHandle 未處理 mutation 錯誤，可能導致未捕獲的 rejection</summary>

`confirmHandle` 呼叫 `confirmBlueskyHandleMutation.mutateAsync().then(...)` 但沒有 `.catch`。若 mutation 失敗（例如網路錯誤或 429），會產生未處理的 Promise rejection，可能導致瀏覽器顯示錯誤或影響其他邏輯。建議加上 `.catch` 處理錯誤，例如顯示 toast 或停止輪詢。

**判斷依據**：在 `confirmHandle` 函式中，`mutateAsync()` 回傳的 Promise 僅有 `.then`，沒有 `.catch`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69</code> 輪詢成功後未更新快取，可能導致重複輪詢</summary>

在 `confirmHandle` 成功取得 handle 後，僅呼叫 `setHandleConfirmed(true)`，但未更新 React Query 快取中的 `blueskyHandleConfirmed`。因此 `account?.blueskyHandleConfirmed` 仍為 `false`，`useEffect` 的依賴項不會改變，可能導致輪詢繼續進行，直到達到最大重試次數。建議在成功後呼叫 `updateAccountBlueskyCache` 或 invalidate 相關查詢。

**判斷依據**：`confirmHandle` 僅設定 local state，未更新全域快取；而 `useEffect` 依賴 `account?.blueskyHandleConfirmed`，若快取未更新，該值不會改變。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢間隔內可能重複呼叫 confirmHandle</summary>

`useEffect` 設定 `setInterval` 每 5 秒呼叫 `confirmHandle`，但 `confirmHandle` 本身是 async 且可能耗時超過 5 秒。若前一次請求尚未完成，下一次 interval 又觸發，可能導致多個並行請求。建議在 `confirmHandle` 中加入防護，例如檢查是否已有進行中的請求，或使用 `setTimeout` 遞迴取代 `setInterval`。

**判斷依據**：`setInterval` 固定間隔觸發，未考慮非同步操作的完成時間。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 達到最大重試次數後呼叫 disableBlueskyMutation 可能造成非預期狀態</summary>

當輪詢達到最大次數時，程式會呼叫 `disableBlueskyMutation.mutateAsync()` 來停用 Bluesky。但若使用者已手動停用或狀態已變更，此舉可能造成不必要的 API 呼叫或狀態不一致。建議先檢查目前狀態再決定是否停用。

**判斷依據**：在 `setInterval` 的 callback 中，當 `retryCountRef.current >= MAX_CONFIRMATION_RETRIES` 時執行停用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32</code> 初始 loading 狀態依賴 account 資料，可能造成閃爍</summary>

`useState` 的初始值使用 `account?.blueskyEnabled && !account?.blueskyHandleConfirmed`，但 `account` 在首次 render 時可能尚未載入（undefined），導致初始 loading 為 false。之後當 account 載入且符合條件時，`useEffect` 會設定 loading 為 true，可能造成 UI 閃爍。建議在 account 載入前顯示 loading 或延後判斷。

**判斷依據**：初始 state 依賴非同步取得的 account 資料。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11753 (cache hit 11648) ｜ completion tokens 1669 ｜ PR #10</sub>