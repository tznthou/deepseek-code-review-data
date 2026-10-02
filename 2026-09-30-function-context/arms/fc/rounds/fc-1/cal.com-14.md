<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 為 feature opt-in 功能新增了 scope 設定（org/team/user），並在服務層加入對應的驗證邏輯。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 `globalEnabled` 為 true 的項目，但程式碼卻回傳 `!state.globalEnabled`），這會導致使用者看不到任何已啟用的功能。另外，`setUserState` 的 mutation 缺少 `await`，可能造成未處理的 Promise rejection。整體而言，scope 驗證邏輯本身設計合理，但上述兩個問題需要修正。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，導致回傳全域停用的功能 | 0.95 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103` | setUserState mutation 缺少 await，可能造成未處理的 Promise rejection | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，導致回傳全域停用的功能</summary>

在 `listFeaturesForUser` 方法中，原本應該回傳 `globalEnabled` 為 true 的功能，但程式碼卻寫成 `filter((state) => !state.globalEnabled)`，這會回傳所有全域停用的功能，而使用者將看不到任何已啟用的功能。

**失敗情境**：當使用者呼叫 `listForUser` API 時，會收到一個空陣列（或僅包含停用功能的陣列），導致前端無法顯示任何可設定的功能。

**建議修法**：將條件改為 `filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由原本的 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103</code> setUserState mutation 缺少 await，可能造成未處理的 Promise rejection</summary>

在 `setUserState` mutation 中，呼叫 `featureOptInService.setUserFeatureState(...)` 時沒有加上 `await`。這會導致如果該方法拋出錯誤（例如 scope 驗證失敗），錯誤不會被 tRPC 正確捕獲，而會成為 unhandled promise rejection，可能導致伺服器不穩定或回傳錯誤的狀態碼。

**失敗情境**：當使用者嘗試設定一個不允許在 user scope 設定的功能時，`setUserFeatureState` 會拋出 `ErrorWithCode`，但因為沒有 `await`，這個錯誤不會被 tRPC 的錯誤處理機制攔截，客戶端可能收到成功回應，但實際上操作並未完成。

**建議修法**：在呼叫前加上 `await`。

**判斷依據**：diff 中此處原本有 `await`，但被移除。其他 mutation（如 `setTeamState`）仍保留 `await`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數未被使用，且其值為字串，可能只是測試用途。這會觸發 lint 警告，並增加不必要的程式碼。

**建議修法**：刪除此常數。

**判斷依據**：diff 中新增此行，且後續程式碼未引用此常數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16402 (cache hit 1536) ｜ completion tokens 1016 ｜ PR #14</sub>