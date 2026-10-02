<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enableBluesky）再輪詢確認 handle（confirmBlueskyHandle）。主要風險在於前端輪詢邏輯可能造成重複請求、錯誤處理不完整，以及關閉 TypeScript strict 模式降低型別安全。建議優先修正輪詢的競態與錯誤處理，並恢復 strict 模式。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成重複請求與競態 | 0.90 |
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式降低型別安全 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢失敗時未處理錯誤，可能導致無限重試 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.80 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:86` | 輪詢完成後未清除 interval 可能造成記憶體洩漏 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32` | 輪詢期間使用者可能重複啟用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成重複請求與競態</summary>

在 `useEffect` 中，每次 `account?.blueskyEnabled` 或 `account?.blueskyHandleConfirmed` 改變時都會建立新的 `setInterval`。但 `confirmHandle` 使用 `useCallback` 且依賴為空，內部呼叫的 `confirmBlueskyHandleMutation.mutateAsync()` 並未檢查是否已有進行中的請求。若元件重新渲染或依賴變化，可能同時存在多個 interval，導致重複呼叫 API。此外，`retryCountRef.current` 在 interval 內遞增，但若多個 interval 同時執行，計數會不準確。建議使用單一 interval 並在 effect 清理時清除，或改用遞迴 `setTimeout` 並在每次呼叫前檢查是否已有請求。

**判斷依據**：diff 中新增的 useEffect 內建立 setInterval，且 confirmHandle 無防重複機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式降低型別安全</summary>

此 PR 將 `strict` 從 `true` 改為 `false`，違反規範 R16。這會關閉所有 strict 相關檢查（包括 `noImplicitAny`、`strictNullChecks` 等），可能隱藏潛在的型別錯誤。建議恢復 `strict: true` 並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢失敗時未處理錯誤，可能導致無限重試</summary>

`confirmHandle` 呼叫 `confirmBlueskyHandleMutation.mutateAsync()` 但未捕捉錯誤。若 API 回傳非 2xx（例如 500），promise 會被 reject，但 interval 仍會繼續執行，直到達到 `MAX_CONFIRMATION_RETRIES`。這可能造成不必要的請求與使用者困惑。建議在 `confirmHandle` 中加入 `.catch()` 處理錯誤，並考慮在特定錯誤（如 404）時停止輪詢。

**判斷依據**：diff 中 confirmHandle 未處理 mutateAsync 的 rejection。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解指出「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 列表可能改變（例如自動追蹤 brid.gy 帳號），但未呼叫 `queryClient.invalidateQueries` 來更新相關查詢。這可能導致 UI 顯示過時的 following 資料。建議加入對應的 invalidateQueries 呼叫。

**判斷依據**：diff 中新增的註解明確指出缺少 invalidation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:86</code> 輪詢完成後未清除 interval 可能造成記憶體洩漏</summary>

在 `useEffect` 中，當 `account?.blueskyHandleConfirmed` 為 true 時，會執行 `setHandleConfirmed(true)` 和 `setLoading(false)`，但未清除先前建立的 interval。若元件在 interval 仍存在時重新渲染，可能導致多個 interval 同時執行。建議在 effect 的 cleanup 函式中清除 interval，或在確認後立即清除。

**判斷依據**：diff 中確認後未清除 interval。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32</code> 輪詢期間使用者可能重複啟用</summary>

在 `loading` 狀態下，啟用按鈕被禁用，但使用者仍可透過其他方式（例如重新整理頁面）觸發新的啟用流程。若帳號已啟用但尚未確認 handle，`loading` 初始值為 `account?.blueskyEnabled && !account?.blueskyHandleConfirmed`，可能導致重複呼叫 `enableBluesky`。建議在啟用前檢查是否已有進行中的啟用流程。

**判斷依據**：diff 中 loading 初始值設定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11743 (cache hit 11648) ｜ completion tokens 1734 ｜ PR #10</sub>