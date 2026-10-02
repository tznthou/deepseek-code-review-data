<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 `components/devtools/` 下，並新增兩個 lazy loader（React Scan 與 TanStack Devtools）。主要風險在於 React Scan loader 的動態 import 錯誤處理：catch 中回傳的 fallback 元件會讓錯誤被吞掉，且 `console.error` 可能洩漏內部路徑。TanStack loader 的 catch 則完全靜默，不利於除錯。整體結構合理，但建議改善錯誤處理與可觀測性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:10` | React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊 | 0.80 |
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:10` | TanStack Devtools 載入失敗時完全靜默 | 0.70 |

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊</summary>

當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

**判斷依據**：diff 中新增的 loader.tsx 第 9-11 行顯示 catch 區塊直接 console.error 並回傳空元件，未將錯誤向上傳遞或提供可觀測的 fallback。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> TanStack Devtools 載入失敗時完全靜默</summary>

catch 區塊僅回傳空元件，沒有任何錯誤記錄。這使得在開發環境中若動態 import 失敗，開發者將無法得知原因，增加除錯困難。建議至少加入 `console.error` 或使用 Sentry 記錄錯誤。

**判斷依據**：diff 中新增的 loader.tsx 第 9-11 行顯示 catch 區塊為空，未記錄任何錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2904 (cache hit 1536) ｜ completion tokens 603 ｜ PR #8</sub>