<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 MessageAgentThought 模型從 Base 改為 TypeBase，並加入型別註記與預設值，同時調整 base_agent_runner.py 中的建立與處理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 改為使用 tool_inputs 而非 tool_responses，可能造成工具回應內容錯誤；此外 AgentThoughtValidation 使用 Pydantic v1 的 Config 語法，違反 R14。整體而言，型別改進方向正確，但需修正上述問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | 工具回應內容錯誤：使用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法 | 0.90 |
| ⚠️ | Major | `api/models/model.py:1853` | message_chain_id 欄位缺少 Mapped 型別註記 | 0.85 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:320` | message_price_unit 預設值從 0 改為 0.001 可能影響計費 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> 工具回應內容錯誤：使用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，ToolPromptMessage 的 content 原本使用 `tool_responses.get(tool, agent_thought.observation)`，現在改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果。例如，當工具輸入為 `{"query": "..."}` 且觀察結果為 `{"result": "..."}` 時，回應會錯誤地顯示輸入內容。建議改回使用 `tool_responses`。

**判斷依據**：diff 中此行將原本的 `tool_responses.get` 改為 `tool_inputs.get`，且未見其他邏輯調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法</summary>

AgentThoughtValidation 類別使用 `class Config: extra = "allow"`，這是 Pydantic v1 的寫法。根據規範 R14，應使用 Pydantic v2 的 `model_config = ConfigDict(extra='forbid')`。此外，目前設定為 allow 可能允許未宣告的欄位，與規範的 forbid 預設不符。

**判斷依據**：diff 中新增的 AgentThoughtValidation 類別包含 Pydantic v1 的 Config 語法，且註解也指出應使用 ConfigDict。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1853</code> message_chain_id 欄位缺少 Mapped 型別註記</summary>

在 MessageAgentThought 模型中，`message_chain_id` 欄位定義為 `message_chain_id: Mapped[str | None] = mapped_column(StringUUID, nullable=True, default=None)`，但其他欄位如 `id`、`message_id` 都有明確的 `Mapped` 型別。此處缺少 `Mapped` 可能導致型別檢查不一致。建議補上 `Mapped[str | None]`。

**判斷依據**：diff 中此行未包含 Mapped 型別註記，與其他欄位不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:320</code> message_price_unit 預設值從 0 改為 0.001 可能影響計費</summary>

在 create_agent_thought 中，`message_price_unit` 從 `0` 改為 `Decimal("0.001")`，`answer_unit_price` 從 `0` 改為 `Decimal("0.001")`。這可能改變計費邏輯，若原本預期為 0 則可能導致費用計算錯誤。請確認此變更是否符合預期。

**判斷依據**：diff 中將原本的 `message_price_unit=0` 改為 `Decimal("0.001")`，且未見相關說明。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8522 (cache hit 1536) ｜ completion tokens 1093 ｜ PR #11</sub>