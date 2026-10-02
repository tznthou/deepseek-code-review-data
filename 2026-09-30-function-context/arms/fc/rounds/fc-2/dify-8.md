<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 `web/app/components/devtools/` 下，並引入 lazy loading 的 loader 元件。主要風險在於 React Scan loader 的錯誤處理會吞掉載入失敗，且開發環境判斷依賴 `IS_DEV` 常數，可能導致建置時期決定而非執行時期。TanStack loader 的錯誤處理則完全靜默，不利於除錯。整體而言，重構方向合理，但錯誤處理與可觀測性需要加強。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:10` | React Scan 載入失敗時僅回傳空元件，可能隱藏錯誤 | 0.80 |
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:10` | TanStack Devtools 載入失敗時完全靜默 | 0.80 |
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:16` | 使用建置時期常數 `IS_DEV` 控制 devtools 載入，可能無法在執行時期動態切換 | 0.70 |
| 🔸 | Minor | `web/app/components/devtools/tanstack/loader.tsx:15` | 使用建置時期常數 `IS_DEV` 控制 devtools 載入，可能無法在執行時期動態切換 | 0.70 |

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> React Scan 載入失敗時僅回傳空元件，可能隱藏錯誤</summary>

當動態載入 `./scan` 失敗時，catch 區塊回傳一個渲染 `null` 的元件，僅在 console 輸出錯誤。這會讓開發者難以察覺 devtools 未正常運作，特別是在 production 建置或網路問題時。建議至少保留錯誤狀態顯示，或考慮將錯誤拋出讓上層錯誤邊界處理。

**判斷依據**：diff 中新增的 loader.tsx 第 8-10 行顯示 catch 區塊僅記錄錯誤並回傳空元件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> TanStack Devtools 載入失敗時完全靜默</summary>

catch 區塊直接回傳渲染 `null` 的元件，且未記錄任何錯誤。這使得動態載入失敗時完全無從得知，增加除錯困難。建議至少加入 `console.error` 或類似機制。

**判斷依據**：diff 中新增的 loader.tsx 第 7-9 行顯示 catch 區塊未記錄錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:16</code> 使用建置時期常數 `IS_DEV` 控制 devtools 載入，可能無法在執行時期動態切換</summary>

`IS_DEV` 通常在建置時由環境變數決定，若部署環境與建置環境不一致（例如在 staging 建置但部署到 production），可能導致 devtools 意外啟用或停用。建議改為執行時期判斷（例如檢查 `process.env.NODE_ENV` 或使用 runtime config）。

**判斷依據**：diff 中 loader.tsx 第 15-16 行使用 `IS_DEV` 常數進行條件渲染。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/tanstack/loader.tsx:15</code> 使用建置時期常數 `IS_DEV` 控制 devtools 載入，可能無法在執行時期動態切換</summary>

與 React Scan loader 相同，`IS_DEV` 在建置時決定，可能導致環境不一致。建議改為執行時期判斷。

**判斷依據**：diff 中 loader.tsx 第 14-15 行使用 `IS_DEV` 常數進行條件渲染。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4380 (cache hit 4352) ｜ completion tokens 941 ｜ PR #8</sub>