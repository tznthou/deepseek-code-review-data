<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 MessageAgentThought 的 SQLAlchemy 型別標註，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤的內容給模型；此外，新增的 AgentThoughtValidation 模型使用 Pydantic v1 語法且未實際使用，違反專案規範。整體改動尚可，但需修正上述問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用 | 0.90 |
| ⚠️ | Major | `api/models/model.py:1838` | MessageAgentThought 改為繼承 TypeBase 可能影響既有行為 | 0.85 |
| 🔸 | Minor | `api/models/model.py:1846` | id 欄位同時使用 insert_default 與 default_factory 可能造成混淆 | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:320` | message_price_unit 與 answer_price_unit 的預設值不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs</summary>

在建立 ToolPromptMessage 時，content 參數使用了 `tool_inputs.get(tool, agent_thought.observation)`，但此處應使用 `tool_responses` 來取得工具的回應內容。這會導致回傳給模型的工具回應內容錯誤（變成輸入參數），可能造成模型產生錯誤的後續行為。

建議修正為：
```python
content=str(tool_responses.get(tool, observation_payload)),
```

**判斷依據**：diff 中此行將原本的 `tool_responses.get(tool, agent_thought.observation)` 改為 `tool_inputs.get(tool, agent_thought.observation)`，但上下文顯示此處應為工具回應。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用</summary>

新增的 `AgentThoughtValidation` 模型使用了 Pydantic v1 的 `class Config` 語法，違反專案規範 R14（應使用 Pydantic v2 的 `ConfigDict`）。此外，此模型在程式碼中並未被使用，可能為冗餘程式碼。

建議：
- 若需保留，改用 `model_config = ConfigDict(extra='forbid')`。
- 若未使用，應移除。

**判斷依據**：diff 新增此類別，但未見任何使用；且 `class Config` 為 Pydantic v1 寫法。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1838</code> MessageAgentThought 改為繼承 TypeBase 可能影響既有行為</summary>

將 `MessageAgentThought` 的基底類別從 `Base` 改為 `TypeBase`，可能改變其 ORM 行為（例如是否自動加入 tenant_id 等欄位）。需確認 `TypeBase` 的定義與此模型相容，且不會影響現有查詢或資料隔離。

建議：檢查 `TypeBase` 的實作，確認此變更不會引入非預期的欄位或約束。

**判斷依據**：diff 將 `class MessageAgentThought(Base):` 改為 `class MessageAgentThought(TypeBase):`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1846</code> id 欄位同時使用 insert_default 與 default_factory 可能造成混淆</summary>

`id` 欄位同時設定了 `insert_default` 和 `default_factory`，兩者皆用於產生 UUID。這可能導致行為不一致或非預期的覆蓋。建議僅保留一個，或確認兩者的使用情境。

**判斷依據**：diff 中此欄位同時出現 `insert_default` 與 `default_factory`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:320</code> message_price_unit 與 answer_price_unit 的預設值不一致</summary>

在 `create_agent_thought` 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這可能與模型定義中的 server_default 不一致，需確認是否為預期行為。

**判斷依據**：diff 中 `message_price_unit` 與 `answer_price_unit` 的預設值不同，且與模型定義的 server_default 可能不符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8531 (cache hit 4992) ｜ completion tokens 1386 ｜ PR #11</sub>