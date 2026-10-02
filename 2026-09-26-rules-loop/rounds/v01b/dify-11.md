<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 MessageAgentThought 模型從 Base 改為 TypeBase，並加入 SQLAlchemy 2.0 型別註記，同時調整 create_agent_thought 的欄位初始化與 organize_agent_history 的解析邏輯。整體方向合理，但存在一個嚴重的邏輯錯誤：在 organize_agent_history 中，ToolPromptMessage 的 content 誤用 tool_inputs 而非 tool_responses，導致工具回應內容錯誤。此外，新增的 AgentThoughtValidation 模型使用 Pydantic v1 語法且未被使用，違反專案規範 R14。其他問題包括 Decimal 型別與 Numeric 欄位精度不一致、以及測試中移除 id 欄位可能影響測試隔離性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | ToolPromptMessage content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未被使用 | 0.90 |
| ⚠️ | Major | `api/models/model.py:1864` | Decimal 型別與 Numeric 欄位精度不一致 | 0.80 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_agent_service.py:232` | 測試中移除 id 欄位可能影響測試隔離性 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> ToolPromptMessage content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，建立 ToolPromptMessage 時，content 參數使用了 `tool_inputs.get(tool, agent_thought.observation)`，但此處應為工具的回應內容，應使用 `tool_responses.get(tool, agent_thought.observation)`。這會導致工具回應內容被錯誤地設定為工具輸入，造成後續處理錯誤。

建議修正：
```python
content=str(tool_responses.get(tool, agent_thought.observation)),
```

**判斷依據**：diff 中此行由原本的 `content=tool_responses.get(tool, agent_thought.observation)` 改為 `content=str(tool_inputs.get(tool, agent_thought.observation))`，但上下文顯示 tool_responses 才是正確的來源。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未被使用</summary>

新增的 `AgentThoughtValidation` 模型使用了 Pydantic v1 的 `class Config` 語法，且 `extra = "allow"` 與專案規範 R14 要求的 `ConfigDict(extra='forbid')` 不符。此外，此模型在 diff 中並未被任何程式碼使用，可能為冗餘程式碼。

建議：若此模型確實需要，應改用 Pydantic v2 語法：
```python
from pydantic import BaseModel, ConfigDict

class AgentThoughtValidation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ...
```
否則應移除。

**判斷依據**：diff 中新增此模型，且未見任何 import 或使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1864</code> Decimal 型別與 Numeric 欄位精度不一致</summary>

`message_unit_price` 和 `answer_unit_price` 的型別註記為 `Mapped[Decimal | None]`，但對應的資料庫欄位 `sa.Numeric` 未指定精度，可能導致小數位數不一致。而 `message_price_unit` 和 `answer_price_unit` 使用 `sa.Numeric(10, 7)` 並有 `Decimal("0.001")` 預設值，但型別註記為 `Mapped[Decimal]`，未考慮到資料庫可能回傳 `Decimal` 以外的型別（例如 float）。

建議：統一使用 `sa.Numeric(10, 7)` 並確保型別註記與實際儲存精度一致。

**判斷依據**：diff 中可見 `message_unit_price` 使用 `sa.Numeric` 無精度，而 `message_price_unit` 使用 `sa.Numeric(10, 7)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_agent_service.py:232</code> 測試中移除 id 欄位可能影響測試隔離性</summary>

多個測試中建立 `MessageAgentThought` 時移除了 `id=fake.uuid4()`，改為依賴模型的預設值。雖然模型已設定 `insert_default` 和 `default_factory`，但若測試依賴特定 id 進行後續操作，可能導致不穩定。建議確認測試中是否使用 id 進行查詢或斷言，若無則可接受。

**判斷依據**：diff 中多處移除 `id=fake.uuid4()`，例如在 `_create_test_agent_thoughts` 中。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8521 (cache hit 8448) ｜ completion tokens 1437 ｜ PR #11</sub>