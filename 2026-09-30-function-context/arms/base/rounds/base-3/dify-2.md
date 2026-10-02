<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 啟用了 JSON_OBJECT 型別在 Console UI 的支援，移除了原本的硬編碼停用旗標，並調整了 JSON Schema 的處理邏輯：現在直接儲存完整的 schema 而非僅 properties。主要風險在於 `handleJSONSchemaChange` 中回傳了 Python 風格的 `True`（在 TypeScript 中會是未定義的全域變數，可能導致 ReferenceError），以及 `handleConfirm` 中對 `jsonSchemaValue` 的型別檢查不夠嚴謹，可能讓非字串值進入 JSON.parse。此外，空 schema 的處理方式（設定為 undefined）可能與後端預期不符，需要確認。整體而言，功能方向合理，但需修正上述問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/app/configuration/config-var/config-modal/index.tsx:138` | 回傳未定義的 `True` 可能導致 ReferenceError | 0.95 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:311` | `jsonSchemaValue` 可能不是字串，導致 JSON.parse 收到非字串 | 0.80 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:255` | 空 schema 設定為 undefined 可能與後端預期不符 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:138</code> 回傳未定義的 `True` 可能導致 ReferenceError</summary>

在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳了 `True`（大寫 T）。在 TypeScript/JavaScript 中，`True` 不是內建的全域變數，除非有自訂的全域宣告，否則執行到此處會拋出 `ReferenceError: True is not defined`。這會中斷函式執行，且由於此函式是事件處理器，錯誤可能不會被明顯捕捉，導致 UI 行為異常。建議改為回傳 `true` 或直接不回傳值。

**判斷依據**：diff 中新增的 `return True` 行，在 TypeScript 中 `True` 未定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:311</code> `jsonSchemaValue` 可能不是字串，導致 JSON.parse 收到非字串</summary>

在 `handleConfirm` 中，`jsonSchemaValue` 的型別是 `InputVar['json_schema']`，可能是 `string | undefined`。程式碼先檢查 `!isSchemaEmpty && typeof jsonSchemaValue === 'string'`，但 `isSchemaEmpty` 的實作中，若 `value` 不是 null/undefined 且不是字串，會回傳 `false`。因此，若 `jsonSchemaValue` 是其他型別（例如數字或物件），`isSchemaEmpty` 會回傳 `false`，但 `typeof jsonSchemaValue === 'string'` 會是 `false`，所以不會進入 JSON.parse 的區塊，而是直接呼叫 `onConfirm`。這可能導致非字串的 schema 被儲存，與預期不符。建議在 `isJsonSchemaEmpty` 中明確處理非字串型別，或在此處增加型別檢查。

**判斷依據**：diff 中新增的型別檢查條件，但 `isSchemaEmpty` 對非字串型別的回傳值可能造成邏輯漏洞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:255</code> 空 schema 設定為 undefined 可能與後端預期不符</summary>

在 `handleConfirm` 中，若 schema 為空，會將 `json_schema` 設為 `undefined` 後傳給 `onConfirm`。這可能導致後端收到缺少 `json_schema` 欄位的 payload，若後端預期該欄位存在（即使是空字串），可能造成錯誤。建議確認後端 API 對 `json_schema` 的處理方式，或改為傳送空字串。

**判斷依據**：diff 中新增的 payloadToSave 邏輯，將空 schema 設為 undefined。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9012 (cache hit 8960) ｜ completion tokens 1046 ｜ PR #2</sub>