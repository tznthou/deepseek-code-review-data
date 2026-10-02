<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多處 LIKE 查詢改為使用統一的 escape_like_pattern 函式，並加上 ESCAPE 子句，以正確處理使用者輸入中的特殊字元（%、_、\）。整體方向正確，能有效防止 LIKE 萬用字元注入。但仍有幾處實作細節需要修正：部分呼叫未加上 escape 參數、Clickzetta 的 ESCAPE 語法可能錯誤、以及 workflow_app_service 中對既有 unicode_escape 邏輯的移除可能改變行為。建議修正後再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/rag/retrieval/dataset_retrieval.py:1207` | notlike 未指定 escape 參數，導致跳脫失效 | 0.90 |
| ⚠️ | Major | `api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991` | Clickzetta 的 ESCAPE 語法可能不正確 | 0.80 |
| ⚠️ | Major | `api/services/workflow_app_service.py:94` | 移除 unicode_escape 可能改變搜尋行為 | 0.80 |
| 🔸 | Minor | `api/libs/helper.py:61` | escape_like_pattern 未處理 None 以外的 falsy 值 | 0.70 |
| 🔸 | Minor | `api/services/dataset_service.py:147` | 使用 helper.escape_like_pattern 但未明確 import | 0.70 |
| 🔸 | Minor | `api/controllers/console/app/conversation.py:346` | 函式內 import 可能違反 import 順序規範 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/retrieval/dataset_retrieval.py:1207</code> notlike 未指定 escape 參數，導致跳脫失效</summary>

在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會使 `escape_like_pattern` 產生的跳脫字元（如 `\%`）被資料庫視為一般字元，無法正確比對包含 `%` 或 `_` 的字串。

**失敗情境**：當使用者搜尋「不包含 50%」時，若資料中有「100%」，因為 `%` 未被跳脫，`notlike` 會將 `%` 視為萬用字元，導致「100%」也被排除，結果不正確。

**建議**：加上 `escape="\\"` 參數，與其他 like 呼叫保持一致。

**判斷依據**：diff 中該行未包含 escape 參數，而其他 like 呼叫均有。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/rag/datasource/vdb/clickzetta/clickzetta_vector.py:991</code> Clickzetta 的 ESCAPE 語法可能不正確</summary>

在 Clickzetta 的 SQL 中，`ESCAPE '\\\\'` 使用了四個反斜線，這可能導致資料庫將跳脫字元視為兩個反斜線，而非單一反斜線。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，跳脫可能失效，導致萬用字元被展開，回傳過多結果。

**建議**：確認 Clickzetta 的 ESCAPE 語法，通常應為 `ESCAPE '\\'`（兩個反斜線代表一個反斜線字元）。

**判斷依據**：diff 中該行使用了四個反斜線，與其他檔案中的 `escape="\\"` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/services/workflow_app_service.py:94</code> 移除 unicode_escape 可能改變搜尋行為</summary>

原本的程式碼使用 `keyword[:30].encode('unicode_escape').decode('utf-8')` 來處理關鍵字，這會將非 ASCII 字元轉換為 `\uXXXX` 形式，以符合 JSON 欄位中的儲存格式。新的程式碼直接使用 `escape_like_pattern`，不再進行 unicode_escape，可能導致搜尋非 ASCII 字元時無法匹配。

**失敗情境**：當使用者搜尋中文關鍵字時，原本可以匹配到 JSON 中儲存的 `\u4e2d\u6587`，但新程式碼只會搜尋原始中文字元，導致找不到結果。

**建議**：保留 unicode_escape 處理，或確認 JSON 欄位儲存格式已變更。

**判斷依據**：diff 中移除了原本的 unicode_escape 處理，直接使用 escape_like_pattern。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/helper.py:61</code> escape_like_pattern 未處理 None 以外的 falsy 值</summary>

函式開頭 `if not pattern: return pattern` 會將空字串、None 等 falsy 值原樣回傳。雖然空字串回傳空字串是合理的，但若傳入非字串型別（如整數 0），會回傳 0，可能導致後續 f-string 產生非預期結果。

**建議**：明確檢查 `if pattern is None: return pattern`，並考慮對非字串型別拋出例外或轉型。

**判斷依據**：diff 中該函式僅以 falsy 判斷，未做型別檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/services/dataset_service.py:147</code> 使用 helper.escape_like_pattern 但未明確 import</summary>

在 `dataset_service.py` 中，呼叫 `helper.escape_like_pattern`，但 diff 中未顯示 `helper` 的 import 來源。若 `helper` 是模組別名，需確認已正確 import；否則可能導致 NameError。

**建議**：確認檔案頂部有 `from libs import helper` 或類似 import。

**判斷依據**：diff 中該行使用了 `helper.escape_like_pattern`，但未見 import 變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/controllers/console/app/conversation.py:346</code> 函式內 import 可能違反 import 順序規範</summary>

在函式內進行 `from libs.helper import escape_like_pattern`，可能違反專案的 import 排序規則（R02）。雖然有時是為了避免循環依賴，但此處看不出有循環依賴的必要。

**建議**：將 import 移至檔案頂部，除非有明確的循環依賴問題。

**判斷依據**：diff 中多處在函式內 import，可能觸發 ruff 的 import 規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16065 (cache hit 16000) ｜ completion tokens 1659 ｜ PR #12</sub>