<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 MessageAgentThought 模型從 Base 改為 TypeBase，並加入型別註記與 Decimal 預設值，同時調整 agent runner 中相關邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 改為使用 tool_inputs 而非 tool_responses，可能導致工具輸出內容錯誤；此外，模型欄位型別與預設值變更可能影響既有資料相容性。建議優先修正 tool_call_response 的內容來源，並確認 Decimal 預設值與資料庫 schema 的一致性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | 工具回應內容誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/models/model.py:1865` | message_price_unit 與 answer_price_unit 的 Python 端預設值與資料庫 server_default 不一致 | 0.80 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:320` | create_agent_thought 中 message_price_unit 與 answer_price_unit 的初始值可能導致價格計算錯誤 | 0.75 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:52` | AgentThoughtValidation 模型未被使用 | 0.70 |
| 🔸 | Minor | `api/models/model.py:1851` | created_by_role 型別從 String 改為 Mapped[str]，但未使用 Enum 型別 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> 工具回應內容誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本 ToolPromptMessage 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具呼叫的回應內容變成工具的輸入參數，而非實際的輸出結果，造成對話歷史中工具回應錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史訊息中的工具回應會顯示輸入參數而非輸出，導致後續 LLM 判斷錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

**判斷依據**：diff 中該行由 `content=tool_responses.get(tool, agent_thought.observation)` 改為 `content=str(tool_inputs.get(tool, agent_thought.observation))`，明顯誤用變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1865</code> message_price_unit 與 answer_price_unit 的 Python 端預設值與資料庫 server_default 不一致</summary>

在 MessageAgentThought 模型中，`message_price_unit` 和 `answer_price_unit` 的 Python 端預設值設為 `Decimal("0.001")`，但資料庫的 `server_default` 也是 `sa.text("0.001")`。這看似一致，但若資料庫中已有舊資料，其值可能為 0 或其他數值，而 Python 端預設值僅在新建物件時生效。此外，`message_unit_price` 和 `answer_unit_price` 的 Python 端預設值為 `None`，但資料庫欄位為 nullable=True，這可能導致後續計算時出現 None 相加的錯誤。

失敗情境：若程式碼中直接使用 `message_unit_price` 進行數值運算，且該值為 None，會拋出 TypeError。

建議：確認所有使用這些欄位進行計算的地方都有處理 None 值，或將欄位設為非 nullable 並提供預設值。

**判斷依據**：diff 中新增了 Python 端 default，但未處理既有資料可能為 0 或 NULL 的情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:320</code> create_agent_thought 中 message_price_unit 與 answer_price_unit 的初始值可能導致價格計算錯誤</summary>

在 create_agent_thought 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這與模型定義中的預設值相反（模型定義中 message_price_unit 預設為 0.001，answer_price_unit 預設為 0.001）。這可能導致後續價格計算時，answer 部分的價格被錯誤地乘以 0，造成總價低估。

失敗情境：當 agent 產生 answer 時，若未更新 answer_price_unit，則總價計算會將 answer 的 token 數乘以 0，導致費用計算錯誤。

建議：確認初始值應與模型預設值一致，或明確設定為正確的價格單位。

**判斷依據**：diff 中顯示 create_agent_thought 將 message_price_unit 設為 0.001，但 answer_price_unit 設為 0，與模型定義的預設值不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:52</code> AgentThoughtValidation 模型未被使用</summary>

新增的 AgentThoughtValidation 類別似乎未被任何程式碼使用。這可能是為了未來的驗證而準備，但目前是死碼。

建議：若暫時不使用，可考慮移除或加上 TODO 註解說明用途。

**判斷依據**：diff 中新增了該類別，但未見其他程式碼引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1851</code> created_by_role 型別從 String 改為 Mapped[str]，但未使用 Enum 型別</summary>

在 MessageAgentThought 中，`created_by_role` 的型別從原本的 `mapped_column(String(255), nullable=False)` 改為 `Mapped[str]`，但未使用 `CreatorUserRole` Enum 型別。這可能導致型別安全性降低，且與其他模型（如 MessageFile）的作法不一致。

建議：考慮使用 `Mapped[CreatorUserRole]` 並搭配 SQLAlchemy 的 Enum 型別。

**判斷依據**：diff 中該行型別改為 Mapped[str]，但未使用 Enum。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10327 (cache hit 1536) ｜ completion tokens 1597 ｜ PR #11</sub>