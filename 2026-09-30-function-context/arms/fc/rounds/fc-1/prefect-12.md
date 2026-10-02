<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為 UI v2 的 task run 詳情頁增加與 Vue 版本一致的功能：動態 favicon、頁面標題、麵包屑導航參數、輸入複製按鈕，並將詳細資訊欄位改為一律顯示（無值時顯示 'None'）。整體風險低，但 favicon hook 存在潛在的競態條件與 SSR 相容性問題，且詳細資訊欄位使用 `||` 可能錯誤地將 0 或空字串顯示為 'None'。建議修正後合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:37` | favicon 設定存在競態條件，可能殘留錯誤圖示 | 0.80 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:14` | SSR 環境下直接存取 window 可能導致錯誤 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117` | 使用 `\|\|` 可能錯誤地將 0 或空字串顯示為 'None' | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:37</code> favicon 設定存在競態條件，可能殘留錯誤圖示</summary>

`useStateFavicon` 在 `useEffect` 中設定 favicon，但 cleanup 函式僅在 unmount 時執行。若 `stateType` 快速變化（例如從 RUNNING 變為 COMPLETED），前一個 effect 的 cleanup 會先執行，將 favicon 重設為預設值，然後新的 effect 設定新圖示，順序正確。但若元件因路由切換而 unmount，cleanup 會將 favicon 重設為預設值，但若新頁面也使用此 hook，其 effect 會在 cleanup 後執行，可能造成短暫閃爍。更嚴重的問題是：若多個元件同時使用此 hook，最後 unmount 的元件會覆蓋其他元件的 favicon。建議使用全域狀態管理（如 context 或 store）來追蹤目前應顯示的 favicon，並在 cleanup 時檢查是否仍為當前設定。

**判斷依據**：diff 中新增的 hook 檔案，第 42 行開始的 useEffect 與 cleanup 邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:14</code> SSR 環境下直接存取 window 可能導致錯誤</summary>

`getPreferredColorScheme` 直接使用 `window.matchMedia`，若此 hook 在伺服器端渲染（SSR）時被呼叫，會因為 `window` 未定義而拋出錯誤。雖然此 hook 目前僅在 client component 中使用，但未來若被引入其他元件可能造成問題。建議在函式內檢查 `typeof window !== 'undefined'`，或將此邏輯移至 `useEffect` 內（因為 `useEffect` 僅在 client 執行）。

**判斷依據**：diff 中新增的 hook 檔案，第 12 行開始的函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117</code> 使用 `||` 可能錯誤地將 0 或空字串顯示為 'None'</summary>

在 `Run Count` 欄位中，`{taskRun.run_count || 0}` 會將 `run_count` 為 0 時顯示為 0，這是正確的。但其他欄位如 `Cache Key` 使用 `{taskRun.cache_key || "None"}`，若 `cache_key` 為空字串（合法值），會顯示 'None'，可能造成誤導。建議改用 `??` 運算子來區分 `null`/`undefined` 與其他 falsy 值。

**判斷依據**：diff 中第 100 行附近的 `Cache Key` 欄位。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9766 (cache hit 1536) ｜ completion tokens 1437 ｜ PR #12</sub>