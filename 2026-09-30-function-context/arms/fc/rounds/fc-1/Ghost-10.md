<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用再輪詢確認 handle，並將 API 從 v1 升級到 v2。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript strict 模式被關閉，以及 API 回應型別與快取更新的一致性。建議優先修正 strict 設定與輪詢相關的潛在問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:78` | 輪詢 effect 缺少對 disableBlueskyMutation 的依賴 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢可能重複觸發 confirmHandle | 0.75 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | confirmHandle 的錯誤處理可能導致未處理的 rejection | 0.70 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | useConfirmBlueskyHandleMutationForUser 缺少 accountFollows 查詢的 invalidate | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:29` | Account 介面中 blueskyHandle 型別改為 string \| null 可能影響其他程式碼 | 0.60 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 和 disableBluesky 的回傳型別未明確標示 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與 PR 目的無關，且會影響整個專案的型別檢查。建議恢復為 `true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` → `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:78</code> 輪詢 effect 缺少對 disableBlueskyMutation 的依賴</summary>

在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅包含 `account?.blueskyEnabled`, `account?.blueskyHandleConfirmed`, `confirmHandle`，並註解 `disableBlueskyMutation is stable`。若 mutation 函式因 hook 重新渲染而改變（例如 queryClient 或 handle 變化），可能導致 effect 使用過時的 mutation 函式。建議將 `disableBlueskyMutation` 加入依賴陣列，或確認其穩定性。

**判斷依據**：diff 中新增的 useEffect 依賴陣列未包含 `disableBlueskyMutation`，且註解聲稱其穩定。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢可能重複觸發 confirmHandle</summary>

在 `setInterval` 中呼叫 `confirmHandle()`，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`。若前一次請求尚未完成，下一次 interval 仍會觸發新的請求，可能導致多個併發請求。建議在 `confirmHandle` 中加入進行中標誌，或使用 `isLoading` 狀態防止重入。

**判斷依據**：diff 中新增的 setInterval 回呼直接呼叫 confirmHandle，無任何防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> confirmHandle 的錯誤處理可能導致未處理的 rejection</summary>

`confirmHandle` 使用 `.then()` 但沒有 `.catch()`。若 `confirmBlueskyHandleMutation.mutateAsync()` 失敗（例如網路錯誤），會產生未處理的 Promise rejection。建議加入 `.catch()` 處理錯誤，或使用 try/catch。

**判斷依據**：diff 中新增的 confirmHandle 函式缺少錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> useConfirmBlueskyHandleMutationForUser 缺少 accountFollows 查詢的 invalidate</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但沒有 invalidate `accountFollows` 查詢。註解也提到「Missing invalidation of accountFollows query that should happen here」。若確認 handle 後會影響 following 列表（例如 brid.gy 帳戶的追蹤狀態），UI 可能不會即時更新。建議加入相應的 invalidateQueries。

**判斷依據**：diff 中新增的 mutation 缺少 invalidateQueries，且有註解指出。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:29</code> Account 介面中 blueskyHandle 型別改為 string | null 可能影響其他程式碼</summary>

`blueskyHandle` 從 `string` 改為 `string | null`，並新增 `blueskyHandleConfirmed`。這可能導致其他使用 `blueskyHandle` 的地方需要處理 null，若未處理可能產生執行時期錯誤。建議搜尋所有使用處並確認 null 處理。

**判斷依據**：diff 中 Account 介面的變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 和 disableBluesky 的回傳型別未明確標示</summary>

`enableBluesky` 和 `disableBluesky` 沒有標示回傳型別（隱含 `Promise<void>`），但呼叫端可能期望回傳值。建議明確標示 `Promise<void>` 以增加可讀性。

**判斷依據**：diff 中新增的方法未標示回傳型別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23267 (cache hit 1536) ｜ completion tokens 1861 ｜ PR #10</sub>