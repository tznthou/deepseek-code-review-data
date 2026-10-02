<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並加入伺服器端切換設定。主要風險在於 `create_ui_app` 中變數作用域錯誤（`source_static_path` 未定義即使用），以及 `v2_enabled` 預設為 `True` 可能導致未預期的行為變更。另有 GitHub Actions 中缺少 `timeout-minutes` 與未 pin SHA 的第三方 action 等可靠性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:509` | `source_static_path` 在 `create_ui_static_subpath` 中未定義 | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | `v2_enabled` 預設為 `True` 可能造成非預期的行為變更 | 0.80 |
| 🔸 | Minor | `.github/workflows/python-package.yaml:46` | 缺少 `timeout-minutes` | 0.70 |
| 🔸 | Minor | `Dockerfile:65` | 未 pin 第三方 action 到完整 commit SHA | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:509</code> `source_static_path` 在 `create_ui_static_subpath` 中未定義</summary>

在 `create_ui_static_subpath` 函式中，`copy_directory(str(source_static_path), str(static_dir))` 使用了 `source_static_path`，但該變數是在 `create_ui_app` 中定義的區域變數，並未傳入此函式。當 `v2_enabled` 為 `True` 且 `PREFECT_UI_STATIC_DIRECTORY` 未設定時，會拋出 `NameError`，導致伺服器無法啟動。

建議將 `source_static_path` 作為參數傳入 `create_ui_static_subpath`，或改為從設定中重新取得。

**判斷依據**：diff 中新增的 `source_static_path` 變數僅在 `create_ui_app` 內定義，但 `create_ui_static_subpath` 函式內直接使用，且該函式簽名未變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> `v2_enabled` 預設為 `True` 可能造成非預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這表示所有現有使用者在升級後將預設使用實驗性的 V2 UI，而非原本的 V1 UI。若 V2 UI 尚未穩定，可能導致使用者遇到未預期的問題。建議將預設值改為 `False`，並在正式發布時再切換。

**判斷依據**：diff 中新增的設定欄位預設值為 `True`，且描述中標明為 experimental。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/workflows/python-package.yaml:46</code> 缺少 `timeout-minutes`</summary>

新增的 `Build UI v2` step 沒有設定 `timeout-minutes`，若建置過程卡住可能導致 workflow 長時間執行。建議為每個 job 或 step 設定合理的 timeout。

**判斷依據**：diff 中新增的 step 未包含 timeout-minutes 設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:65</code> 未 pin 第三方 action 到完整 commit SHA</summary>

在 Dockerfile 中使用了 `node:${NODE_V2_VERSION}-bullseye-slim` 作為基礎映像，但未固定到特定 digest。這可能導致建置時使用到不同的映像版本，影響可重現性。建議使用 digest 或至少固定 minor 版本。

**判斷依據**：diff 中新增的 FROM 指令使用 tag 而非 digest。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7254 (cache hit 7168) ｜ completion tokens 1048 ｜ PR #8</sub>