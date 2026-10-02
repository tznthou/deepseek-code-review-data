<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 分享啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯可能造成重複請求、狀態不同步，以及 TypeScript strict 模式被關閉，可能隱藏型別錯誤。建議優先修正輪詢邏輯與恢復 strict 模式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成重複請求與狀態不同步 | 0.95 |
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | [R16] TypeScript strict 模式被關閉 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.85 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢失敗時自動停用 Bluesky 可能造成非預期行為 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成重複請求與狀態不同步</summary>

在 `useEffect` 中，`confirmHandle` 被呼叫後，`confirmBlueskyHandleMutation.mutateAsync()` 會立即執行，但 `confirmHandle` 的依賴陣列為空，且 `confirmBlueskyHandleMutation` 並未包含在依賴中。這可能導致每次 `account?.blueskyEnabled` 或 `account?.blueskyHandleConfirmed` 改變時，`useEffect` 重新執行並建立新的 interval，但舊的 interval 可能未被清除，造成多個 interval 同時輪詢，導致重複請求。此外，`retryCountRef.current` 在每次 effect 執行時被重置為 0，可能導致重試次數計算不正確。建議將 `confirmBlueskyHandleMutation` 加入依賴陣列，或使用 `useCallback` 穩定其參考，並確保 interval 正確清除。

**判斷依據**：在 `useEffect` 中，`confirmHandle` 被呼叫，但 `confirmHandle` 的依賴陣列為空，且 `confirmBlueskyHandleMutation` 未包含在依賴中。這可能導致多個 interval 同時存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] TypeScript strict 模式被關閉</summary>

此 PR 將 `strict` 從 `true` 改為 `false`，違反了專案規範 R16（TypeScript 檔案必須啟用嚴格型別檢查）。這可能隱藏潛在的型別錯誤，降低程式碼安全性。建議恢復 `strict: true` 並修正相關型別錯誤。

**判斷依據**：diff 中顯示 `-    "strict": true,` 改為 `+    "strict": false,`，違反 R16。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解指出缺少 `accountFollows` 查詢的失效處理。這可能導致啟用 Bluesky 後，追蹤清單未更新，造成 UI 不一致。建議加入對應的 `queryClient.invalidateQueries` 呼叫。

**判斷依據**：程式碼中明確註解缺少 invalidation，且與啟用/停用時的處理不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢失敗時自動停用 Bluesky 可能造成非預期行為</summary>

當輪詢達到最大重試次數時，程式碼會自動呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。這可能導致使用者在未明確同意的情況下被停用，且若停用失敗，狀態可能不一致。建議改為顯示錯誤訊息並讓使用者手動重試或停用。

**判斷依據**：在 `MAX_CONFIRMATION_RETRIES` 達到後自動停用，可能不符合使用者預期。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11677 (cache hit 9344) ｜ completion tokens 1180 ｜ PR #10</sub>