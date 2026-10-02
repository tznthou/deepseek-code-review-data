<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並加入 `v2_enabled` 設定來切換 UI 版本。主要風險在於 `create_ui_app` 中 `source_static_path` 與 `static_subpath` 變數的作用域：它們在 `if` 區塊內賦值，但後續使用時可能未定義，導致 `NameError`。此外，`v2_enabled` 預設為 `True`，若 V2 UI 尚未準備好，可能造成使用者預設看到實驗性 UI。建議修正變數作用域並考慮將預設值改為 `False`。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:462` | 變數作用域錯誤：`source_static_path` 與 `static_subpath` 可能未定義 | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | `v2_enabled` 預設為 `True` 可能導致使用者預設使用實驗性 UI | 0.80 |
| 🔸 | Minor | `src/prefect/server/api/server.py:531` | 日誌記錄器未遵循標準初始化模式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:462</code> 變數作用域錯誤：`source_static_path` 與 `static_subpath` 可能未定義</summary>

在 `create_ui_app` 函式中，`source_static_path` 和 `static_subpath` 在 `if v2_enabled:` 區塊內賦值，但後續程式碼（如 `static_dir = ...` 和 `copy_directory(str(source_static_path), ...)`）在區塊外使用這些變數。如果 `v2_enabled` 為 `False`，則 `source_static_path` 和 `static_subpath` 不會被賦值，導致 `NameError`。

建議在 `if` 區塊之前先定義預設值，或將後續使用邏輯移入對應的 `if`/`else` 分支中。

**判斷依據**：diff 中新增的程式碼在 `if` 區塊內賦值，但後續 `static_dir = prefect.settings.PREFECT_UI_STATIC_DIRECTORY.value() or str(static_subpath)` 和 `copy_directory(str(source_static_path), str(static_dir))` 在區塊外使用這些變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> `v2_enabled` 預設為 `True` 可能導致使用者預設使用實驗性 UI</summary>

新增的 `v2_enabled` 設定預設值為 `True`，這表示所有使用者預設會使用實驗性的 V2 UI。如果 V2 UI 尚未穩定或存在未修復的問題，這可能導致使用者體驗下降或功能異常。建議將預設值改為 `False`，並在 V2 UI 穩定後再考慮變更預設值。

**判斷依據**：diff 中新增的設定欄位 `v2_enabled` 預設為 `True`，且描述中明確指出是 experimental。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:531</code> 日誌記錄器未遵循標準初始化模式</summary>

在 `create_ui_app` 中，使用 `logging.getLogger("ui_server")` 直接建立 logger，違反了專案規範 [R03]（Logger Instances Must Follow Standard Initialization Pattern）。應使用 `get_logger("ui_server")` 並加上型別註解。

**判斷依據**：diff 中新增的程式碼直接呼叫 `logging.getLogger`，而專案規範要求使用 `get_logger` 並遵循標準模式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7264 (cache hit 1536) ｜ completion tokens 1062 ｜ PR #8</sub>