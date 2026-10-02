<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量服務檔案重新命名為 kebab-case，並同步更新所有 require/import 路徑。整體而言是低風險的機械式重構，但需特別注意：1) 檔案系統大小寫敏感（macOS 開發環境可能未察覺）可能導致 Linux 生產環境模組解析失敗；2) 部分 import 路徑更新可能遺漏（例如 EmailServiceWrapper.js 中的 DomainWarmingService 未改名）；3) 部分檔案在重新命名時混入了非預期的格式變更（如移除行尾分號、調整空白），增加 review 雜訊。建議合併前先以 CI 在 Linux 環境執行完整測試，並確認所有 import 路徑皆已更新。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/core/core/server/services/email-service/EmailServiceWrapper.js:25` | 可能遺漏的 import 路徑更新：DomainWarmingService | 0.90 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | 非預期的格式變更：移除行尾分號 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:12` | 不一致的 import 路徑格式 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/core/core/server/services/email-service/EmailServiceWrapper.js:25</code> 可能遺漏的 import 路徑更新：DomainWarmingService</summary>

此 PR 將多數服務檔案改為 kebab-case，但此處的 `require('./DomainWarmingService')` 未同步更新。若 `DomainWarmingService.js` 檔案已改名為 `domain-warming-service.js`，此 require 將在 Linux 環境中因大小寫敏感而失敗。請確認該檔案是否已改名，並更新此路徑。

**判斷依據**：diff 中此檔案僅更新了 MailgunClient 的 require，但未更新 DomainWarmingService，而其他服務檔案皆已改為 kebab-case。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> 非預期的格式變更：移除行尾分號</summary>

此檔案在重新命名 import 路徑的同時，移除了多行行尾分號（例如 `const {Router} = require('express')`）。這與 PR 主旨（檔案重新命名）無關，可能違反專案 ESLint 規則（若專案要求分號）。建議還原這些格式變更，以減少 review 雜訊並避免 CI lint 失敗。

**判斷依據**：diff 顯示原本有分號的行被移除分號，且此變更與檔案重新命名無關。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:12</code> 不一致的 import 路徑格式</summary>

部分 import 路徑已更新為 kebab-case，但部分仍保留 PascalCase（例如 `EventRepository`、`ProductRepository`）。若對應檔案已改名，這些 require 將失敗；若未改名，則不一致的命名風格可能造成混淆。請確認所有檔案皆已改名並更新所有路徑。

**判斷依據**：diff 中此處的 require 路徑已改為 kebab-case，但其他行（如 `MemberRepository`）仍為 PascalCase，顯示可能未完全更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 46697 (cache hit 46592) ｜ completion tokens 883 ｜ PR #7</sub>