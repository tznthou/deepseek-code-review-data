<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先呼叫 enable 再輪詢 confirm-handle，並更新相關 API 與 UI。主要風險在於前端輪詢邏輯可能造成重複請求或狀態不同步，且關閉了 TypeScript 嚴格模式，降低型別安全。建議先修正輪詢與錯誤處理，並恢復 strict 模式。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript 嚴格模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢可能重複觸發 confirmBlueskyHandleMutation | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | 輪詢失敗時未處理錯誤，可能導致無限重試 | 0.75 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢期間元件 unmount 時未清除 interval | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript 嚴格模式</summary>

此變更將 `strict` 設為 `false`，違反規範 R16（TypeScript 檔案必須啟用嚴格型別檢查）。這會降低型別安全，可能隱藏潛在的執行時期錯誤。請恢復為 `true` 並修正任何型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` 改為 `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢可能重複觸發 confirmBlueskyHandleMutation</summary>

在 `useEffect` 中設定 `setInterval` 每 5 秒呼叫 `confirmHandle`，但 `confirmHandle` 內部呼叫 `confirmBlueskyHandleMutation.mutateAsync()`。若前一次請求尚未完成，下一次 interval 仍會觸發，可能導致多個併發請求。建議在 `confirmHandle` 中檢查 mutation 是否正在進行（例如使用 `isPending` 狀態），或使用 `setTimeout` 遞迴方式確保前一次完成後再排下一次。

**判斷依據**：diff 中新增的 `useEffect` 區塊，包含 `setInterval` 與 `confirmHandle` 呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> 輪詢失敗時未處理錯誤，可能導致無限重試</summary>

`confirmHandle` 中呼叫 `confirmBlueskyHandleMutation.mutateAsync()` 但未捕捉錯誤。若請求失敗（例如網路錯誤），promise 會被拒絕，但 interval 仍會繼續觸發，直到達到最大重試次數。建議在 `confirmHandle` 中加入 `.catch()` 處理錯誤，或讓 `useEffect` 監聽 mutation 的錯誤狀態。

**判斷依據**：diff 中新增的 `confirmHandle` 函式，未處理 `mutateAsync` 的 rejection。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢期間元件 unmount 時未清除 interval</summary>

`useEffect` 的回傳函式會清除 interval，但若元件在 interval 觸發前 unmount，`clearInterval` 仍會執行，這沒有問題。然而，若 `confirmBlueskyHandleMutation` 正在進行中，unmount 後其回呼仍可能執行並呼叫 `setHandleConfirmed`，導致對已 unmount 元件的狀態更新。建議使用 `useRef` 追蹤 mounted 狀態，或在 mutation 的 `onSuccess` 中檢查。

**判斷依據**：diff 中 `useEffect` 的回傳函式，僅清除 interval，未處理進行中的 mutation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 狀態可能改變，應使相關查詢失效以更新 UI。建議加入對應的 `queryClient.invalidateQueries`。

**判斷依據**：diff 中新增的 `useConfirmBlueskyHandleMutationForUser` 函式，內含該註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11743 (cache hit 9344) ｜ completion tokens 1383 ｜ PR #10</sub>