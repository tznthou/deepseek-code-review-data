<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要重構 MessageAgentThought 的 SQLAlchemy 型別標註，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤內容；此外，AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用，違反專案規範。整體改動尚可，但需修正上述問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:502` | organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs | 0.90 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用 | 0.85 |
| 🔸 | Minor | `api/models/model.py:1838` | MessageAgentThought 改為繼承 TypeBase 可能影響既有行為 | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:320` | create_agent_thought 中 message_price_unit 設為 Decimal("0.001") 可能不符預期 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:502</code> organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs</summary>

在建立 ToolPromptMessage 時，content 使用了 `tool_inputs.get(tool, agent_thought.observation)`，但此處應為工具回應內容，應使用 `tool_responses.get(tool, observation_payload)`。這會導致回傳給模型的工具回應內容錯誤，可能造成模型產生錯誤的後續行為。

**判斷依據**：diff 中新增行 `content=str(tool_inputs.get(tool, agent_thought.observation)),`，而前文已解析 `tool_responses`，此處應使用 `tool_responses`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用</summary>

新增的 `AgentThoughtValidation` 類別使用了 Pydantic v1 的 `class Config` 語法，違反專案規範 R14（應使用 Pydantic v2 的 `ConfigDict`）。此外，此類別在 diff 中並未被任何程式碼使用，可能為冗餘程式碼。

**判斷依據**：diff 新增 `class AgentThoughtValidation(BaseModel):` 及其內部 `class Config`，且未見其他引用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1838</code> MessageAgentThought 改為繼承 TypeBase 可能影響既有行為</summary>

將 `MessageAgentThought` 的基底類別從 `Base` 改為 `TypeBase`。若 `TypeBase` 有額外的行為（如自動設定 `id` 或時間戳），可能影響既有資料建立流程。需確認此變更不會破壞現有功能。

**判斷依據**：diff 中 `-class MessageAgentThought(Base):` 改為 `+class MessageAgentThought(TypeBase):`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:320</code> create_agent_thought 中 message_price_unit 設為 Decimal("0.001") 可能不符預期</summary>

原本 `message_price_unit=0`，現改為 `Decimal("0.001")`。若此欄位代表每單位價格，預設值變更可能影響計費邏輯。需確認此變更是否為刻意調整。

**判斷依據**：diff 中 `-message_price_unit=0,` 改為 `+message_price_unit=Decimal("0.001"),`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8441 (cache hit 4992) ｜ completion tokens 961 ｜ PR #11</sub>