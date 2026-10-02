<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 V2 UI 的建置與 Docker 整合，並在伺服器端加入切換 V1/V2 UI 的設定。主要風險在於 `create_ui_app` 函式中的變數作用域錯誤，可能導致 V1 UI 無法正常運作；此外，Dockerfile 中安裝 Chromium 的步驟可能大幅增加映像檔大小，且未驗證其必要性。建議優先修正變數作用域問題，並評估 Chromium 的必要性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `src/prefect/server/api/server.py:458` | 變數作用域錯誤導致 V1 UI 無法正常運作 | 0.95 |
| ⚠️ | Major | `Dockerfile:69` | 安裝 Chromium 可能大幅增加映像檔大小且未說明必要性 | 0.80 |
| 🔸 | Minor | `src/prefect/server/api/server.py:531` | 日誌記錄器未遵循標準初始化模式 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>src/prefect/server/api/server.py:458</code> 變數作用域錯誤導致 V1 UI 無法正常運作</summary>

在 `create_ui_app` 函式中，`source_static_path` 和 `static_subpath` 在 `if v2_enabled` 區塊內被賦值，但後續的 `create_ui_static_subpath` 函式（第 506 行）使用了 `source_static_path`，而該函式是在 `if` 區塊外呼叫的。若 `v2_enabled` 為 False，則 `source_static_path` 未定義，會拋出 `NameError`。

建議將變數初始化移到 `if` 區塊之前，或確保在所有路徑下都有賦值。

**判斷依據**：diff 中新增的程式碼片段顯示變數在條件分支內賦值，但後續使用點在分支外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>Dockerfile:69</code> 安裝 Chromium 可能大幅增加映像檔大小且未說明必要性</summary>

在 `ui-v2-builder` 階段安裝了 `chromium`，這可能導致最終映像檔體積顯著增加。若僅為了建置時執行測試或特定工具，應考慮使用多階段建置或僅在建置階段安裝，並在最終階段移除。請確認是否真的需要 Chromium，或是否有更輕量的替代方案。

**判斷依據**：diff 中新增的安裝步驟，且註解僅說明為 arm64 建置所需，未提供其他細節。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:531</code> 日誌記錄器未遵循標準初始化模式</summary>

在 `create_ui_app` 函式中，使用 `logging.getLogger("ui_server")` 直接取得 logger，違反了專案規範 R03（Logger 實例必須遵循標準初始化模式）。應使用 `get_logger("ui_server")` 並加上型別註解。

**判斷依據**：diff 中新增的程式碼行，且專案規範 R03 明確要求使用 `get_logger`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7264 (cache hit 7168) ｜ completion tokens 939 ｜ PR #8</sub>