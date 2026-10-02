<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 V2 UI 的建置與服務整合，包含 Dockerfile、GitHub Actions workflow、Python 設定與伺服器程式碼。主要風險在於 V2 UI 預設啟用（v2_enabled=True）可能導致未預期的行為變更，且缺少對應的測試與驗證。此外，Dockerfile 中安裝 Chromium 可能增加映像檔大小與攻擊面，但屬可接受。整體而言，需確認 V2 UI 的穩定性與相容性後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/prefect/settings/models/server/ui.py:22` | V2 UI 預設啟用可能導致未預期的行為變更 | 0.80 |
| ⚠️ | Major | `src/prefect/server/api/server.py:458` | V2 UI 啟用時，靜態路徑設定可能錯誤 | 0.70 |
| 🔸 | Minor | `src/prefect/server/api/server.py:532` | 日誌訊息未使用結構化日誌 | 0.60 |
| 🔸 | Minor | `Dockerfile:72` | 安裝 Chromium 可能增加映像檔大小與攻擊面 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/settings/models/server/ui.py:22</code> V2 UI 預設啟用可能導致未預期的行為變更</summary>

新增的 `v2_enabled` 設定預設為 `True`，這將使所有使用者預設使用實驗性的 V2 UI。若 V2 UI 尚未穩定或與現有功能不相容，可能造成使用者困擾或功能回歸。建議將預設值改為 `False`，待 V2 UI 穩定後再啟用。

**判斷依據**：diff 中新增的設定欄位，預設值為 True。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/prefect/server/api/server.py:458</code> V2 UI 啟用時，靜態路徑設定可能錯誤</summary>

在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`source_static_path` 設為 `prefect.__ui_v2_static_path__`，但 `static_subpath` 設為 `prefect.__ui_static_subpath__`（V1 的子路徑）。這可能導致 V2 UI 的靜態檔案被複製到 V1 的子路徑，造成路徑混淆或覆蓋。請確認 `static_subpath` 是否應為 V2 專用的子路徑。

**判斷依據**：diff 中 `static_subpath` 使用 `prefect.__ui_static_subpath__`，而非 V2 專用路徑。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/prefect/server/api/server.py:532</code> 日誌訊息未使用結構化日誌</summary>

新增的日誌訊息使用 `ui_logger.info("Serving experimental V2 UI")`，但未包含任何上下文（如版本、路徑）。建議使用結構化日誌或至少包含相關資訊，以便於除錯。

**判斷依據**：diff 中新增的日誌語句。

</details>

<details><summary>🔸 <b>Minor</b> — <code>Dockerfile:72</code> 安裝 Chromium 可能增加映像檔大小與攻擊面</summary>

在 V2 UI 建置階段安裝 Chromium 是為了 arm64 建置，但這會顯著增加映像檔大小，並引入不必要的相依性。建議評估是否可改用其他方式（如使用 Playwright 的 headless shell）或僅在需要時安裝。

**判斷依據**：diff 中新增的 apt-get install chromium。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5734 (cache hit 1408) ｜ completion tokens 982 ｜ PR #8</sub>