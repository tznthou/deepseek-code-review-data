<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要重構 MessageAgentThought 的 SQLAlchemy 型別註記，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 改為使用 tool_inputs 而非 tool_responses，可能造成語意錯誤；此外新增的 AgentThoughtValidation 模型使用 Pydantic v1 語法，違反專案規範 R14。整體改動尚可，但需修正上述問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:502` | organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs | 0.90 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法 | 0.85 |
| 🔸 | Minor | `api/models/model.py:1838` | MessageAgentThought 改繼承 TypeBase 可能影響既有行為 | 0.70 |
| 🔸 | Minor | `api/models/model.py:1846` | id 欄位同時使用 insert_default 和 default_factory 可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:502</code> organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs</summary>

在 `organize_agent_history` 中，原本 `ToolPromptMessage` 的 `content` 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果，可能造成後續處理錯誤。

**失敗情境**：當 agent 使用工具並產生 observation 時，歷史訊息中的工具回應會錯誤地顯示輸入參數，而非工具輸出。

**建議**：改回使用 `tool_responses`，或確認此變更為有意為之。

**判斷依據**：diff 中將 `content=tool_responses.get(tool, agent_thought.observation)` 改為 `content=str(tool_inputs.get(tool, agent_thought.observation))`，但 `tool_inputs` 是工具輸入，非回應。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法</summary>

新增的 `AgentThoughtValidation` 模型使用 `class Config: extra = "allow"`，這是 Pydantic v1 的寫法。專案規範 R14 要求使用 Pydantic v2 並以 `ConfigDict(extra='forbid')` 設定。此模型目前未見實際使用，但若未來啟用，可能導致未預期的欄位被允許。

**建議**：改用 Pydantic v2 語法：
```python
from pydantic import BaseModel, ConfigDict

class AgentThoughtValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ...
```

**判斷依據**：diff 中新增的 `AgentThoughtValidation` 類別包含 `class Config: extra = "allow"`，違反 R14。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1838</code> MessageAgentThought 改繼承 TypeBase 可能影響既有行為</summary>

`MessageAgentThought` 原本繼承 `Base`，現在改為繼承 `TypeBase`。`TypeBase` 可能包含額外的 mixin 行為（如軟刪除、時間戳等），需確認此變更不會影響資料庫操作或 ORM 行為。

**建議**：確認 `TypeBase` 的定義，並驗證相關測試是否通過。

**判斷依據**：diff 中將 `class MessageAgentThought(Base):` 改為 `class MessageAgentThought(TypeBase):`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1846</code> id 欄位同時使用 insert_default 和 default_factory 可能造成混淆</summary>

`id` 欄位設定為 `insert_default=lambda: str(uuid4()), default_factory=lambda: str(uuid4()), init=False`。同時使用 `insert_default` 和 `default_factory` 可能導致行為不一致，特別是在不同 SQLAlchemy 版本或操作情境下。

**建議**：確認兩者同時存在的必要性，或僅保留一個。

**判斷依據**：diff 中 `id` 欄位同時指定 `insert_default` 和 `default_factory`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8531 (cache hit 8448) ｜ completion tokens 1178 ｜ PR #11</sub>