<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了文字輸入的硬編碼 48 字元上限，改為依賴後端提供的 max_length。整體方向合理，但存在兩個主要風險：`console.log` 可能洩漏批次輸入資料，且 `varItem.max_length` 為 undefined 時會導致比較失效，使長度驗證被跳過。建議先移除 console.log 並修正長度驗證邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/share/text-generation/index.tsx:199` | console.log 可能洩漏使用者輸入資料 | 0.95 |
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | max_length 為 undefined 時長度驗證失效 | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | 數字輸入框類型從 number 改為 text 可能影響驗證 | 0.80 |
| 🔸 | Minor | `web/app/components/share/text-generation/run-once/index.tsx:142` | maxLength 屬性可能被設為 undefined | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> console.log 可能洩漏使用者輸入資料</summary>

新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。

**判斷依據**：diff 中新增的 console.log 行，位於批次輸入驗證邏輯之前。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> max_length 為 undefined 時長度驗證失效</summary>

當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

**判斷依據**：diff 中將原本的 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 改為直接使用 `varItem.max_length`，未處理 undefined 的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> 數字輸入框類型從 number 改為 text 可能影響驗證</summary>

將數字輸入框的 `type` 從 `number` 改為 `text`，可能導致瀏覽器不再自動驗證數字格式，且行動裝置可能顯示不同的鍵盤。若此變更非刻意為之，建議保留 `type="number"`。

**判斷依據**：diff 中將原本的 `type="number"` 改為 `type="text"`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/share/text-generation/run-once/index.tsx:142</code> maxLength 屬性可能被設為 undefined</summary>

當 `item.max_length` 未定義時，`maxLength={item.max_length}` 會將屬性設為 undefined，React 不會渲染該屬性，但可能導致非預期行為。建議明確處理：`maxLength={item.max_length || undefined}` 或條件渲染。

**判斷依據**：diff 中將原本的 `maxLength={item.max_length || DEFAULT_VALUE_MAX_LEN}` 改為 `maxLength={item.max_length}`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5636 (cache hit 1536) ｜ completion tokens 901 ｜ PR #5</sub>