<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除了文字輸入的硬編碼 48 字元限制，改為依賴後端提供的 max_length。整體方向合理，但新增的 console.log 違反前端規範，且移除 max_length 預設值可能導致既有資料或未更新後端時出現未定義行為。建議先移除 console.log 並確認後端已正確提供 max_length。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/share/text-generation/index.tsx:261` | max_length 可能為 undefined 導致比較錯誤 | 0.80 |
| ⚠️ | Major | `web/app/components/share/text-generation/run-once/index.tsx:142` | maxLength 屬性可能為 undefined 導致無限制輸入 | 0.80 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:198` | paragraph 類型不再設定 max_length 預設值 | 0.80 |
| ⚠️ | Major | `web/app/components/rag-pipeline/components/panel/input-field/editor/form/hooks.ts:87` | paragraph 類型不再設定 maxLength 預設值 | 0.80 |
| ⚠️ | Major | `web/app/components/app/configuration/prompt-value-panel/index.tsx:167` | number 輸入類型改為 text 可能影響驗證 | 0.80 |
| 🔸 | Minor | `web/app/components/share/text-generation/index.tsx:199` | [R25] 移除 console.log 陳述式 | 0.95 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/index.tsx:261</code> max_length 可能為 undefined 導致比較錯誤</summary>

原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在直接使用 `varItem.max_length`。若後端未提供 `max_length`，則 `item[varIndex].length > undefined` 會得到 `false`，導致長度驗證失效。請確認後端必定提供 `max_length`，或在此處保留預設值。

**判斷依據**：diff 中將 `const maxLen = varItem.max_length || DEFAULT_VALUE_MAX_LEN` 改為直接使用 `varItem.max_length`，且未提供 fallback。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/share/text-generation/run-once/index.tsx:142</code> maxLength 屬性可能為 undefined 導致無限制輸入</summary>

原本使用 `item.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在直接使用 `item.max_length`。若 `max_length` 未定義，則 `maxLength` 屬性會是 `undefined`，瀏覽器將不限制輸入長度。請確認後端必定提供 `max_length`，或在此處保留預設值。

**判斷依據**：diff 中將 `maxLength={item.max_length || DEFAULT_VALUE_MAX_LEN}` 改為 `maxLength={item.max_length}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:198</code> paragraph 類型不再設定 max_length 預設值</summary>

原本在類型變更為 paragraph 時會設定 `draft.max_length = DEFAULT_VALUE_MAX_LEN`，現在移除後，若使用者未手動設定，`max_length` 可能為 undefined，導致後續驗證或 UI 顯示問題。請確認此行為符合預期。

**判斷依據**：diff 中移除了設定 `draft.max_length = DEFAULT_VALUE_MAX_LEN` 的程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/rag-pipeline/components/panel/input-field/editor/form/hooks.ts:87</code> paragraph 類型不再設定 maxLength 預設值</summary>

原本在類型變更為 paragraph 時會呼叫 `setFieldValue('maxLength', DEFAULT_VALUE_MAX_LEN)`，現在移除後，若使用者未手動設定，`maxLength` 可能為 undefined，導致後續驗證或 UI 顯示問題。請確認此行為符合預期。

**判斷依據**：diff 中移除了設定 `maxLength` 的程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/prompt-value-panel/index.tsx:167</code> number 輸入類型改為 text 可能影響驗證</summary>

原本 `type="number"` 的輸入框改為 `type="text"`，這可能導致瀏覽器不再提供數字輸入的驗證和介面（如上下箭頭）。若需要數字輸入，建議保留 `type="number"` 或使用其他方式驗證。

**判斷依據**：diff 中將 `type="number"` 改為 `type="text"`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/share/text-generation/index.tsx:199</code> [R25] 移除 console.log 陳述式</summary>

新增的 `console.log` 違反前端規範 R25（不得使用 console 陳述式）。請移除或改用適當的 logging 機制。

**判斷依據**：diff 中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，違反 R25。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8352 (cache hit 8320) ｜ completion tokens 1278 ｜ PR #5</sub>