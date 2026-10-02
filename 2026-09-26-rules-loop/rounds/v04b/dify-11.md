<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要重構 MessageAgentThought 模型的 SQLAlchemy 型別標註，並調整 agent thought 的建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 來源從 observation 改為 tool_input，可能造成語意錯誤；此外 Pydantic 模型使用 v1 語法但專案規範要求 v2，且新增的 AgentThoughtValidation 未被使用。整體需修正上述問題後再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | tool_call_response 的 content 誤用 tool_input 而非 observation | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | [R14] Pydantic 模型使用 v1 語法，違反專案 Pydantic v2 規範 | 0.90 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:52` | 新增的 AgentThoughtValidation 模型未被使用 | 0.85 |
| ⚠️ | Major | `api/models/model.py:1838` | MessageAgentThought 改為繼承 TypeBase 可能影響既有行為 | 0.80 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:320` | message_price_unit 與 answer_price_unit 的預設值不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> tool_call_response 的 content 誤用 tool_input 而非 observation</summary>

在 organize_agent_history 中，原本 tool_call_response 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果，造成對話歷史中的工具回應錯誤。

**失敗情境**：當 agent 呼叫工具並獲得 observation 時，歷史訊息中的 ToolPromptMessage 會顯示輸入而非輸出，導致後續模型理解錯誤。

**建議**：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別為字串。

**判斷依據**：diff 中此行將原本的 `tool_responses` 改為 `tool_inputs`，且 fallback 仍使用 `agent_thought.observation`，顯示邏輯不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> [R14] Pydantic 模型使用 v1 語法，違反專案 Pydantic v2 規範</summary>

新增的 `AgentThoughtValidation` 類別使用 `class Config: extra = "allow"`，這是 Pydantic v1 的寫法。專案規範 R14 要求使用 Pydantic v2，應改用 `model_config = ConfigDict(extra='allow')`。

**失敗情境**：若專案已全面升級至 Pydantic v2，此寫法可能導致驗證行為不一致或錯誤。

**建議**：改用 Pydantic v2 的 `model_config` 屬性。

**判斷依據**：diff 中新增的類別明確使用 v1 語法，且註解也指出應使用 ConfigDict。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:52</code> 新增的 AgentThoughtValidation 模型未被使用</summary>

此 PR 新增了 `AgentThoughtValidation` Pydantic 模型，但在 diff 中未見任何地方使用它。這可能是未完成的重構或遺留程式碼。

**失敗情境**：若此模型原本打算用於驗證 agent thought 資料，未使用會導致驗證缺失，可能讓無效資料進入資料庫。

**建議**：若不需要，請移除；若需要，請在建立或更新 agent thought 時使用。

**判斷依據**：diff 中僅定義此類別，未見任何實例化或引用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1838</code> MessageAgentThought 改為繼承 TypeBase 可能影響既有行為</summary>

原本 `MessageAgentThought` 繼承 `Base`，現在改為繼承 `TypeBase`。需確認 `TypeBase` 是否提供與 `Base` 相同的功能，例如 `id` 欄位的自動生成、session 管理等。若 `TypeBase` 有額外行為（如自動時間戳），可能影響資料寫入。

**失敗情境**：若 `TypeBase` 未正確設定 `id` 的預設值，可能導致插入時缺少主鍵。

**建議**：確認 `TypeBase` 的定義，並確保所有必要欄位行為一致。

**判斷依據**：diff 中類別繼承從 `Base` 改為 `TypeBase`，但未見 `TypeBase` 的定義，無法確認其行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:320</code> message_price_unit 與 answer_price_unit 的預設值不一致</summary>

在 `create_agent_thought` 中，`message_price_unit` 設為 `Decimal("0.001")`，而 `answer_price_unit` 設為 `Decimal(0)`。這與模型定義中的預設值（兩者皆為 0.001）不一致，可能導致資料不一致。

**失敗情境**：若後續計算依賴這些欄位，可能出現價格計算錯誤。

**建議**：確認哪個值正確，並統一設定。

**判斷依據**：diff 中顯示兩者設定不同，且與模型預設值不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7082 (cache hit 7040) ｜ completion tokens 1474 ｜ PR #11</sub>