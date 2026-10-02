<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript strict 模式被關閉，以及 API 回傳型別與快取更新的一致性。建議優先修正 strict 關閉與輪詢相關的潛在問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:96` | 輪詢 effect 缺少對 disableBlueskyMutation 的依賴 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢可能產生競態條件 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 確認 handle 後未 invalidate 相關查詢 | 0.80 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 回傳型別不明確 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32` | loading 初始狀態依賴 account 可能導致閃爍 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與 PR 目的無關，且會影響整個專案的型別檢查。建議恢復為 `true`，並修正任何因 strict 而產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` → `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:96</code> 輪詢 effect 缺少對 disableBlueskyMutation 的依賴</summary>

在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`。雖然註解聲稱 mutation 是穩定的，但 React Query 的 mutation 物件在每次 render 時可能重新建立，若其身份改變，effect 可能使用到過時的 mutation 實例，導致錯誤或記憶體洩漏。建議將 `disableBlueskyMutation` 加入依賴陣列，或使用 `useCallback` 穩定其參考。

**判斷依據**：diff 中新增的 useEffect 依賴陣列缺少 `disableBlueskyMutation`，且註解聲稱其穩定但未提供保證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢可能產生競態條件</summary>

`confirmHandle` 使用 `mutateAsync` 但未處理錯誤，且輪詢間隔固定為 5 秒。若前一次請求尚未完成，下一次輪詢可能同時發出多個請求，導致伺服器壓力或狀態不一致。此外，若 `confirmBlueskyHandleMutation` 失敗（例如網路錯誤），錯誤未被捕獲，可能造成 unhandled rejection。建議在 `confirmHandle` 中加入錯誤處理，並考慮使用 `isPending` 或鎖定機制避免重疊請求。

**判斷依據**：diff 中新增的 `confirmHandle` 函式未處理 `mutateAsync` 的 rejection，且輪詢 interval 可能觸發重疊呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 確認 handle 後未 invalidate 相關查詢</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解指出缺少 `accountFollows` 查詢的 invalidation。這可能導致 UI 顯示過時的追蹤狀態，例如啟用 Bluesky 後應自動追蹤 brid.gy 帳戶，但相關列表不會更新。建議加入對應的 `queryClient.invalidateQueries` 呼叫。

**判斷依據**：diff 中新增的 mutation 內有明確註解指出缺少 invalidation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 回傳型別不明確</summary>

`enableBluesky` 方法現在不回傳任何值（`Promise<void>`），但呼叫端 `useEnableBlueskyMutationForUser` 的 `onSuccess` 不再使用回傳值，因此功能上可行。然而，若未來需要回傳資料，型別不明確可能造成誤用。建議明確標註回傳型別為 `Promise<void>`。

**判斷依據**：diff 中 `enableBluesky` 方法缺少回傳型別註記。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32</code> loading 初始狀態依賴 account 可能導致閃爍</summary>

`loading` 的初始值使用 `useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed)`，但 `account` 在首次 render 時可能尚未載入（undefined），導致初始為 false。當 account 載入後，effect 會設定 loading，但可能造成短暫的 UI 閃爍。建議在 account 載入前顯示載入指示，或延後判斷。

**判斷依據**：diff 中新增的 useState 初始化依賴非同步載入的 account。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9408 (cache hit 1408) ｜ completion tokens 1629 ｜ PR #10</sub>