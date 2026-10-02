<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 `web/app/components/devtools/` 下，並引入 lazy loading 與錯誤處理。主要風險在於 TanStack devtools 的載入失敗被靜默吞掉，且 React Scan 的錯誤處理回傳了無效元件，可能導致執行時期錯誤。整體結構合理，但建議修正錯誤處理並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/devtools/tanstack/loader.tsx:7` | TanStack devtools 載入失敗被靜默吞掉 | 0.80 |
| ⚠️ | Major | `web/app/components/devtools/react-scan/loader.tsx:7` | React Scan 錯誤處理回傳無效元件 | 0.75 |
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:20` | Suspense fallback 顯示載入文字可能造成版面跳動 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/tanstack/loader.tsx:7</code> TanStack devtools 載入失敗被靜默吞掉</summary>

在 `import('./devtools')` 的 `.catch()` 中直接回傳 `{ default: () => null }`，沒有記錄任何錯誤。這會讓開發者在 devtools 載入失敗時完全沒有線索，難以診斷問題。建議至少加上 `console.error` 記錄錯誤，或提供更明確的 fallback UI。

**判斷依據**：diff 中新增的 loader.tsx 第 8-12 行，catch 區塊沒有錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/react-scan/loader.tsx:7</code> React Scan 錯誤處理回傳無效元件</summary>

在 `.catch()` 中回傳 `{ default: () => null }`，但 `ReactScan` 元件可能預期有特定的 props 或行為。若 `ReactScan` 在掛載時呼叫 hooks 或依賴 context，這個 fallback 可能導致執行時期錯誤。建議確認 `ReactScan` 的介面，或提供一個安全的 fallback 元件。

**判斷依據**：diff 中新增的 loader.tsx 第 7-12 行，catch 回傳的元件可能不符合預期。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:20</code> Suspense fallback 顯示載入文字可能造成版面跳動</summary>

在 devtools 載入期間顯示「Loading devtools...」文字，可能造成版面跳動或影響使用者體驗。建議使用 `null` 或 invisible fallback，或將 fallback 設計為不佔空間的元素。

**判斷依據**：diff 中新增的 loader.tsx 第 18 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2868 (cache hit 2816) ｜ completion tokens 785 ｜ PR #8</sub>