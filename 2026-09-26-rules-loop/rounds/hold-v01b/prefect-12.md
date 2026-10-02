<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要改善 UI v2 的 task run 詳細頁面，使其與 Vue 版本功能對齊。新增了狀態對應的 favicon SVG 檔案，並引入 usePageTitle 與 useStateFavicon hooks。同時調整了 task run details 的顯示邏輯，將原本條件式隱藏的欄位改為一律顯示並以 'None' 表示空值。整體風險中等，主要問題在於 useStateFavicon 的實作可能導致 favicon 設定錯誤或無法正確還原，以及 task-run-details.tsx 中對 run_count 的處理可能將 0 顯示為 0 但原本可能顯示 '0'，差異不大。建議修正 favicon hook 的邏輯後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:40` | useStateFavicon 在 dark mode 下可能找不到正確的 favicon 元素 | 0.80 |
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:50` | favicon 路徑未考慮 base URL，可能導致 404 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | run_count 顯示邏輯可能將 0 顯示為 0，但原本可能顯示 '0' | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:94` | estimated_run_time 顯示邏輯與其他欄位不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:40</code> useStateFavicon 在 dark mode 下可能找不到正確的 favicon 元素</summary>

在 `getPreferredColorScheme` 回傳 `dark` 時，程式碼會嘗試取得 `favicon-16-dark` 與 `favicon-32-dark` 元素。但若 HTML 中沒有這些 id（例如僅有 `favicon-16` 與 `favicon-32`），則 `favicon16` 與 `favicon32` 會是 `null`，導致後續 `setAttribute` 呼叫失敗，favicon 不會更新。此外，cleanup 函式中的還原邏輯也依賴相同的元素，若元素不存在，則無法還原。建議確認 HTML 中確實存在對應的 dark 模式 favicon 元素，或加入 fallback 邏輯。

**判斷依據**：diff 中新增的 hook 直接使用 getElementById 取得元素，但未檢查是否存在。若 HTML 中沒有 dark 模式的 favicon 元素，則會導致 null 參考錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:50</code> favicon 路徑未考慮 base URL，可能導致 404</summary>

favicon 路徑使用 `/${stateType.toLowerCase()}.svg`，但若應用程式部署在子路徑下（例如 `https://example.com/prefect/`），則此絕對路徑會指向根目錄，導致 404。建議使用相對路徑或基於 `import.meta.env.BASE_URL` 建構路徑。

**判斷依據**：diff 中新增的 favicon 路徑以 `/` 開頭，未考慮 base URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> run_count 顯示邏輯可能將 0 顯示為 0，但原本可能顯示 '0'</summary>

原本的程式碼在 `run_count` 不為 null/undefined 時顯示其值，否則不顯示。新程式碼改為 `{taskRun.run_count || 0}`，這會將 `run_count` 為 0 或 null/undefined 時都顯示為 0。若 `run_count` 為 0，原本會顯示 0，新程式碼也顯示 0，差異不大；但若 `run_count` 為 null，原本不顯示，新程式碼顯示 0，可能造成誤導。建議改為 `{taskRun.run_count ?? 'None'}` 以維持一致性。

**判斷依據**：diff 中將原本條件式顯示改為一律顯示，並使用 `||` 運算子，可能將 null 視為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:94</code> estimated_run_time 顯示邏輯與其他欄位不一致</summary>

其他欄位在空值時顯示 'None'，但 `estimated_run_time` 的判斷條件為 `!== null && !== undefined`，若值為 0 則會顯示 'None'，但 0 可能是有效的估計時間。建議使用 `??` 或 `!= null` 來判斷。

**判斷依據**：diff 中該欄位的條件判斷與其他欄位不同，可能導致 0 被視為空值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9063 (cache hit 8960) ｜ completion tokens 1334 ｜ PR #12</sub>