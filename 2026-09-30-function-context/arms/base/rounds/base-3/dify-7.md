<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 統一抽到 `web/test/i18n-mock.ts` 的輔助函式，並更新全域 mock 與文件。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為改變（現在會加上 namespace 前綴），可能影響未修改的測試；此外，`createTFunction` 的參數序列化方式與舊 mock 不完全一致，可能導致部分測試斷言失敗。建議先確認所有依賴全域 mock 的測試是否仍通過，並補齊新輔助函式的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:13` | 全域 mock 行為變更可能影響未修改的測試 | 0.80 |
| ⚠️ | Major | `web/test/i18n-mock.ts:24` | 參數序列化方式與舊 mock 不一致 | 0.75 |
| 🔸 | Minor | `web/test/i18n-mock.ts:10` | 缺少輔助函式的單元測試 | 0.60 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態 import 輔助函式可能造成非同步問題 | 0.55 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:13</code> 全域 mock 行為變更可能影響未修改的測試</summary>

全域 mock 原本在沒有 namespace 時直接回傳 key，現在改為一律加上 namespace 前綴（若存在）。這會改變所有依賴全域 mock 的測試行為，可能導致大量測試失敗。建議先執行完整測試套件確認影響範圍，或考慮保留舊行為作為預設，僅在需要時才加上前綴。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的變更顯示原本的 `t` 函式在沒有 namespace 時回傳 `key`，新的 `createTFunction` 則會回傳 `fullKey`（包含 namespace）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:24</code> 參數序列化方式與舊 mock 不一致</summary>

舊的全域 mock 在序列化參數時會排除 `ns` 並使用 `JSON.stringify`，但新的 `createTFunction` 使用 `delete params.ns` 後再序列化，兩者結果相同，但若 `options` 為 `undefined` 或 `null`，`delete` 可能拋出錯誤。此外，舊 mock 在 `options` 存在但無其他參數時不會加上後綴，新函式則會加上 `:{}`，可能導致測試斷言失敗。建議明確處理 `options` 為空的情況，並保持與舊行為一致。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊實作在 `options` 存在但無其他參數時不會加上後綴，新實作則會加上 `:{}`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:10</code> 缺少輔助函式的單元測試</summary>

新增的 `createTFunction`、`createUseTranslationMock`、`createTransMock` 等函式沒有對應的測試。建議補上單元測試，確保其行為符合預期，特別是參數處理和 fallback 邏輯。

**判斷依據**：diff 中新增的 `web/test/i18n-mock.ts` 檔案沒有對應的測試檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態 import 輔助函式可能造成非同步問題</summary>

在 `vi.mock` 中使用 `await import('@/test/i18n-mock')` 是可行的，但需確保該模組在測試環境中可被正確解析。若路徑別名設定有誤，可能導致測試失敗。建議確認 `@/test` 別名在 Vitest 設定中已正確配置。

**判斷依據**：diff 中 `install.spec.tsx` 的變更使用了動態 import。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10301 (cache hit 10240) ｜ completion tokens 1093 ｜ PR #7</sub>