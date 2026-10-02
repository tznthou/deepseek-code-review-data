<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯 work pool 的 description 與 concurrency limit，並包含 Storybook stories 與測試。整體結構清晰，但存在幾個問題：concurrency limit 的輸入處理可能導致非預期的 null 或 NaN 提交；測試中對 useUpdateWorkPool 的 mock 型別與實際回傳值不完全一致，可能隱藏型別錯誤；此外，部分測試斷言依賴於實作細節，可能造成誤報。建議優先修正 concurrency limit 的輸入驗證與處理邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | concurrency limit 輸入處理可能產生 NaN 或非預期的 null | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28` | mock 的 useUpdateWorkPool 型別與實際 hook 回傳不一致 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:162` | 測試斷言依賴於實作細節，可能造成誤報 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> concurrency limit 輸入處理可能產生 NaN 或非預期的 null</summary>

在 `onChange` 中，當輸入為空字串時設定為 `null`，否則使用 `Number(value)`。但 `Number('')` 為 0，而 `Number('abc')` 為 NaN。若使用者輸入非數字字元（例如 'e' 或 '-'），可能得到 NaN，且表單驗證可能無法攔截，導致提交 NaN 給 API。此外，若輸入為 '0'，會得到 0，但後端可能將 0 視為無限制或錯誤。建議使用更嚴格的解析方式，例如 `parseInt` 並檢查 `Number.isNaN`，或使用 zod schema 進行驗證。

**判斷依據**：diff 中新增的 `onChange` 處理邏輯直接使用 `Number(value)`，未檢查 NaN 或非數字輸入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28</code> mock 的 useUpdateWorkPool 型別與實際 hook 回傳不一致</summary>

測試中 mock 的 `useUpdateWorkPool` 回傳物件包含 `updateWorkPool` 和 `isPending`，但實際 hook 可能回傳更多屬性（如 `isError`、`error` 等）。這可能導致測試通過但實際使用時型別錯誤。建議使用 `vi.mocked` 或從實際模組取得型別來確保一致性。

**判斷依據**：mock 回傳物件僅包含兩個屬性，可能與實際 hook 的完整回傳型別不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:162</code> 測試斷言依賴於實作細節，可能造成誤報</summary>

在「handles empty concurrency limit as null」測試中，直接檢查 `mockUpdateWorkPool` 的呼叫參數，這與元件內部實作耦合。若未來重構參數結構，測試將失敗。建議改為驗證使用者可見的行為（例如成功 toast 或導航），或使用更穩定的 mock 驗證方式。

**判斷依據**：測試直接檢查 mock 函式的呼叫參數，而非驗證最終結果。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9211 (cache hit 7680) ｜ completion tokens 996 ｜ PR #13</sub>