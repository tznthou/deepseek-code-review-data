<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將 MessageAgentThought 模型從 Base 改為 TypeBase，並調整欄位型別與預設值，同時在 BaseAgentRunner 中改用 Decimal 與 CreatorUserRole。整體方向合理，但存在兩個高風險問題：organize_agent_history 中 ToolPromptMessage 的 content 誤用 tool_inputs 而非 tool_responses，可能導致歷史訊息內容錯誤；以及 AgentThoughtValidation 使用 Pydantic v1 的 Config 語法，若專案已升級至 Pydantic v2 將失效。建議先修正這兩個問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `api/core/agent/base_agent_runner.py:502` | ToolPromptMessage content 誤用 tool_inputs 而非 tool_responses | 0.95 |
| ⚠️ | Major | `api/core/agent/base_agent_runner.py:64` | AgentThoughtValidation 使用 Pydantic v1 語法，可能與專案 Pydantic 版本不相容 | 0.80 |
| ⚠️ | Major | `api/models/model.py:1853` | message_chain_id 欄位型別標註為 Mapped[str \| None] 但未設定 default=None | 0.70 |
| 🔸 | Minor | `api/core/agent/base_agent_runner.py:502` | ToolPromptMessage content 被強制轉為 str，可能改變原有型別 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>api/core/agent/base_agent_runner.py:502</code> ToolPromptMessage content 誤用 tool_inputs 而非 tool_responses</summary>

在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容被替換成工具輸入，造成歷史訊息中的工具輸出錯誤。例如當 tool_inputs 為 `{"tool1": {"input": "data"}}` 且 tool_responses 為 `{"tool1": {"output": "result"}}` 時，原本應回傳 "result"，現在會回傳 "{'input': 'data'}"。

**判斷依據**：diff 中此行取代了原本的 `content=tool_responses.get(tool, agent_thought.observation)`，且前文已正確解析 tool_responses，此處應使用 tool_responses 而非 tool_inputs。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/core/agent/base_agent_runner.py:64</code> AgentThoughtValidation 使用 Pydantic v1 語法，可能與專案 Pydantic 版本不相容</summary>

新增的 AgentThoughtValidation 類別使用 `class Config: extra = "allow"`，這是 Pydantic v1 的寫法。若專案已升級至 Pydantic v2，此設定將被忽略，可能導致驗證行為不符預期（例如未預期的欄位被允許）。建議確認專案使用的 Pydantic 版本，若為 v2 應改用 `model_config = ConfigDict(extra='allow')`。

**判斷依據**：diff 中新增此類別，且註解本身也指出應使用 ConfigDict，顯示作者可能已知版本問題但未修正。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/models/model.py:1853</code> message_chain_id 欄位型別標註為 Mapped[str | None] 但未設定 default=None</summary>

在 MessageAgentThought 中，`message_chain_id` 的型別標註為 `Mapped[str | None]`，但 mapped_column 中僅有 `nullable=True`，未設定 `default=None`。這可能導致在建立實例時若未提供此欄位，SQLAlchemy 會嘗試插入 NULL，但型別標註暗示可為 None，可能造成型別檢查或執行期錯誤。建議加上 `default=None` 以明確表示可選。

**判斷依據**：diff 中此行新增，且其他可選欄位（如 thought、tool）均有 `default=None`，此處遺漏。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/core/agent/base_agent_runner.py:502</code> ToolPromptMessage content 被強制轉為 str，可能改變原有型別</summary>

原本 `tool_responses.get(tool, agent_thought.observation)` 可能回傳 dict 或其他型別，但修改後使用 `str()` 強制轉為字串。這可能導致下游處理時型別不符，或遺失結構化資料。若 tool_responses 原本就是字串則無影響，但若為 dict 則會變成字串表示。建議確認 ToolPromptMessage 的 content 欄位型別，若允許 dict 則不應強制轉換。

**判斷依據**：diff 中新增 str() 轉換，且原本程式碼未做此轉換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10327 (cache hit 10240) ｜ completion tokens 1201 ｜ PR #11</sub>