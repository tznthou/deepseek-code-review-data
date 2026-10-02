<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 `web/app/components/devtools/` 目錄下，並引入 lazy loading 與錯誤處理。主要風險在於 `react-scan/loader.tsx` 中錯誤處理後回傳的元件可能導致 React 渲染錯誤，以及 `IS_DEV` 判斷在 client bundle 中可能失效，使 devtools 在 production 環境意外載入。建議修正錯誤處理邏輯並確認 `IS_DEV` 的實作方式。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/devtools/react-scan/loader.tsx:11` | React Scan 載入失敗時回傳的元件可能導致渲染錯誤 | 0.80 |
| ⚠️ | Major | `web/app/components/devtools/react-scan/loader.tsx:16` | IS_DEV 判斷可能在 client bundle 中失效 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/react-scan/loader.tsx:11</code> React Scan 載入失敗時回傳的元件可能導致渲染錯誤</summary>

在 `lazy` 的 `catch` 中回傳 `{ default: () => null }`，但 `ReactScan` 元件本身可能接受 props 或依賴 context。若 `ReactScan` 在渲染時需要特定 props 或 context，這個 fallback 元件可能無法滿足，導致錯誤。此外，`lazy` 的 factory 必須回傳一個 Promise，其 resolve 值必須是 `{ default: Component }`，此處符合，但 fallback 元件若被渲染且內部有 hook 或依賴，可能造成問題。建議改為回傳一個明確的 fallback 元件，或直接讓錯誤拋出並由 error boundary 處理。

**判斷依據**：diff 中第 10 行：`return { default: () => null }`

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/react-scan/loader.tsx:16</code> IS_DEV 判斷可能在 client bundle 中失效</summary>

`IS_DEV` 從 `@/config` 匯入，若該值在建置時被替換為 `false`，則在 production 環境中 devtools 不會載入，符合預期。但若 `IS_DEV` 是 runtime 判斷（例如依賴 `process.env.NODE_ENV`），在 client bundle 中可能無法正確反映環境，導致 devtools 在 production 中意外載入，或反之在 development 中未載入。建議確認 `IS_DEV` 的實作方式，並考慮在建置時使用 `process.env.NODE_ENV` 進行靜態替換。

**判斷依據**：diff 中第 16-17 行：`if (!IS_DEV) return null`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 2868 (cache hit 1408) ｜ completion tokens 664 ｜ PR #8</sub>