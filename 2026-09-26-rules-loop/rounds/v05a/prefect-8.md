<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並在伺服器端加入切換 V1/V2 的設定。主要風險在於 `create_ui_app` 中 `source_static_path` 與 `static_subpath` 的指派邏輯可能顛倒，導致 V2 啟用時仍複製 V1 靜態檔；此外，`v2_enabled` 預設為 True 會讓所有使用者預設使用實驗性 UI，可能造成非預期的行為變更。建議優先修正路徑指派邏輯，並考慮將預設值改為 False。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:463` | V2 啟用時靜態路徑指派錯誤 | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | 實驗性 V2 UI 預設啟用 | 0.80 |
| 🔸 | Minor | `src/prefect/server/api/server.py:531` | Logger 實例化方式不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:463</code> V2 啟用時靜態路徑指派錯誤</summary>

在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`source_static_path` 被設為 `prefect.__ui_v2_static_path__`，但 `static_subpath` 卻被設為 `prefect.__ui_static_subpath__`（V1 的子路徑）。這會導致後續 `create_ui_static_subpath` 將 V2 的靜態檔複製到 V1 的子路徑，而 V1 的靜態檔可能覆蓋或混淆。應將 `static_subpath` 設為 `prefect.__ui_v2_static_subpath__`。

**判斷依據**：diff 中第 462-463 行顯示指派邏輯，與 `__ui_v2_static_subpath__` 的定義（`src/prefect/__init__.py` 第 70 行）不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> 實驗性 V2 UI 預設啟用</summary>

`v2_enabled` 預設為 True，這會讓所有使用者在未明確設定的情況下使用實驗性 V2 UI。若 V2 UI 尚未穩定，可能導致使用者遇到未預期的錯誤或行為變更。建議將預設值改為 False，並在文件或 release notes 中說明如何啟用。

**判斷依據**：diff 中新增的設定欄位，預設值為 True。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:531</code> Logger 實例化方式不一致</summary>

在 `create_ui_app` 中，使用 `logging.getLogger("ui_server")` 直接取得 logger，而專案規範 [R03] 要求使用 `get_logger("module_name")` 模式。這可能導致 logging 配置不一致。建議改用 `get_logger("ui_server")`。

**判斷依據**：diff 中新增的 logger 實例化，違反 [R03]。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7219 (cache hit 4096) ｜ completion tokens 849 ｜ PR #8</sub>