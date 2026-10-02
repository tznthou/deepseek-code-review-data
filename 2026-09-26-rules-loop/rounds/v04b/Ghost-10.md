<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要風險在於前端輪詢邏輯可能造成競態與資源浪費，且關閉了 TypeScript strict 模式，降低型別安全。建議先修正輪詢邏輯與恢復 strict 模式。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式 | 0.95 |
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成多個並行 interval 與記憶體洩漏 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢期間可能重複觸發 mutation | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢失敗後自動停用 Bluesky 可能非預期 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 違反專案規範 R16，且會降低型別安全，可能隱藏潛在錯誤。請恢復 `strict: true` 並修正相關型別錯誤。

**判斷依據**：diff 中 `"strict": true` 改為 `"strict": false`，違反 R16。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成多個並行 interval 與記憶體洩漏</summary>

在 `useEffect` 中，依賴陣列包含 `account?.blueskyEnabled` 和 `account?.blueskyHandleConfirmed`。當 `confirmBlueskyHandleMutation` 成功更新快取後，`account` 物件會改變，導致 effect 重新執行。但舊的 interval 可能尚未清除，造成多個 interval 同時輪詢。此外，`confirmHandle` 使用 `useCallback` 且依賴為空，但內部呼叫的 `confirmBlueskyHandleMutation` 可能因重新渲染而改變，但由於依賴為空，可能使用到舊的 mutation 函式。建議使用 `useRef` 管理 interval，並在 effect 中明確清除，或改用 `setTimeout` 遞迴。

**判斷依據**：effect 依賴 `account?.blueskyEnabled` 和 `account?.blueskyHandleConfirmed`，當 mutation 成功後，account 更新，effect 重新執行，但舊 interval 可能未清除。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解指出缺少 `accountFollows` 查詢的失效。這可能導致啟用後追蹤列表未更新。請加入相應的 `queryClient.invalidateQueries`。

**判斷依據**：程式碼中明確註解缺少 invalidation。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢期間可能重複觸發 mutation</summary>

在 `confirmHandle` 中，每次呼叫都會執行 `confirmBlueskyHandleMutation.mutateAsync()`，但沒有檢查是否已有進行中的 mutation。若前一次請求尚未完成，可能導致重複請求。建議加入 `isPending` 檢查或使用 `mutate` 並依賴 mutation 狀態。

**判斷依據**：`confirmHandle` 無條件呼叫 mutation，未檢查 `isPending`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢失敗後自動停用 Bluesky 可能非預期</summary>

當達到最大重試次數時，程式碼自動呼叫 `disableBlueskyMutation.mutateAsync()`。這可能導致使用者僅因暫時性錯誤就被停用，且沒有提供手動重試選項。建議改為顯示錯誤並允許使用者手動重試或停用。

**判斷依據**：在達到最大重試次數後自動停用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10633 (cache hit 10624) ｜ completion tokens 1328 ｜ PR #10</sub>