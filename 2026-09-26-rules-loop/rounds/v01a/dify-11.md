<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 MessageAgentThought 的 SQLAlchemy 型別標註，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤的內容給使用者；此外，新增的 AgentThoughtValidation 模型使用 Pydantic v1 語法且未實際使用，違反專案規範。整體而言，型別標註的改動合理，但邏輯錯誤需修正。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用 | 0.90 |
| ⚠️ | Major | `api/models/model.py:1838` | MessageAgentThought 繼承 TypeBase 可能改變既有行為 | 0.85 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:320` | message_price_unit 與 answer_price_unit 的預設值不一致 | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:365` | 字串串接方式改變可能影響效能與可讀性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，建立 ToolPromptMessage 時，content 參數使用了 `tool_inputs.get(tool, agent_thought.observation)`，但此處應為工具的回應內容，應使用 `tool_responses`。這會導致回傳給使用者的內容是工具的輸入而非輸出，造成資訊錯誤。

建議修正為：
```python
content=str(tool_responses.get(tool, agent_thought.observation)),
```

**判斷依據**：diff 中該行將原本的 `tool_responses.get(tool, agent_thought.observation)` 改為 `tool_inputs.get(...)`，但變數名稱與上下文顯示此處應為回應內容。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用</summary>

新增的 `AgentThoughtValidation` 模型使用了 Pydantic v1 的 `class Config` 語法，違反專案規範 R14（應使用 Pydantic v2 的 `ConfigDict`）。此外，該模型在程式碼中並未被使用，可能為冗餘程式碼。

建議：若此模型無實際用途，應移除；若需保留，應改用 Pydantic v2 語法：
```python
from pydantic import ConfigDict
class AgentThoughtValidation(BaseModel):
    model_config = ConfigDict(extra='forbid')
```

**判斷依據**：diff 中新增此模型，且未在其他地方引用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1838</code> MessageAgentThought 繼承 TypeBase 可能改變既有行為</summary>

將 `MessageAgentThought` 的基底類別從 `Base` 改為 `TypeBase`。若 `TypeBase` 有額外的行為（例如自動設定 `id`、`created_at` 或軟刪除），可能影響現有資料的相容性。需確認 `TypeBase` 的定義是否與原本的 `Base` 相容，特別是 `id` 欄位的預設值與 `init=False` 設定是否會影響現有程式碼中手動指定 `id` 的用法（例如測試中已移除 `id=fake.uuid4()`）。

**判斷依據**：diff 中將 `class MessageAgentThought(Base):` 改為 `class MessageAgentThought(TypeBase):`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:320</code> message_price_unit 與 answer_price_unit 的預設值不一致</summary>

在 `create_agent_thought` 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這與模型定義中的預設值（兩者皆為 `0.001`）不一致，可能導致資料不一致。請確認此處的意圖是否正確。

**判斷依據**：diff 中將原本的 `message_price_unit=0` 改為 `Decimal("0.001")`，但 `answer_price_unit` 改為 `Decimal(0)`，兩者不對稱。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:365</code> 字串串接方式改變可能影響效能與可讀性</summary>

將 `agent_thought.thought += thought` 改為 `agent_thought.thought = f"{existing_thought}{thought}"`。雖然功能相同，但 f-string 串接在大量累積時可能產生較多暫存物件。若 `thought` 可能為 `None`，此處的 `existing_thought` 已處理，但 `thought` 本身若為 `None` 會導致錯誤。建議確認 `thought` 參數是否可能為 `None`。

**判斷依據**：diff 中將原本的 `agent_thought.thought += thought` 改為上述兩行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8521 (cache hit 1536) ｜ completion tokens 1498 ｜ PR #11</sub>