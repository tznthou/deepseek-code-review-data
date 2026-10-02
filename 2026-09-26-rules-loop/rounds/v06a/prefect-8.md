<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並加入設定開關以切換服務的 UI 版本。主要風險在於 `create_ui_app` 中 `source_static_path` 與 `static_subpath` 的指派邏輯可能相反，導致服務錯誤的靜態檔案；此外，V2 UI 預設啟用可能造成未預期的行為變更。建議先修正路徑指派邏輯，並考慮將預設值改為 False。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:463` | V2 啟用時靜態路徑指派相反 | 0.95 |
| ⚠️ | Major | `src/prefect/server/api/server.py:467` | V1 啟用時靜態路徑指派相反 | 0.85 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | V2 UI 預設啟用可能造成未預期的行為變更 | 0.80 |
| 🔸 | Minor | `src/prefect/__init__.py:69` | 新增的 V2 靜態路徑變數命名不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:463</code> V2 啟用時靜態路徑指派相反</summary>

在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`source_static_path` 被設為 `prefect.__ui_v2_static_path__`，但 `static_subpath` 被設為 `prefect.__ui_static_subpath__`（V1 的子路徑）。這會導致後續 `create_ui_static_subpath` 將 V2 的靜態檔案複製到 V1 的子路徑，而服務時卻從 V1 的子路徑讀取，造成路徑不一致。應將 `static_subpath` 改為 `prefect.__ui_v2_static_subpath__`。

**判斷依據**：diff 中新增的指派邏輯：當 v2_enabled 為 True 時，source_static_path 使用 V2 路徑，但 static_subpath 使用 V1 路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:467</code> V1 啟用時靜態路徑指派相反</summary>

當 `v2_enabled` 為 False 時，`source_static_path` 被設為 `prefect.__ui_static_path__`，但 `static_subpath` 被設為 `prefect.__ui_v2_static_subpath__`。這會導致 V1 的靜態檔案被複製到 V2 的子路徑，而服務時卻從 V2 的子路徑讀取，造成路徑不一致。應將 `static_subpath` 改為 `prefect.__ui_static_subpath__`。

**判斷依據**：diff 中新增的指派邏輯：當 v2_enabled 為 False 時，source_static_path 使用 V1 路徑，但 static_subpath 使用 V2 路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> V2 UI 預設啟用可能造成未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 True，這會讓所有使用預設設定的使用者自動切換到實驗性的 V2 UI。若 V2 UI 尚未穩定或與現有功能不相容，可能導致使用者遇到問題。建議將預設值改為 False，並在文件或發布說明中明確標示為實驗性功能。

**判斷依據**：diff 中新增的設定欄位，預設值為 True。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/__init__.py:69</code> 新增的 V2 靜態路徑變數命名不一致</summary>

新增的 `__ui_v2_static_subpath__` 和 `__ui_v2_static_path__` 使用 `ui_v2` 命名，但 Dockerfile 和 pyproject.toml 中使用的目錄名稱為 `ui-v2`（連字號）。這可能導致混淆，建議統一命名風格（例如使用底線或連字號）。

**判斷依據**：diff 中新增的變數名稱使用底線，而其他檔案使用連字號。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7254 (cache hit 4096) ｜ completion tokens 1217 ｜ PR #8</sub>