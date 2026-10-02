<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 啟用 JSON_OBJECT 型別支援，並調整 JSON Schema 的儲存格式（從只存 properties 改為存完整 schema）。主要風險在於 `handleJSONSchemaChange` 中出現未定義的 `True`，會導致執行時 ReferenceError；此外 `handleConfirm` 中對 JSON Schema 的驗證僅檢查 `type === 'object'`，未驗證 schema 結構完整性，可能讓無效 schema 被儲存。建議先修正 `True` 的錯誤，並考慮加入更完整的 schema 驗證。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `web/app/components/app/configuration/config-var/config-modal/index.tsx:138` | 未定義的 `True` 會導致 ReferenceError | 0.99 |
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:314` | JSON Schema 驗證不完整，可能接受無效 schema | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:138</code> 未定義的 `True` 會導致 ReferenceError</summary>

在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳 `True`，但 `True` 並未定義（JavaScript 中布林值為 `true`，非 `True`）。這會導致執行時拋出 `ReferenceError: True is not defined`，使函式無法正常完成。

**失敗情境**：使用者在 JSON Schema 編輯器中輸入合法 JSON 並觸發 onChange，函式會拋出錯誤，可能導致 UI 中斷或狀態未更新。

**建議**：將 `return True` 改為 `return true`。

**判斷依據**：diff 中新增的 `return True` 行，`True` 在 JavaScript 中不是保留字，且未在檔案中定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:314</code> JSON Schema 驗證不完整，可能接受無效 schema</summary>

在 `handleConfirm` 中，對 JSON Schema 的驗證僅檢查 `schema?.type === 'object'`，但未驗證其他必要欄位（如 `properties` 是否存在、是否為物件等）。這可能讓使用者輸入如 `{"type": "object"}` 的 schema 通過驗證，但後續使用該 schema 的程式碼可能假設 `properties` 存在而導致錯誤。

**失敗情境**：使用者輸入 `{"type": "object"}` 並儲存，之後使用該變數時，程式碼嘗試存取 `schema.properties` 可能得到 `undefined`，進而引發錯誤。

**建議**：除了檢查 `type`，也應驗證 `properties` 是否存在且為物件，或使用更完整的 JSON Schema 驗證函式庫。

**判斷依據**：diff 中新增的驗證區塊，只檢查 `type`，未檢查其他 schema 結構。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12087 (cache hit 1536) ｜ completion tokens 771 ｜ PR #2</sub>