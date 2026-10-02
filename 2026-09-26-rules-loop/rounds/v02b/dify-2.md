<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 啟用 JSON_OBJECT 型別支援，並調整 JSON Schema 的處理邏輯：不再自動包裝為 { type: 'object', properties: ... }，而是直接儲存使用者輸入的完整 schema。主要風險在於 handleJSONSchemaChange 中回傳了 Python 風格的 True（TypeScript 中應為 true），可能導致型別錯誤或非預期行為；此外，移除 jsonObjectWrap 後，舊有已儲存的 schema 若仍為包裝格式，可能造成顯示或驗證不一致。整體方向合理，但需修正 True 並確認向後相容性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/app/components/app/configuration/config-var/config-modal/index.tsx:138` | 回傳值 True 應為 true（TypeScript 布林值） | 0.90 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:86` | 移除 jsonObjectWrap 可能導致舊資料顯示不一致 | 0.70 |
| 🔸 | Minor | `web/app/components/app/configuration/config-var/config-modal/index.tsx:138` | handleJSONSchemaChange 回傳值不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:138</code> 回傳值 True 應為 true（TypeScript 布林值）</summary>

在 handleJSONSchemaChange 中，成功解析後回傳了 `True`（Python 風格），但 TypeScript 中布林值應為 `true`。這會導致型別錯誤（若函式有明確回傳型別）或非預期行為（例如呼叫端若檢查回傳值是否為 true 會失敗）。請改為 `return true`。

**判斷依據**：diff 中新增的 `return True` 行，TypeScript 不認得 `True`，會視為未定義的變數或型別錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:86</code> 移除 jsonObjectWrap 可能導致舊資料顯示不一致</summary>

原本 jsonSchemaStr 會從 tempPayload.json_schema 解析後取出 `.properties` 顯示，現在直接顯示整個 schema。若舊有已儲存的 schema 是包裝格式（含 type: 'object' 與 properties），則編輯時會顯示完整包裝，但使用者可能只預期看到 properties 內容。建議確認資料遷移或提供相容處理。

**判斷依據**：diff 中將原本的 `.properties` 改為直接回傳整個解析結果，但未處理舊格式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/app/configuration/config-var/config-modal/index.tsx:138</code> handleJSONSchemaChange 回傳值不一致</summary>

函式在空值時回傳 null，成功時回傳 True（應為 true），失敗時回傳 null。回傳值似乎未被使用，建議確認是否真的需要回傳值，或統一為 void。

**判斷依據**：diff 中新增的回傳值，但呼叫端未使用，可能造成混淆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11691 (cache hit 11648) ｜ completion tokens 771 ｜ PR #2</sub>