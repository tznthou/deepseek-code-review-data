<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript 嚴格模式被關閉，以及 API 回傳型別與快取更新不一致。建議先修正輪詢 effect 的依賴與清理，並恢復 strict 模式。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢 effect 缺少 disableBlueskyMutation 依賴，可能使用過時閉包 | 0.95 |
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript 嚴格模式，降低型別安全 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢 interval 未在元件卸載或依賴變更時正確清理 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢重試次數上限後自動停用 Bluesky，可能造成非預期停用 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 與 disableBluesky 回傳型別未明確標示，可能導致呼叫端誤用 | 0.80 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | confirmBlueskyHandle 成功後未 invalidate accountFollows 查詢 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢 effect 缺少 disableBlueskyMutation 依賴，可能使用過時閉包</summary>

useEffect 的依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`，但 effect 內呼叫了 `disableBlueskyMutation.mutateAsync()`。若 `disableBlueskyMutation` 在元件生命週期內被重新建立（例如 queryClient 變更），effect 不會重新執行，導致呼叫到舊的 mutation 實例，可能造成請求失敗或狀態不同步。

建議將 `disableBlueskyMutation` 加入依賴陣列，或使用 ref 保存最新的 mutation 函式。

**判斷依據**：diff 中新增的 useEffect 內呼叫 `disableBlueskyMutation.mutateAsync()`，但依賴陣列註解寫著 `// disableBlueskyMutation is stable`，實際上並未加入依賴。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript 嚴格模式，降低型別安全</summary>

此 PR 將 `strict` 從 `true` 改為 `false`，違反專案規範 R16（TypeScript 檔案必須啟用嚴格型別檢查）。這可能隱藏潛在的型別錯誤，例如 `account?.blueskyHandle` 可能為 null 或 undefined 的處理。

建議恢復 `strict: true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的 `strict` 屬性從 `true` 改為 `false`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢 interval 未在元件卸載或依賴變更時正確清理</summary>

useEffect 的回傳清理函式僅清除 interval，但若 `account?.blueskyEnabled` 或 `account?.blueskyHandleConfirmed` 在輪詢期間改變，舊的 interval 會被清除，但新的 effect 會重新建立 interval。然而，若元件在 interval 觸發前卸載，清理函式會執行，但 interval 內的非同步操作（如 `confirmHandle`）可能仍在進行，導致狀態更新在卸載後發生。

建議在清理函式中加入取消機制，或使用 AbortController 取消進行中的請求。

**判斷依據**：diff 中新增的 useEffect 回傳清理函式僅清除 interval，未處理進行中的非同步操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢重試次數上限後自動停用 Bluesky，可能造成非預期停用</summary>

當 `retryCountRef.current >= MAX_CONFIRMATION_RETRIES` 時，程式會自動呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。若使用者只是暫時離開頁面或網路不穩，可能導致已啟用的 Bluesky 被意外停用，且使用者未被告知。

建議改為僅顯示錯誤訊息，不自動停用，或提供明確的確認對話框。

**判斷依據**：diff 中新增的 interval 回呼內，當重試次數超過上限時呼叫 `disableBlueskyMutation.mutateAsync()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 與 disableBluesky 回傳型別未明確標示，可能導致呼叫端誤用</summary>

`enableBluesky` 和 `disableBluesky` 方法沒有明確的回傳型別（隱含 `Promise<void>`），但呼叫端可能期望取得 handle 或其他資料。這可能導致未來修改時型別檢查失效。

建議明確標示回傳型別為 `Promise<void>`。

**判斷依據**：diff 中 `enableBluesky` 方法沒有回傳型別註記。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> confirmBlueskyHandle 成功後未 invalidate accountFollows 查詢</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解提到缺少 `accountFollows` 查詢的 invalidation。這可能導致追蹤清單顯示過時資料。

建議加入對應的 query invalidation。

**判斷依據**：diff 中新增的 `useConfirmBlueskyHandleMutationForUser` 內有註解指出缺少 invalidation。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11763 (cache hit 9344) ｜ completion tokens 1537 ｜ PR #10</sub>