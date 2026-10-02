<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 啟用 JSON_OBJECT 型別支援，並調整 JSON Schema 的儲存格式：不再包裝為 { type: 'object', properties: ... }，而是直接儲存使用者輸入的完整 schema。主要風險在於 handleJSONSchemaChange 中回傳了 Python 風格的 True（應為 true），以及 handleConfirm 中對 json_schema 的驗證與正規化邏輯可能造成非預期的 payload 變更。此外，多語系檔案僅新增兩個 key，未發現其他問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:139` | 回傳值 True 應為 true | 0.90 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:255` | payloadToSave 可能意外移除 json_schema | 0.80 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:314` | JSON Schema 驗證僅檢查 type 為 object，未驗證完整結構 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:139</code> 回傳值 True 應為 true</summary>

在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但在 JavaScript/TypeScript 中應為 `true`。這會導致呼叫端若依賴此回傳值判斷是否成功，將得到 ReferenceError（若未定義 True）或非預期的 truthy 值。

建議改為 `return true`。

**判斷依據**：diff 中新增的 `return True` 行，位於 handleJSONSchemaChange 函式內。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:255</code> payloadToSave 可能意外移除 json_schema</summary>

在 handleConfirm 中，若 isSchemaEmpty 為 true，則將 json_schema 設為 undefined。但此邏輯套用於所有型別，而不僅限於 jsonObject。若其他型別（如 string、number）的 tempPayload 中殘留了 json_schema 欄位（例如使用者先選 jsonObject 再切換型別），此變更會將該欄位移除，可能導致非預期的資料遺失。

建議僅在 type === InputVarType.jsonObject 時才進行此正規化。

**判斷依據**：diff 中新增的 payloadToSave 計算，未檢查 type。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:314</code> JSON Schema 驗證僅檢查 type 為 object，未驗證完整結構</summary>

在 handleConfirm 的 jsonObject 分支中，僅檢查 schema.type === 'object'，但未驗證 schema 是否符合 JSON Schema 規範（例如 properties 是否為物件、required 是否為陣列等）。若後端依賴 schema 的完整性，可能導致後續處理錯誤。

建議使用 JSON Schema 驗證函式庫（如 ajv）進行完整驗證，或至少檢查必要欄位。

**判斷依據**：diff 中新增的驗證邏輯僅檢查 type。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9012 (cache hit 8960) ｜ completion tokens 843 ｜ PR #2</sub>