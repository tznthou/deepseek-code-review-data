<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與服務支援，包含 Docker 建置階段、設定選項與伺服器路由切換。主要風險在於 `create_ui_app` 中 V2 啟用時仍使用 V1 的 `static_subpath`，可能導致檔案複製到錯誤位置；此外，V2 設定預設為啟用，若未正確建置可能造成服務失敗。建議先修正路徑指派問題，並確認 V2 建置流程的完整性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:462` | V2 啟用時仍使用 V1 的 static_subpath | 0.95 |
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | V2 UI 預設啟用可能導致未建置時服務失敗 | 0.80 |
| 🔸 | Minor | `Dockerfile:69` | V2 建置階段安裝 Chromium 可能大幅增加映像大小 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:462</code> V2 啟用時仍使用 V1 的 static_subpath</summary>

在 `v2_enabled` 為 True 時，`static_subpath` 仍被指派為 `prefect.__ui_static_subpath__`（V1 的路徑），而非 `prefect.__ui_v2_static_subpath__`。這會導致 `create_ui_static_subpath` 將 V2 的靜態檔案複製到 V1 的子目錄，可能覆蓋 V1 檔案或造成路徑衝突。

**失敗情境**：當使用者設定 `PREFECT_SERVER_UI_V2_ENABLED=true` 且未設定 `PREFECT_UI_STATIC_DIRECTORY` 時，伺服器會將 V2 檔案複製到 `server/ui_build`（V1 的動態目錄），而 V1 的靜態檔案可能仍存在，導致服務內容混亂或找不到正確資源。

**建議**：將 `static_subpath` 指派為 `prefect.__ui_v2_static_subpath__`。

**判斷依據**：diff 中 `static_subpath = prefect.__ui_static_subpath__` 位於 `if v2_enabled:` 區塊內，但未改用 V2 對應的 `__ui_v2_static_subpath__`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> V2 UI 預設啟用可能導致未建置時服務失敗</summary>

新增的 `v2_enabled` 設定預設為 `True`，但 V2 UI 的靜態檔案只有在執行建置步驟（如 Docker 建置或 CI 中的 `npm run build`）後才會存在。若使用者直接從原始碼安裝或未執行建置，伺服器啟動時會嘗試複製不存在的 `src/prefect/server/ui-v2` 目錄，導致 `FileNotFoundError` 或服務無法提供 UI。

**失敗情境**：開發者以 `pip install -e .` 安裝後直接執行 `prefect server start`，未先建置 V2 UI，此時 `source_static_path` 指向不存在的目錄，`copy_directory` 將拋出例外。

**建議**：將預設值改為 `False`，或加入檢查：若 V2 目錄不存在則自動回退至 V1，並記錄警告。

**判斷依據**：diff 中新增的 `v2_enabled` 欄位預設為 `True`，且未見對應的檔案存在性檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:69</code> V2 建置階段安裝 Chromium 可能大幅增加映像大小</summary>

在 `ui-v2-builder` 階段安裝 `chromium` 是為了 arm64 建置，但這會顯著增加建置時間與映像層大小。若僅為特定架構需要，可考慮使用多階段建置或條件安裝，以減少最終映像的體積。

**建議**：確認是否所有架構都需要 Chromium，或改用更輕量的相依套件。

**判斷依據**：diff 中新增的 `apt-get install chromium` 未區分架構，且未見後續清理或條件判斷。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 15491 (cache hit 1536) ｜ completion tokens 1139 ｜ PR #8</sub>