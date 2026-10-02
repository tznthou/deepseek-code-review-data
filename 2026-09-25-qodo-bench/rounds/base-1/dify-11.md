<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 MessageAgentThought 模型從 Base 改為 TypeBase，並加入 SQLAlchemy 2.0 型別註記與預設值，同時調整 AgentThought 建立與歷史整理邏輯。主要風險在於 organize_agent_history 中 tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses，可能導致回傳錯誤內容；此外 Decimal 預設值與 server_default 不一致、Pydantic 模型使用舊版 Config 語法、以及移除測試中的 id 欄位可能影響測試隔離性。建議優先修正 content 來源錯誤，並確認 Decimal 預設值與資料庫 schema 的一致性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/models/model.py:1865` | Decimal 預設值與 server_default 不一致 | 0.80 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:64` | Pydantic 模型使用舊版 Config 語法 | 0.70 |
| 🔸 | Minor | `api/tests/test_containers_integration_tests/services/test_agent_service.py:232` | 移除測試中的 id 欄位可能影響測試隔離性 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

**判斷依據**：diff 中此行由原本的 `content=tool_responses.get(tool, agent_thought.observation)` 改為 `content=str(tool_inputs.get(tool, agent_thought.observation))`，且前後文顯示 tool_responses 已正確解析，但未使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1865</code> Decimal 預設值與 server_default 不一致</summary>

message_price_unit 與 answer_price_unit 的 Python 端預設值設為 Decimal("0.001")，但 server_default 仍為 sa.text("0.001")。若資料庫中已有舊資料，或某些插入路徑未提供此欄位，可能導致 Python 端與資料庫端預設值不一致。此外，message_unit_price 與 answer_unit_price 的預設值設為 None，但原本可能預期為 0，需確認是否會影響既有邏輯。

建議確認資料庫 schema 是否已更新，並統一 Python 端與 server_default 的預設值。

**判斷依據**：diff 中新增了 default=Decimal("0.001")，但 server_default 仍為 sa.text("0.001")，兩者可能不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:64</code> Pydantic 模型使用舊版 Config 語法</summary>

AgentThoughtValidation 使用 class Config 設定 extra = "allow"，但若專案已升級至 Pydantic v2，應改用 model_config = ConfigDict(extra='allow')。目前註解也提到此點，但未修正。

建議確認 Pydantic 版本，若為 v2 則改用新語法。

**判斷依據**：diff 中新增此模型，且註解明確指出應使用 ConfigDict。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/test_containers_integration_tests/services/test_agent_service.py:232</code> 移除測試中的 id 欄位可能影響測試隔離性</summary>

多處測試建立 MessageAgentThought 時移除了 id=fake.uuid4()，改由模型自動產生。若測試依賴特定 id 進行後續操作，可能導致測試失敗或資料混淆。

建議確認測試是否依賴 id，或改為在建立後取得自動生成的 id。

**判斷依據**：diff 中多處移除 id=fake.uuid4()，且未見後續取得 id 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5843 (cache hit 1536) ｜ completion tokens 1217 ｜ PR #11</sub>