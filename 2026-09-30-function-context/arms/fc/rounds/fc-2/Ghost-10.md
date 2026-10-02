<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enable）再確認 handle（confirm-handle），並更新 API 端點至 v2。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript strict 模式被關閉，以及 API 回傳型別與快取更新的一致性。建議優先修正 strict 關閉與輪詢 effect 的依賴問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121` | useEffect 依賴陣列不完整可能導致輪詢失效或記憶體洩漏 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢期間未處理元件卸載時的競態 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2790` | 確認 handle 成功後未 invalidate accountFollows 查詢 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 和 disableBluesky 回傳型別不明確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與 PR 目的無關，且會影響整個專案的型別檢查。建議恢復 `strict: true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` → `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121</code> useEffect 依賴陣列不完整可能導致輪詢失效或記憶體洩漏</summary>

useEffect 的依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`，但內部使用了 `disableBlueskyMutation`。若 `disableBlueskyMutation` 的實例在重新渲染時改變（例如因 queryClient 或 mutation 狀態變化），effect 不會重新執行，可能導致使用過時的 mutation 或無法正確清理 interval。建議將 `disableBlueskyMutation` 加入依賴陣列，或確保其穩定性。

**判斷依據**：diff 中新增的 useEffect 依賴陣列，註解聲稱 disableBlueskyMutation 是穩定的，但未在依賴中列出。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢期間未處理元件卸載時的競態</summary>

在 useEffect 的 interval 回呼中，呼叫 `confirmHandle()` 後若元件卸載，`confirmBlueskyHandleMutation.mutateAsync()` 的 promise 仍可能 resolve，並呼叫 `setHandleConfirmed(true)`，導致對已卸載元件的狀態更新。建議在 cleanup 中設定一個 cancelled 旗標，或在 promise 回呼中檢查元件是否仍掛載。

**判斷依據**：diff 中新增的 interval 回呼，未見對元件卸載的防護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2790</code> 確認 handle 成功後未 invalidate accountFollows 查詢</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 onSuccess 中，更新了帳戶快取，但未 invalidate `accountFollows` 查詢。啟用 Bluesky 後會自動追蹤 brid.gy 帳號，確認 handle 後可能也需要更新追蹤列表。建議加入 `queryClient.invalidateQueries({ queryKey: QUERY_KEYS.accountFollows('index', 'following') })`。

**判斷依據**：diff 中新增的 onSuccess 區塊，註解明確指出缺少 invalidation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 和 disableBluesky 回傳型別不明確</summary>

`enableBluesky` 和 `disableBluesky` 現在沒有明確的回傳型別（隱含 `Promise<void>`），但呼叫端可能期望回傳值。建議明確標註 `Promise<void>`，並確認所有呼叫端都已更新。

**判斷依據**：diff 中新增的方法定義，缺少回傳型別註記。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23267 (cache hit 23168) ｜ completion tokens 1456 ｜ PR #10</sub>