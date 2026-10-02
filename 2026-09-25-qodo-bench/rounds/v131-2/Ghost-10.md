<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯的競態與錯誤處理、TypeScript strict 模式被關閉，以及 API 回傳型別與快取更新不一致。建議先修正 strict 模式與輪詢邏輯再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢邏輯可能造成競態與重複請求 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:104` | 輪詢失敗時自動停用 Bluesky 可能造成非預期行為 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 確認 handle 後未 invalidate 相關查詢 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 與 disableBluesky 回傳型別不明確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與 PR 目的無關，且會影響整個專案的型別檢查。建議恢復為 `true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` → `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢邏輯可能造成競態與重複請求</summary>

在 `useEffect` 中，`confirmHandle` 被以 `setInterval` 呼叫，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，未處理 mutation 的 pending 狀態。若前一次請求尚未完成，下一次 interval 又觸發，可能同時有多個請求在進行，導致重複確認或狀態不一致。建議在 `confirmHandle` 中檢查 mutation 是否正在進行，或使用 `isPending` 來避免重疊請求。

**判斷依據**：diff 中新增的 `confirmHandle` 函式與 `setInterval` 呼叫，未見對 mutation 狀態的檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:104</code> 輪詢失敗時自動停用 Bluesky 可能造成非預期行為</summary>

當輪詢次數超過 `MAX_CONFIRMATION_RETRIES` 時，程式會呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。這可能不是使用者預期的行為，且若停用失敗，錯誤未被處理。建議改為顯示錯誤訊息並讓使用者手動重試，或至少處理停用失敗的情況。

**判斷依據**：diff 中新增的錯誤處理區塊，直接呼叫 `disableBlueskyMutation.mutateAsync()` 而無錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 確認 handle 後未 invalidate 相關查詢</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解指出缺少 `accountFollows` 查詢的 invalidation。這可能導致 UI 顯示過時的追蹤狀態。建議加入對應的 `queryClient.invalidateQueries` 呼叫。

**判斷依據**：diff 中新增的註解明確指出缺少 invalidation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 與 disableBluesky 回傳型別不明確</summary>

`enableBluesky` 和 `disableBluesky` 現在不回傳任何值（`Promise<void>`），但呼叫端可能仍期待回傳值。建議明確標註回傳型別為 `Promise<void>`，並確認所有呼叫端已更新。

**判斷依據**：diff 中 `enableBluesky` 的實作，未指定回傳型別且無 return 值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9408 (cache hit 9344) ｜ completion tokens 1318 ｜ PR #10</sub>