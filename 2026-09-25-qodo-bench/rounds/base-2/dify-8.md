<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 devtools/ 目錄下，並引入 lazy loading 與錯誤處理。主要風險在於 React Scan 的 lazy import 在失敗時會回傳一個靜默的 null 元件，可能隱藏載入錯誤；TanStack devtools 的錯誤處理則完全吞掉錯誤，不利於除錯。整體結構改善合理，但錯誤處理與可觀測性需要加強。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/devtools/react-scan/loader.tsx:10` | React Scan 載入失敗時靜默降級，可能隱藏錯誤 | 0.80 |
| 🔸 | Minor | `web/app/components/devtools/tanstack/loader.tsx:9` | TanStack devtools 載入失敗時完全吞掉錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> React Scan 載入失敗時靜默降級，可能隱藏錯誤</summary>

當 `import('./scan')` 失敗時，`.catch` 回傳一個渲染 `null` 的元件，導致 devtools 完全不出現且沒有任何使用者可見的提示。雖然有 `console.error`，但在 production 環境中可能被忽略。建議在開發環境中顯示一個明顯的錯誤訊息，或至少保留錯誤狀態供後續處理。

**判斷依據**：diff 中新增的 loader.tsx 第 9-11 行顯示 catch 區塊僅記錄錯誤並回傳 null 元件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/tanstack/loader.tsx:9</code> TanStack devtools 載入失敗時完全吞掉錯誤</summary>

`.catch(() => { return { default: () => null } })` 沒有記錄任何錯誤，若動態載入失敗，開發者將無法得知原因。建議至少加上 `console.error` 或類似的錯誤記錄。

**判斷依據**：diff 中新增的 loader.tsx 第 8-10 行顯示 catch 區塊為空，未記錄錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2904 (cache hit 2816) ｜ completion tokens 533 ｜ PR #8</sub>