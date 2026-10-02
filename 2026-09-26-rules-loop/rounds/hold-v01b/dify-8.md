<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 devtools 元件重新組織到 `web/app/components/devtools/` 下，並引入 lazy loading 的 loader 元件。主要風險在於 React Scan loader 的錯誤處理：catch 中回傳 fallback 元件並記錄錯誤，但若動態載入失敗，使用者只會看到空元件，可能誤以為 devtools 正常運作。TanStack loader 的 catch 則完全吞掉錯誤，沒有任何 log，不利於除錯。此外，React Scan loader 的 fallback UI 包含硬編碼文字，違反 i18n 規範。整體而言，改動方向合理，但錯誤處理與可觀測性需要加強。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/devtools/react-scan/loader.tsx:10` | React Scan 載入失敗時僅回傳空元件，使用者無法察覺 devtools 未啟動 | 0.80 |
| ⚠️ | Major | `web/app/components/devtools/tanstack/loader.tsx:10` | TanStack Devtools 載入失敗時完全吞掉錯誤，無任何 log | 0.80 |
| 🔸 | Minor | `web/app/components/devtools/react-scan/loader.tsx:20` | [R11] 硬編碼使用者可見文字，應使用 i18n 翻譯 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/react-scan/loader.tsx:10</code> React Scan 載入失敗時僅回傳空元件，使用者無法察覺 devtools 未啟動</summary>

在 `lazy` 的 `catch` 中，回傳 `{ default: () => null }`，這會讓 `ReactScan` 元件渲染為空。如果動態載入失敗（例如網路問題或 chunk 載入錯誤），使用者將看不到任何 devtools 功能，且沒有任何視覺提示，可能誤以為 devtools 正常運作。建議在 catch 中回傳一個顯示錯誤狀態的元件，或至少保留錯誤 log（目前已有 `console.error`，但使用者看不到）。

**判斷依據**：diff 中新增的 loader.tsx 第 9-11 行顯示 catch 區塊回傳空元件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/devtools/tanstack/loader.tsx:10</code> TanStack Devtools 載入失敗時完全吞掉錯誤，無任何 log</summary>

在 `lazy` 的 `catch` 中，僅回傳 `{ default: () => null }`，沒有記錄任何錯誤。這使得動態載入失敗時完全無法追蹤，不利於除錯。建議至少加入 `console.error` 記錄錯誤，或使用其他 logging 機制。

**判斷依據**：diff 中新增的 loader.tsx 第 9-11 行顯示 catch 區塊沒有錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/devtools/react-scan/loader.tsx:20</code> [R11] 硬編碼使用者可見文字，應使用 i18n 翻譯</summary>

fallback UI 中的文字 "Loading devtools..." 是硬編碼的，違反專案規範 R11（前端使用者可見字串必須使用 i18n 翻譯）。請改用翻譯鍵，例如 `t('common.loading')` 或新增對應翻譯。

**判斷依據**：diff 中新增的 loader.tsx 第 18 行顯示硬編碼文字。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5583 (cache hit 5504) ｜ completion tokens 831 ｜ PR #8</sub>