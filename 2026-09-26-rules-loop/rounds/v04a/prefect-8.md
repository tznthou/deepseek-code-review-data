<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並引入 `PREFECT_SERVER_UI_V2_ENABLED` 設定來切換 UI 版本。主要風險在於 `create_ui_app` 中變數作用域錯誤（`source_static_path` 未在函式內定義），可能導致 `NameError`；此外，`v2_enabled` 預設為 `True` 會使所有使用者預設使用實驗性 V2 UI，若 V2 UI 尚未就緒可能造成服務中斷。另有 GitHub Actions workflow 中 `npm ci` 未指定 Node 版本，可能因環境預設版本不符而失敗。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:465` | `source_static_path` 未在函式內定義，可能導致 NameError | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | `v2_enabled` 預設為 True 可能導致所有使用者預設使用實驗性 V2 UI | 0.80 |
| ⚠️ | Major | `.github/workflows/python-package.yaml:46` | `npm ci` 未指定 Node 版本，可能因環境預設版本不符而失敗 | 0.70 |
| 🔸 | Minor | `src/prefect/server/api/server.py:465` | `static_subpath` 變數在 if/else 中賦值但未使用 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:465</code> `source_static_path` 未在函式內定義，可能導致 NameError</summary>

在 `create_ui_app` 函式中，`source_static_path` 在 if/else 區塊內被賦值，但該變數未在函式開頭初始化。若 `v2_enabled` 為 False，則 `source_static_path` 會被賦值為 `prefect.__ui_static_path__`，但若 `v2_enabled` 為 True，則 `source_static_path` 會被賦值為 `prefect.__ui_v2_static_path__`。然而，在後續的 `create_ui_static_subpath` 函式中使用了 `source_static_path`，但該函式是獨立的，無法存取 `create_ui_app` 中的區域變數。這會導致 `NameError: name 'source_static_path' is not defined`。

建議將 `source_static_path` 的決定邏輯移到 `create_ui_static_subpath` 函式內，或將 `source_static_path` 作為參數傳遞。

**判斷依據**：diff 中新增的 if/else 區塊在 `create_ui_app` 內定義了 `source_static_path`，但後續的 `create_ui_static_subpath` 函式（未在 diff 中顯示，但根據上下文推測）使用了 `source_static_path`，而該變數不在其作用域內。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> `v2_enabled` 預設為 True 可能導致所有使用者預設使用實驗性 V2 UI</summary>

新增的 `v2_enabled` 設定預設值為 `True`，這表示所有使用者升級後將預設使用實驗性的 V2 UI。如果 V2 UI 尚未完全穩定或與現有功能不相容，可能導致使用者遇到問題。建議將預設值設為 `False`，並在 V2 UI 穩定後再考慮更改預設值。

**判斷依據**：diff 中新增的設定欄位 `v2_enabled` 預設為 `True`，且描述中標明為 experimental。

</details>

<details><summary>⚠️ <b>Major</b> — <code>.github/workflows/python-package.yaml:46</code> `npm ci` 未指定 Node 版本，可能因環境預設版本不符而失敗</summary>

在新增的 `Build UI v2` step 中，直接執行 `npm ci`，但未指定 Node.js 版本。V2 UI 需要 Node 22+（如 Dockerfile 中所示），而 GitHub Actions 的預設 Node 版本可能較低，導致建置失敗。建議在 workflow 中設定 Node 版本，例如使用 `actions/setup-node` 並指定版本。

**判斷依據**：diff 中新增的 step 未包含 Node 版本設定，而 Dockerfile 中明確指出 V2 UI 需要 Node 22+。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:465</code> `static_subpath` 變數在 if/else 中賦值但未使用</summary>

在 `create_ui_app` 中，`static_subpath` 被賦值為 `prefect.__ui_static_subpath__` 或 `prefect.__ui_v2_static_subpath__`，但後續程式碼並未使用該變數（而是使用 `static_dir`）。這可能是冗餘程式碼，建議移除或確認其用途。

**判斷依據**：diff 中 `static_subpath` 被賦值，但後續未見使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6471 (cache hit 4096) ｜ completion tokens 1484 ｜ PR #8</sub>