<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 啟用 JSON_OBJECT 型別支援，並調整 JSON Schema 的處理邏輯：不再自動包裝為 {type:'object', properties:...}，而是直接儲存使用者輸入的完整 schema。主要風險在於 handleJSONSchemaChange 中回傳 True（Python 風格）而非 true，以及移除 isSupportJSON 後可能對所有應用型別開放 JSON 輸入，需確認是否符合產品預期。整體邏輯尚可，但需修正型別錯誤並補齊測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:138` | 回傳值 True 應為 true（JavaScript 布林值） | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:179` | 移除 isSupportJSON 後，所有應用型別皆可選用 JSON 輸入，可能造成非預期行為 | 0.80 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:237` | isJsonSchemaEmpty 函式可簡化，且型別判斷可能不完整 | 0.70 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:314` | JSON Schema 驗證僅檢查 type 為 object，未驗證其他 schema 有效性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:138</code> 回傳值 True 應為 true（JavaScript 布林值）</summary>

在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳 `True`，但 JavaScript 中布林值應為小寫 `true`。`True` 未定義，會導致 ReferenceError，使函式在成功路徑拋出例外。

失敗情境：使用者輸入合法 JSON 時，`JSON.parse` 成功，接著執行 `return True`，此時會拋出 `ReferenceError: True is not defined`，導致 `handlePayloadChange` 已執行但函式回傳錯誤，可能影響後續邏輯。

建議改為 `return true`。

**判斷依據**：diff 中新增的 `return True` 位於 `handleJSONSchemaChange` 函式內，且前一行為 `handlePayloadChange('json_schema')(value)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:179</code> 移除 isSupportJSON 後，所有應用型別皆可選用 JSON 輸入，可能造成非預期行為</summary>

原本 `isSupportJSON` 為 `false`，因此 JSON 選項從未顯示。此 PR 移除該變數，使 `!isBasicApp` 成立時（即 ADVANCED_CHAT 或 WORKFLOW 模式）就會顯示 JSON 輸入選項。若後端尚未完整支援 JSON 輸入，可能導致使用者建立無法正常運作的變數。

建議確認後端已完整支援 JSON 輸入，或保留某種 feature flag 控制顯示。

**判斷依據**：diff 中將 `...((!isBasicApp && isSupportJSON)` 改為 `...((!isBasicApp)`，且 `isSupportJSON` 變數被刪除。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:237</code> isJsonSchemaEmpty 函式可簡化，且型別判斷可能不完整</summary>

`isJsonSchemaEmpty` 檢查 `value` 是否為 null/undefined 或空字串，但若 `value` 為非字串型別（例如物件），則回傳 `false`，表示非空。然而 `json_schema` 的型別可能為 `string | undefined`，此處的 `typeof value !== 'string'` 分支可能永遠不會執行。建議確認型別定義，若確定只會是 string 或 undefined，可簡化邏輯。

**判斷依據**：新增的函式包含對非字串型別的處理，但型別定義可能不允許。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:314</code> JSON Schema 驗證僅檢查 type 為 object，未驗證其他 schema 有效性</summary>

在 `handleConfirm` 中，對 JSON 輸入僅檢查解析後的 `schema.type === 'object'`，但未驗證 schema 是否符合 JSON Schema 規範（例如 properties 是否為物件、required 是否為陣列等）。若使用者輸入 `{ "type": "object", "properties": "invalid" }`，仍會通過驗證並儲存，可能導致後續使用錯誤。

建議使用 JSON Schema 驗證函式庫（如 ajv）進行完整驗證，或至少檢查必要欄位型別。

**判斷依據**：新增的驗證邏輯僅檢查 `type` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11681 (cache hit 8960) ｜ completion tokens 1267 ｜ PR #2</sub>