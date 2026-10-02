<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 MessageAgentThought 模型從 Base 改為 TypeBase，並更新欄位型別與預設值，同時調整 agent runner 中的建立與歷史組織邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤的工具結果；此外，AgentThoughtValidation 模型未被使用且 extra 設定有誤，以及 Decimal 預設值與 server_default 不一致等問題。建議優先修正 tool_call_response 的資料來源錯誤。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | AgentThoughtValidation 模型未被使用且 extra 設定錯誤 | 0.80 |
| ⚠️ | Major | `api/models/model.py:1865` | Decimal 預設值與 server_default 不一致 | 0.75 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:319` | message_unit_price 與 answer_unit_price 的 Decimal 值可能不符預期 | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:365` | 字串串接方式改變可能影響效能與可讀性 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果，造成歷史訊息錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史記錄中的工具回應會顯示輸入參數而非輸出結果，影響後續模型理解上下文。

建議改回使用 `tool_responses`，並考慮是否需要 `str()` 轉換。

**判斷依據**：diff 中此行由 `content=tool_responses.get(tool, agent_thought.observation),` 改為 `content=str(tool_inputs.get(tool, agent_thought.observation)),`，明顯誤用變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> AgentThoughtValidation 模型未被使用且 extra 設定錯誤</summary>

新增的 AgentThoughtValidation 模型定義了 `extra = "allow"`，但註解指出應使用 `ConfigDict(extra='forbid')`。此外，此模型在 diff 中未見任何使用，可能為多餘程式碼。若未來用於驗證，應修正 extra 設定以嚴格拒絕未知欄位，避免意外接受未預期的資料。

**判斷依據**：diff 中新增此類別，但未在其他地方引用；且 extra 設定與註解矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1865</code> Decimal 預設值與 server_default 不一致</summary>

message_price_unit 和 answer_price_unit 欄位同時設定了 Python 端 default=Decimal("0.001") 和 server_default=sa.text("0.001")。若資料庫已有舊資料，server_default 僅在 insert 時未提供值時生效，而 Python 端 default 會在 ORM 層級填入。兩者可能造成不一致，特別是在直接使用 SQL 插入時。建議確認是否需要同時設定，或移除其中一個以避免混淆。

**判斷依據**：diff 中新增 default=Decimal("0.001")，同時保留 server_default=sa.text("0.001")。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:319</code> message_unit_price 與 answer_unit_price 的 Decimal 值可能不符預期</summary>

在 create_agent_thought 中，message_unit_price 設為 Decimal(0)，answer_unit_price 設為 Decimal("0.001")，而 message_price_unit 設為 Decimal("0.001")，answer_price_unit 設為 Decimal(0)。這些值可能與原本的整數 0 和預設 0.001 不同，需確認是否符合業務邏輯。

**判斷依據**：diff 中將原本的整數 0 改為 Decimal(0)，並將 message_price_unit 改為 Decimal("0.001")。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:365</code> 字串串接方式改變可能影響效能與可讀性</summary>

原本使用 `agent_thought.thought += thought`，修改後改為 `existing_thought = agent_thought.thought or ""` 再使用 f-string 串接。雖然功能相同，但若 thought 很長，f-string 會建立新字串，可能稍微增加記憶體使用。建議維持原寫法或使用 `+=` 以保持簡潔。

**判斷依據**：diff 中將 `agent_thought.thought += thought` 改為上述兩行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5807 (cache hit 1408) ｜ completion tokens 1391 ｜ PR #11</sub>