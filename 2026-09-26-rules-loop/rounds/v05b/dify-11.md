<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 MessageAgentThought 模型的 SQLAlchemy 型別標註，並調整 agent thought 建立與歷史整理的邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 改為使用 tool_inputs 而非 tool_responses，這可能導致回傳錯誤的內容給前端；此外，新增的 AgentThoughtValidation 模型使用 Pydantic v1 語法且未實際使用，違反專案規範。整體而言，型別改進方向正確，但需修正上述邏輯錯誤與規範違反。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用 | 0.90 |
| ⚠️ | Major | `api/models/model.py:1838` | MessageAgentThought 改為繼承 TypeBase 可能導致 id 欄位型別不一致 | 0.85 |
| 🔸 | Minor | `api/models/model.py:1846` | id 欄位同時使用 insert_default 和 default_factory 可能造成混淆 | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:319` | message_price_unit 和 answer_price_unit 的預設值不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本 tool_call_response 的 content 是 `tool_responses.get(tool, agent_thought.observation)`，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給前端的工具回應內容變成工具輸入，而非實際的觀察結果，造成資料錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，前端會收到錯誤的工具回應內容，可能導致對話歷史顯示錯誤或下游處理異常。

建議：將該行改回使用 `tool_responses`，例如 `content=str(tool_responses.get(tool, agent_thought.observation))`。

**判斷依據**：diff 中第 499 行將原本的 `tool_responses.get(tool, agent_thought.observation)` 改為 `tool_inputs.get(tool, agent_thought.observation)`，但此處應為工具回應內容，而非輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> [R14] AgentThoughtValidation 使用 Pydantic v1 語法且未實際使用</summary>

新增的 `AgentThoughtValidation` 模型使用了 Pydantic v1 的 `class Config` 語法，且 `extra = "allow"` 與專案規範 R14 要求的 `ConfigDict(extra='forbid')` 不符。此外，該模型在程式碼中並未被使用，屬於冗餘程式碼。

建議：若此模型確實需要，應改用 Pydantic v2 語法，例如 `model_config = ConfigDict(extra='forbid')`，並確保其被實際用於驗證；否則應移除。

**判斷依據**：diff 中新增了 `AgentThoughtValidation` 類別，使用 `class Config` 且 `extra = "allow"`，違反 R14；且該類別未在後續程式碼中引用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1838</code> MessageAgentThought 改為繼承 TypeBase 可能導致 id 欄位型別不一致</summary>

原本 `MessageAgentThought` 繼承自 `Base`，現在改為繼承 `TypeBase`。`TypeBase` 可能定義了不同的 `id` 型別或預設值，而此處明確指定了 `id: Mapped[str]` 並使用 `StringUUID`，但 `TypeBase` 可能已有 `id` 欄位定義，造成衝突或非預期行為。

失敗情境：若 `TypeBase` 的 `id` 欄位型別或預設值與此處不同，可能導致資料庫 schema 不一致或插入時發生錯誤。

建議：確認 `TypeBase` 的定義，確保 `id` 欄位相容；若 `TypeBase` 已定義 `id`，則不應重複定義。

**判斷依據**：diff 中將 `class MessageAgentThought(Base):` 改為 `class MessageAgentThought(TypeBase):`，但未提供 `TypeBase` 的定義，無法確認其對 `id` 欄位的影響。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/models/model.py:1846</code> id 欄位同時使用 insert_default 和 default_factory 可能造成混淆</summary>

`id` 欄位定義為 `mapped_column(StringUUID, insert_default=lambda: str(uuid4()), default_factory=lambda: str(uuid4()), init=False)`，同時指定了 `insert_default` 和 `default_factory`。在 SQLAlchemy 中，`default_factory` 用於 ORM 層級的預設值，而 `insert_default` 用於 Core 層級，兩者同時存在可能導致行為不一致或非預期結果。

建議：僅保留一個預設值來源，例如只使用 `default_factory` 或 `insert_default`，並確認其符合專案慣例。

**判斷依據**：diff 中新增的 `id` 欄位定義同時包含 `insert_default` 和 `default_factory`，可能造成混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:319</code> message_price_unit 和 answer_price_unit 的預設值不一致</summary>

在 `create_agent_thought` 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這與模型定義中的預設值（兩者皆為 `Decimal("0.001")`）不一致，可能導致資料不一致或非預期行為。

建議：確認哪個預設值是正確的，並統一使用。

**判斷依據**：diff 中 `message_price_unit` 設為 `Decimal("0.001")`，但 `answer_price_unit` 設為 `Decimal(0)`，而模型定義中兩者預設值皆為 `Decimal("0.001")`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8441 (cache hit 8320) ｜ completion tokens 1808 ｜ PR #11</sub>