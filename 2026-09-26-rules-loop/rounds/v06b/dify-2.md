<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 啟用 JSON_OBJECT 型別支援，並調整 JSON Schema 的處理方式：不再自動包裝為 {type:'object', properties:...}，而是直接儲存使用者輸入的完整 schema。主要風險在於 handleJSONSchemaChange 中回傳了 Python 風格的 `True`（TypeScript 中應為 `true`），可能導致型別錯誤或非預期行為；此外，移除 isSupportJSON 旗標後，所有非 Basic App 都會顯示 JSON Object 選項，需確認後端是否已全面支援。整體邏輯尚可，但需修正上述問題並補齊測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:139` | handleJSONSchemaChange 回傳 Python 風格的 `True`，應為 `true` | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:179` | 移除 isSupportJSON 旗標後，所有非 Basic App 都會顯示 JSON Object 選項 | 0.80 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:86` | jsonSchemaStr 現在直接顯示完整 schema，可能包含非 properties 的欄位 | 0.70 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:241` | isJsonSchemaEmpty 函式未處理非字串型別 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:139</code> handleJSONSchemaChange 回傳 Python 風格的 `True`，應為 `true`</summary>

在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳了 `True`（大寫 T），這在 TypeScript 中不是有效的布林值，會導致型別錯誤或非預期行為。應改為 `true`。

**判斷依據**：diff 中新增的 `return True` 行，TypeScript 中布林值為小寫 `true`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:179</code> 移除 isSupportJSON 旗標後，所有非 Basic App 都會顯示 JSON Object 選項</summary>

原本 `isSupportJSON` 為 `false`，因此 JSON Object 選項從未顯示。現在移除該旗標後，所有非 Basic App（Advanced Chat 和 Workflow）都會看到 JSON Object 選項。需確認後端是否已全面支援此型別，否則可能導致使用者選用後無法正常運作。

**判斷依據**：diff 中將 `(!isBasicApp && isSupportJSON)` 改為 `(!isBasicApp)`，且 `isSupportJSON` 原本為 `false`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:86</code> jsonSchemaStr 現在直接顯示完整 schema，可能包含非 properties 的欄位</summary>

原本 `jsonSchemaStr` 只顯示 `properties` 內容，現在改為顯示完整 schema。若 schema 中包含 `type`、`required` 等欄位，使用者會看到這些內容，可能造成混淆。需確認 UI 設計是否預期顯示完整 schema。

**判斷依據**：diff 中將 `JSON.parse(tempPayload.json_schema).properties` 改為 `JSON.parse(tempPayload.json_schema)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:241</code> isJsonSchemaEmpty 函式未處理非字串型別</summary>

`isJsonSchemaEmpty` 函式在 `value` 為非字串且非 null/undefined 時回傳 `false`，但未考慮其他型別（如物件）。雖然目前 `json_schema` 應為字串，但若未來型別變更可能導致誤判。建議明確處理或使用型別守衛。

**判斷依據**：diff 中新增的 `isJsonSchemaEmpty` 函式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11681 (cache hit 11648) ｜ completion tokens 970 ｜ PR #2</sub>