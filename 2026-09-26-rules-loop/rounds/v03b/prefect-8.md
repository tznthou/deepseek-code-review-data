<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 V2 UI 的建置與 Docker 整合，並預設啟用 V2 UI。主要風險在於 `create_ui_app` 中 `static_subpath` 的指派邏輯可能造成路徑錯誤，以及 `v2_enabled` 預設為 `True` 可能導致未預期的行為變更。此外，Dockerfile 中安裝 Chromium 的步驟可能大幅增加映像檔大小，且未清理 apt 快取。建議先修正路徑指派邏輯，並確認預設值變更的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/server/api/server.py:462` | static_subpath 指派邏輯錯誤 | 0.90 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | v2_enabled 預設為 True 可能造成未預期的行為變更 | 0.80 |
| 🔸 | Minor | `Dockerfile:69` | 安裝 Chromium 可能大幅增加映像檔大小且未清理 apt 快取 | 0.70 |
| 🔸 | Minor | `src/prefect/server/api/server.py:531` | 日誌記錄器未遵循標準初始化模式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:462</code> static_subpath 指派邏輯錯誤</summary>

在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（即 `ui_v2_build`），但 `source_static_path` 是 `prefect.__ui_v2_static_path__`（即 `ui_v2`）。這會導致後續 `create_ui_static_subpath` 將 V2 靜態檔案複製到 `ui_v2_build` 目錄，但 `static_dir` 指向 `ui_v2_build`，而 `reference_file_matches_base_url` 檢查的檔案可能不存在，造成服務錯誤。建議將 `static_subpath` 改為 `prefect.__ui_v2_static_subpath__`（即 `ui_v2_build`），並確認 `__ui_v2_static_subpath__` 的定義是否正確。

**判斷依據**：diff 中第 462 行：`static_subpath = prefect.__ui_static_subpath__`，但 `source_static_path` 為 `prefect.__ui_v2_static_path__`，兩者不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> v2_enabled 預設為 True 可能造成未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這會讓所有現有使用者自動切換到實驗性的 V2 UI，可能導致未預期的行為變更或破壞性影響。建議將預設值改為 `False`，並在正式發布時再啟用。

**判斷依據**：diff 中新增的設定欄位，預設值為 True。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:69</code> 安裝 Chromium 可能大幅增加映像檔大小且未清理 apt 快取</summary>

在 `ui-v2-builder` 階段安裝 Chromium 是為了 arm64 建置，但 Chromium 及其相依套件可能使映像檔大小增加數百 MB。此外，`apt-get clean` 已執行，但未刪除 `/var/lib/apt/lists/*`，可能殘留不必要的檔案。建議評估是否可改用無頭 Chromium 或僅安裝必要元件，並在清理時一併刪除 lists。

**判斷依據**：diff 中新增的 RUN 指令。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:531</code> 日誌記錄器未遵循標準初始化模式</summary>

在 `create_ui_app` 中，使用 `logging.getLogger("ui_server")` 直接取得 logger，違反專案規範 R03（Logger 實例必須遵循標準初始化模式）。建議改用 `get_logger("ui_server")` 並加上型別註記。

**判斷依據**：diff 中新增的日誌記錄器初始化。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7274 (cache hit 7168) ｜ completion tokens 1131 ｜ PR #8</sub>