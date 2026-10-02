<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enable）再確認 handle（confirm-handle），並新增輪詢機制。主要風險在於前端輪詢邏輯可能造成重複請求與狀態不一致，且 TypeScript 嚴格模式被關閉，降低型別安全。建議先修正輪詢的相依性與競態問題，並恢復 strict 模式。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] TypeScript 嚴格模式被關閉 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121` | 輪詢 effect 缺少 disableBlueskyMutation 相依性，可能使用過時閉包 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | confirmHandle 使用空相依陣列，可能導致過時閉包 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢可能重複觸發 confirmHandle，造成多個並行請求 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢失敗後呼叫 disableBlueskyMutation 可能造成非預期停用 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] TypeScript 嚴格模式被關閉</summary>

此變更將 `strict` 從 `true` 改為 `false`，違反專案規範 R16（TypeScript Files Must Enable Strict Type Checking）。關閉嚴格模式會降低型別安全，可能隱藏潛在的執行時期錯誤。請恢復 `strict: true` 並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` 改為 `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121</code> 輪詢 effect 缺少 disableBlueskyMutation 相依性，可能使用過時閉包</summary>

`useEffect` 的相依陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`，但 effect 內呼叫了 `disableBlueskyMutation.mutateAsync()`。雖然註解聲稱 mutation 是穩定的，但 React Query 的 mutation 物件在重新渲染時可能改變，若未列入相依性，可能導致使用過時的 mutation 實例，造成請求錯誤或狀態不同步。建議將 `disableBlueskyMutation` 加入相依陣列，或使用 `useCallback` 包裝 mutation 函式。

**判斷依據**：diff 中新增的 useEffect 相依陣列未包含 disableBlueskyMutation，但 effect 內呼叫了 disableBlueskyMutation.mutateAsync()

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> confirmHandle 使用空相依陣列，可能導致過時閉包</summary>

`confirmHandle` 使用 `useCallback` 且相依陣列為空，但內部呼叫了 `confirmBlueskyHandleMutation.mutateAsync()`。若 mutation 物件在重新渲染時改變，此回呼將持有舊的 mutation 實例，可能導致請求失敗或狀態更新錯誤。建議將 `confirmBlueskyHandleMutation` 加入相依陣列，或使用 `useMutation` 提供的穩定函式。

**判斷依據**：diff 中新增的 confirmHandle useCallback 相依陣列為空，但使用 confirmBlueskyHandleMutation

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢可能重複觸發 confirmHandle，造成多個並行請求</summary>

在 `useEffect` 中設定 `setInterval` 每 5 秒呼叫 `confirmHandle`，但 `confirmHandle` 內呼叫 `confirmBlueskyHandleMutation.mutateAsync()` 並未檢查是否已有進行中的請求。若前一次請求尚未完成，下一次輪詢會再發起新請求，可能導致多個並行請求，增加伺服器負載並可能造成狀態競爭。建議在 `confirmHandle` 中檢查 mutation 的 `isPending` 狀態，或使用 `mutate` 搭配 `onSuccess` 回呼。

**判斷依據**：diff 中新增的 setInterval 內直接呼叫 confirmHandle，無並行防護

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢失敗後呼叫 disableBlueskyMutation 可能造成非預期停用</summary>

當輪詢達到最大重試次數時，程式會呼叫 `disableBlueskyMutation.mutateAsync()` 來停用 Bluesky。但若使用者已手動停用或狀態已變更，此舉可能造成非預期的停用。建議在停用前檢查目前狀態，或提供更明確的錯誤處理。

**判斷依據**：diff 中新增的錯誤處理邏輯

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解指出缺少 `accountFollows` 查詢的失效處理。這可能導致相關的追蹤清單未更新，顯示過時資料。建議加入對應的 `queryClient.invalidateQueries` 呼叫。

**判斷依據**：diff 中新增的註解指出缺少失效處理

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11753 (cache hit 11648) ｜ completion tokens 1672 ｜ PR #10</sub>