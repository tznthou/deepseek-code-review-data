<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯的競態與錯誤處理、TypeScript strict 模式被關閉，以及 API 版本升級可能造成的相容性問題。建議優先修正 strict 模式與輪詢邏輯中的潛在問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成競態或重複請求 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107` | 輪詢失敗時自動停用 Bluesky 可能非預期 | 0.75 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:712` | API 版本升級可能造成相容性問題 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更應有充分理由，否則應恢復為 `true` 並修正相關型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` 改為 `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成競態或重複請求</summary>

在 `useEffect` 中設置 `setInterval` 並在每次觸發時呼叫 `confirmHandle`，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，若前一次請求尚未完成，可能導致重疊請求。此外，`retryCountRef` 在每次 effect 重新執行時重置為 0，若依賴項頻繁變化，可能導致輪詢次數超過預期。建議使用 `setTimeout` 遞迴或確保請求完成後再安排下一次。

**判斷依據**：diff 中新增的輪詢邏輯，使用 setInterval 且未等待前一次請求完成。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107</code> 輪詢失敗時自動停用 Bluesky 可能非預期</summary>

當輪詢達到最大次數時，程式碼會自動呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。這可能導致使用者在未明確同意的情況下被停用，且若停用失敗，錯誤未被處理。建議改為僅顯示錯誤訊息，讓使用者手動決定是否停用。

**判斷依據**：diff 中在輪詢失敗時自動呼叫 disableBlueskyMutation。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到缺少 `accountFollows` 查詢的失效處理。這可能導致相關資料不同步。建議補上對應的 `queryClient.invalidateQueries`。

**判斷依據**：diff 中新增的註解明確指出缺少失效處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:712</code> API 版本升級可能造成相容性問題</summary>

API 路徑從 v1 改為 v2，需確認後端已部署對應版本，否則前端呼叫會失敗。建議在 PR 描述中確認後端相容性，或提供版本協商機制。

**判斷依據**：diff 中 API 路徑從 v1 改為 v2。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9444 (cache hit 1536) ｜ completion tokens 1208 ｜ PR #10</sub>