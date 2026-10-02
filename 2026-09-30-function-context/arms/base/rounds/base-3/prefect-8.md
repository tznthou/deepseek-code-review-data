<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並引入 `PREFECT_SERVER_UI_V2_ENABLED` 設定來切換 UI 版本。主要風險在於 `create_ui_app` 中變數作用域錯誤：`source_static_path` 與 `static_subpath` 在 `if` 區塊內賦值，但後續使用時可能未定義，導致 `NameError`。此外，V2 UI 預設啟用，若建置未正確打包將造成服務啟動失敗。建議先修正變數作用域問題，並確認 V2 UI 建置流程的穩定性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:458` | 變數作用域錯誤：`source_static_path` 與 `static_subpath` 可能未定義 | 0.95 |
| ⚠️ | Major | `src/prefect/server/api/server.py:472` | `static_subpath` 可能未定義導致 `NameError` | 0.80 |
| ⚠️ | Major | `src/prefect/server/api/server.py:509` | `source_static_path` 可能未定義導致 `NameError` | 0.80 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | V2 UI 預設啟用可能導致未預期的行為變更 | 0.70 |
| 🔸 | Minor | `.github/workflows/python-package.yaml:46` | Workflow 中未設定 `timeout-minutes` | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:458</code> 變數作用域錯誤：`source_static_path` 與 `static_subpath` 可能未定義</summary>

在 `create_ui_app` 函式中，`source_static_path` 和 `static_subpath` 是在 `if v2_enabled:` 和 `else:` 區塊內分別賦值。然而，後續程式碼（如 `static_dir = ... or str(static_subpath)` 和 `copy_directory(str(source_static_path), ...)`）在區塊外使用這兩個變數。若 `v2_enabled` 為真，則 `static_subpath` 未定義；若為假，則 `source_static_path` 未定義，導致 `NameError`。

**失敗情境**：當伺服器啟動且 `v2_enabled` 為真時，執行到 `static_dir = ... or str(static_subpath)` 會拋出 `NameError: name 'static_subpath' is not defined`。

**建議修法**：在 `if` 區塊之前先定義這兩個變數的預設值，或將後續使用邏輯移入對應的條件分支中。

**判斷依據**：diff 中新增的程式碼顯示 `source_static_path` 和 `static_subpath` 僅在條件分支內賦值，但後續第 470 行左右使用 `static_subpath`，第 506 行左右使用 `source_static_path`，均可能未定義。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:472</code> `static_subpath` 可能未定義導致 `NameError`</summary>

`static_subpath` 在 `if v2_enabled` 為真時未被賦值，但此處直接使用 `str(static_subpath)`。若 `v2_enabled` 為真，將拋出 `NameError`。

**失敗情境**：啟用 V2 UI 時，伺服器啟動即失敗。

**建議修法**：在條件判斷前先定義 `static_subpath` 的預設值，或將此邏輯移入對應分支。

**判斷依據**：diff 中顯示 `static_subpath` 僅在 `else` 分支賦值，但此處在分支外使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:509</code> `source_static_path` 可能未定義導致 `NameError`</summary>

`source_static_path` 在 `if v2_enabled` 為假時未被賦值，但此處直接使用 `str(source_static_path)`。若 `v2_enabled` 為假，將拋出 `NameError`。

**失敗情境**：使用 V1 UI 時，伺服器啟動即失敗。

**建議修法**：在條件判斷前先定義 `source_static_path` 的預設值，或將此邏輯移入對應分支。

**判斷依據**：diff 中顯示 `source_static_path` 僅在 `if` 分支賦值，但此處在分支外使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> V2 UI 預設啟用可能導致未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這表示所有現有使用者升級後將預設使用實驗性的 V2 UI。若 V2 UI 尚未完全穩定或與現有功能不相容，可能造成使用者困擾。

**建議修法**：考慮將預設值設為 `False`，或提供明確的遷移指引。

**判斷依據**：diff 中顯示 `default=True`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/workflows/python-package.yaml:46</code> Workflow 中未設定 `timeout-minutes`</summary>

新增的 `Build UI v2` step 未設定 `timeout-minutes`，若建置過程卡住可能導致 workflow 長時間執行。

**建議修法**：為 job 或 step 設定合理的 timeout。

**判斷依據**：diff 中新增的 step 沒有 timeout 設定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5770 (cache hit 5760) ｜ completion tokens 1654 ｜ PR #8</sub>