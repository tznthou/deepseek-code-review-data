<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enable），再輪詢確認 handle（confirm-handle）。主要風險在於前端輪詢邏輯可能造成重複請求、競態與錯誤處理不完整；同時將 tsconfig 的 strict 關閉，違反專案規範 R16，可能隱藏型別錯誤。建議優先修正 strict 設定與輪詢邏輯。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成重複請求與競態 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢失敗時未處理錯誤，可能導致無限重試 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢完成後未清除 interval，可能造成記憶體洩漏 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 與 disableBluesky 未回傳任何值 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false`，違反專案規範 R16（TypeScript 必須啟用 strict 與 noImplicitAny）。這會降低型別安全，可能隱藏潛在的執行時期錯誤。建議恢復 `strict: true` 並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` → `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成重複請求與競態</summary>

在 `useEffect` 中設定 `setInterval` 呼叫 `confirmHandle`，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，且未檢查 mutation 是否正在進行中。若前一次請求尚未完成，下一次 interval 又觸發，可能同時發出多個請求，導致伺服器負擔或狀態不一致。建議在 `confirmHandle` 中加入 `isPending` 檢查，或使用 `setTimeout` 遞迴取代 `setInterval`，確保前一次完成後才進行下一次。

**判斷依據**：diff 中新增的 `useEffect` 區塊，`confirmHandle` 未檢查 mutation 狀態。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢失敗時未處理錯誤，可能導致無限重試</summary>

`confirmHandle` 呼叫 `confirmBlueskyHandleMutation.mutateAsync()` 但未捕捉錯誤。若請求失敗（例如網路錯誤），promise 會被拒絕，但 interval 仍會繼續觸發，直到達到 `MAX_CONFIRMATION_RETRIES` 才停止。這可能造成不必要的請求與使用者困惑。建議在 `confirmHandle` 中加入 `.catch()` 處理錯誤，並考慮在錯誤時停止輪詢或顯示錯誤訊息。

**判斷依據**：diff 中 `confirmHandle` 的實作，未處理 promise rejection。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢完成後未清除 interval，可能造成記憶體洩漏</summary>

在 `useEffect` 的回傳函式中清除 interval，但若 `account?.blueskyHandleConfirmed` 變為 true 時，effect 會重新執行並清除 interval，這部分正確。然而，若 `confirmHandle` 成功設定 `handleConfirmed` 為 true，但 `account?.blueskyHandleConfirmed` 尚未更新（例如快取未同步），interval 可能繼續執行，直到 effect 重新觸發。建議在 `confirmHandle` 成功後主動清除 interval，或依賴 effect 的依賴陣列確保正確清理。

**判斷依據**：diff 中 effect 的回傳函式，但未在成功時立即清除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 狀態可能改變（例如自動追蹤 brid.gy 帳號），但未 invalidate 相關查詢，可能導致 UI 顯示過時資料。建議加入對應的 `queryClient.invalidateQueries`。

**判斷依據**：diff 中新增的 hook，註解明確指出缺少 invalidation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 與 disableBluesky 未回傳任何值</summary>

`enableBluesky` 和 `disableBluesky` 現在不回傳任何值（`Promise<void>`），但呼叫端可能依賴回傳值。在測試中已改為不檢查回傳，但其他未修改的呼叫端可能受到影響。建議確認所有呼叫端都已更新，或保留回傳值以維持向後相容。

**判斷依據**：diff 中 `enableBluesky` 的簽名從 `Promise<string>` 改為無回傳。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11753 (cache hit 9344) ｜ completion tokens 1675 ｜ PR #10</sub>