<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enable），再輪詢確認 handle（confirm-handle）。主要風險在於前端輪詢邏輯的競態與錯誤處理：confirmHandle 的 promise 未捕捉錯誤，可能導致未處理的 rejection；輪詢在元件卸載後仍可能觸發 mutation；且 TypeScript 的 strict 模式被關閉，降低型別安全。建議優先修正錯誤處理與輪詢清理，並恢復 strict 模式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | [R16] TypeScript strict 模式被關閉 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69` | confirmHandle 的 promise 未處理 rejection | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢可能在元件卸載後繼續觸發 mutation | 0.80 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows query 的 invalidation | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] TypeScript strict 模式被關閉</summary>

`strict` 從 `true` 改為 `false`，違反規範 R16（TypeScript Files Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復 `strict: true`，並修正相關型別問題。

**判斷依據**：diff 中 tsconfig.json 的 strict 設定從 true 改為 false。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:69</code> confirmHandle 的 promise 未處理 rejection</summary>

`confirmBlueskyHandleMutation.mutateAsync().then(...)` 沒有接 `.catch`。如果 mutation 失敗（例如網路錯誤或非 429 的錯誤），會產生未處理的 promise rejection，可能導致開發環境的警告或生產環境的錯誤追蹤。建議加上 `.catch` 處理錯誤，或使用 `try/catch` 包住 `await`。

**判斷依據**：diff 中新增的 confirmHandle 函式，呼叫 mutateAsync 後僅使用 .then，沒有 .catch。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢可能在元件卸載後繼續觸發 mutation</summary>

`useEffect` 的回傳函式會清除 interval，但若 interval 回呼正在執行且已呼叫 `confirmHandle()`，該 mutation 仍會繼續。若元件在 mutation 完成前卸載，可能導致狀態更新在卸載的元件上，或產生不必要的請求。建議在 cleanup 中設置一個 cancelled flag，並在 mutation 完成後檢查。

**判斷依據**：diff 中新增的 useEffect 內 setInterval 回呼，呼叫 confirmHandle 後沒有檢查元件是否仍掛載。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows query 的 invalidation</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 onSuccess 中，註解提到「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 狀態可能改變（例如開始追蹤 brid.gy 帳號），但沒有 invalidate 相關 query，可能導致 UI 顯示過時資料。建議加入對應的 query invalidation。

**判斷依據**：diff 中新增的註解明確指出缺少 invalidation。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11753 (cache hit 1536) ｜ completion tokens 1077 ｜ PR #10</sub>