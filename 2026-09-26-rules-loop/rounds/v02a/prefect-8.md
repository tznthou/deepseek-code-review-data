<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與服務支援，包含 Dockerfile 多階段建置、GitHub Actions 工作流程、Python 設定與伺服器邏輯。主要風險在於 Python 程式碼中變數作用域錯誤（source_static_path 未定義）、日誌記錄器未遵循標準模式，以及設定預設值可能導致未預期的行為變更。建議先修正變數作用域問題，並確認日誌記錄器初始化方式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:509` | source_static_path 變數在 create_ui_static_subpath 中未定義 | 0.95 |
| ⚠️ | Major | `src/prefect/server/api/server.py:531` | [R03] 日誌記錄器未遵循標準初始化模式 | 0.90 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | v2_enabled 預設為 True 可能導致未預期的行為變更 | 0.85 |
| 🔸 | Minor | `Dockerfile:14` | npm ci 未指定 Node 版本 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:509</code> source_static_path 變數在 create_ui_static_subpath 中未定義</summary>

在 `create_ui_static_subpath` 函式中，`copy_directory(str(source_static_path), str(static_dir))` 使用了 `source_static_path` 變數，但該變數是在 `create_ui_app` 函式中定義的區域變數，並未傳遞或全域可用。這會導致 `NameError`，使得靜態檔案複製失敗。

**失敗情境**：當 `PREFECT_UI_ENABLED` 為 True 且非 ephemeral 模式時，呼叫 `create_ui_static_subpath` 會拋出 `NameError`，導致伺服器無法啟動。

**建議修法**：將 `source_static_path` 作為參數傳遞給 `create_ui_static_subpath`，或將其設為全域變數。

**判斷依據**：diff 中新增的 `source_static_path` 變數僅在 `create_ui_app` 函式內定義，但在 `create_ui_static_subpath` 函式中使用，且該函式未接收此參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:531</code> [R03] 日誌記錄器未遵循標準初始化模式</summary>

在 `create_ui_app` 函式中，使用 `logging.getLogger("ui_server")` 直接建立日誌記錄器，違反了專案規範 R03：應使用 `get_logger("module_name")` 模式，並加上型別註解。

**建議修法**：改用專案的 `get_logger` 函式，例如 `logger: "logging.Logger" = get_logger("ui_server")`。

**判斷依據**：diff 中新增的程式碼直接呼叫 `logging.getLogger`，未使用專案慣用的 `get_logger`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> v2_enabled 預設為 True 可能導致未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設值為 `True`，這表示升級後所有使用者將預設使用實驗性的 V2 UI，而非原本的 V1 UI。這可能造成使用者介面突然改變，且 V2 UI 可能尚未穩定。

**建議修法**：將預設值改為 `False`，讓使用者明確選擇啟用 V2 UI。

**判斷依據**：diff 中新增的設定欄位預設為 True，且描述中標明為 experimental。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:14</code> npm ci 未指定 Node 版本</summary>

在 GitHub Actions 工作流程中，`npm ci` 使用 runner 預設的 Node.js 版本，但 Dockerfile 中明確指定 V2 UI 需要 Node 22+。若 runner 的 Node 版本低於 22，可能導致建置失敗。

**建議修法**：在工作流程中設定 Node.js 版本，例如使用 `actions/setup-node` 並指定 `node-version: 22`。

**判斷依據**：diff 中新增的步驟未設定 Node 版本，而 Dockerfile 中指定了 `NODE_V2_VERSION=22.12.0`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7265 (cache hit 1536) ｜ completion tokens 1162 ｜ PR #8</sub>