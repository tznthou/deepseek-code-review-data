<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 MessageAgentThought 的 SQLAlchemy 型別標註，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤的內容給使用者；此外，AgentThoughtValidation 模型使用 Pydantic v1 語法且未實際用於驗證，以及部分欄位型別與預設值變更可能影響既有行為。建議優先修正 tool_call_response 的資料來源錯誤。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際用於驗證 | 0.80 |
| ⚠️ | Major | `api/models/model.py:1838` | MessageAgentThought 從 Base 改為 TypeBase 可能影響既有功能 | 0.75 |
| 🔸 | Minor | `api/models/model.py:1865` | message_price_unit 和 answer_price_unit 的預設值變更可能影響既有資料 | 0.60 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:365` | save_agent_thought 中 thought 串接方式改變可能引入效能問題 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本 tool_call_response 的 content 是 `tool_responses.get(tool, agent_thought.observation)`，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給使用者的內容是工具的輸入參數，而不是工具的執行結果，造成資訊錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，使用者會看到工具的輸入而非輸出，可能誤導使用者或洩漏不應公開的輸入資料。

建議修正：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並視需要轉為字串。

**判斷依據**：diff 中此行將原本的 `tool_responses` 改為 `tool_inputs`，且前文已正確解析 `tool_responses`，此處明顯為筆誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際用於驗證</summary>

新增的 `AgentThoughtValidation` 模型使用 `class Config: extra = "allow"`，這是 Pydantic v1 的寫法，但專案規範 R14 要求使用 Pydantic v2。此外，該模型在 diff 中沒有被任何地方使用，無法發揮驗證作用。

建議：改用 Pydantic v2 的 `model_config = ConfigDict(extra='allow')`，並在建立 MessageAgentThought 前實際使用此模型進行驗證，或移除未使用的模型。

**判斷依據**：diff 新增此類別，但未見任何 import 或使用；且 `class Config` 為 Pydantic v1 寫法，違反 R14。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1838</code> MessageAgentThought 從 Base 改為 TypeBase 可能影響既有功能</summary>

原本 `MessageAgentThought` 繼承自 `Base`，現在改為 `TypeBase`。需要確認 `TypeBase` 是否提供與 `Base` 相同的功能，例如自動產生 `id`、`created_at` 等。若 `TypeBase` 缺少某些 mixin 或行為，可能導致資料模型行為不一致。

建議：確認 `TypeBase` 的定義，確保所有必要的欄位和行為都保留，並執行相關測試。

**判斷依據**：diff 中類別繼承從 `Base` 改為 `TypeBase`，但未提供 `TypeBase` 的定義，無法確認其相容性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1865</code> message_price_unit 和 answer_price_unit 的預設值變更可能影響既有資料</summary>

原本 `message_price_unit` 的 server_default 為 '0.001'，現在改為 Python 端 default 為 Decimal('0.001')，同時保留 server_default。這可能導致新建立的記錄在 Python 端使用 Decimal 型別，而既有資料庫中的值可能為 float 或 Decimal，型別不一致可能引發比較或計算問題。

建議：確認所有寫入路徑都使用 Decimal，並考慮是否需要 migration 來統一型別。

**判斷依據**：diff 中新增 `default=Decimal("0.001")`，但未見對既有資料的處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:365</code> save_agent_thought 中 thought 串接方式改變可能引入效能問題</summary>

原本使用 `agent_thought.thought += thought`，現在改為 `agent_thought.thought = f"{existing_thought}{thought}"`。雖然功能相同，但若 thought 欄位很大，f-string 會建立新字串，可能造成記憶體壓力。不過此處 thought 通常不大，影響有限。

建議：若無特殊原因，可保留原本的 `+=` 寫法。

**判斷依據**：diff 中此段修改，但未見明顯必要。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7082 (cache hit 4992) ｜ completion tokens 1548 ｜ PR #11</sub>