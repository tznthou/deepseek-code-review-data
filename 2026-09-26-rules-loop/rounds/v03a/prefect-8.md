<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並在 server 端加入切換 V1/V2 UI 的設定。主要風險在於 `create_ui_app` 中變數作用域錯誤（`source_static_path` 未定義即使用）、`v2_enabled` 預設為 True 可能造成未預期的行為變更，以及 workflow 中缺少 timeout 與 npm 快取。建議先修正變數作用域問題，並評估預設值是否應為 False。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:509` | `source_static_path` 在 `create_ui_static_subpath` 中未定義 | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | `v2_enabled` 預設為 True 可能造成未預期的行為變更 | 0.80 |
| 🔸 | Minor | `.github/workflows/python-package.yaml:46` | 缺少 `timeout-minutes` 可能導致 workflow 無限期執行 | 0.70 |
| 🔸 | Minor | `.github/workflows/python-package.yaml:46` | 未使用 npm 快取可能增加 CI 時間 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:509</code> `source_static_path` 在 `create_ui_static_subpath` 中未定義</summary>

在 `create_ui_static_subpath` 函式中，`copy_directory(str(source_static_path), str(static_dir))` 使用了 `source_static_path`，但該變數是在 `create_ui_app` 中定義的區域變數，並未傳入此函式。這會導致 `NameError`，使靜態檔案複製失敗。

**失敗情境**：當 `PREFECT_UI_STATIC_DIRECTORY` 設定為非空值且 `PREFECT_UI_ENABLED=True` 時，呼叫 `create_ui_static_subpath` 會拋出 `NameError`。

**建議修法**：將 `source_static_path` 作為參數傳入 `create_ui_static_subpath`，或在函式內重新計算。

**判斷依據**：diff 中 `create_ui_static_subpath` 函式內使用了 `source_static_path`，但該變數僅在 `create_ui_app` 中定義，且未作為參數傳遞。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> `v2_enabled` 預設為 True 可能造成未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這表示升級後所有使用者將預設使用實驗性的 V2 UI。若 V2 UI 尚未穩定或與現有功能不相容，可能導致使用者遇到問題。

**建議修法**：將預設值改為 `False`，並在文件或 release notes 中說明如何啟用。

**判斷依據**：diff 中新增的設定欄位 `v2_enabled` 預設值為 `True`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/workflows/python-package.yaml:46</code> 缺少 `timeout-minutes` 可能導致 workflow 無限期執行</summary>

新增的 `Build UI v2` step 沒有設定 `timeout-minutes`。若 `npm ci` 或 `npm run build` 因網路問題或相依性問題卡住，整個 workflow 可能會長時間執行，浪費資源。

**建議修法**：為該 step 或整個 job 設定合理的 `timeout-minutes`。

**判斷依據**：diff 中新增的 step 沒有 `timeout-minutes` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/workflows/python-package.yaml:46</code> 未使用 npm 快取可能增加 CI 時間</summary>

新增的 `Build UI v2` step 執行 `npm ci`，但沒有使用 `actions/setup-node` 或 `actions/cache` 來快取 npm 相依性。這可能導致每次執行都重新下載所有套件，增加 CI 時間。

**建議修法**：使用 `actions/setup-node` 並啟用快取，或使用 `actions/cache` 快取 `~/.npm`。

**判斷依據**：diff 中新增的 step 未使用任何快取機制。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7274 (cache hit 4096) ｜ completion tokens 1195 ｜ PR #8</sub>