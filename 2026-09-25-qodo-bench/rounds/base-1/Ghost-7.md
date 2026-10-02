<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量服務檔案重新命名為 kebab-case，並同步更新所有 require/import 路徑。整體風險低，但需注意：1) 檔案系統大小寫敏感可能導致部署問題；2) 部分檔案在重新命名時混入了非預期的格式變更（如移除分號、調整空白），可能違反專案慣例；3) 需確認所有引用都已更新，避免漏網之魚。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:1` | 重新命名檔案時混入非預期的格式變更 | 0.80 |
| 🔸 | Minor | `ghost/core/core/server/services/members/members-api/members-api.js:6` | require 路徑大小寫變更可能導致部署問題 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/stats/posts-stats-service.js:151` | 重新命名檔案時混入非預期的空白變更 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/stats/posts-stats-service.js:1571` | 檔案結尾缺少換行符 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/outbox/index.js:43` | 檔案結尾缺少換行符 | 0.70 |
| 🔸 | Minor | `ghost/core/core/server/services/outbox/jobs/outbox-job.js:33` | 檔案結尾缺少換行符 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/outbox/index.test.js:49` | 檔案結尾缺少換行符 | 0.70 |
| 🔸 | Minor | `ghost/core/test/unit/server/services/stats/mrr.test.js:362` | 檔案結尾缺少換行符 | 0.70 |

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:1</code> 重新命名檔案時混入非預期的格式變更</summary>

此檔案除了更新 require 路徑外，還移除了所有行尾分號，並將部分 require 陳述式的引號從單引號改為雙引號。這與專案中其他檔案的風格不一致，且可能違反 ESLint 規則。建議只保留必要的路徑變更，避免混入格式調整。

**判斷依據**：diff 顯示原本有分號的程式碼被移除分號，且引號風格改變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/members/members-api/members-api.js:6</code> require 路徑大小寫變更可能導致部署問題</summary>

檔案從 `MembersAPI.js` 重新命名為 `members-api.js`，但此處的 require 路徑也改為小寫。在大小寫敏感的檔案系統（如 Linux）上，如果部署時未正確處理檔案名稱大小寫，可能導致模組找不到。建議確認 CI/CD 流程能正確處理大小寫變更。

**判斷依據**：diff 顯示多個 require 路徑從 PascalCase 改為 kebab-case。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/stats/posts-stats-service.js:151</code> 重新命名檔案時混入非預期的空白變更</summary>

此檔案除了更新 require 路徑外，還移除了多處行尾空白，並調整了部分程式碼的縮排。這可能導致不必要的 diff 雜訊，建議只保留必要的路徑變更。

**判斷依據**：diff 顯示多處行尾空白被移除，且縮排有調整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/stats/posts-stats-service.js:1571</code> 檔案結尾缺少換行符</summary>

檔案結尾原本沒有換行符，此 PR 加入了換行符。這通常是好的，但需確認是否符合專案的風格指南。

**判斷依據**：diff 顯示檔案結尾從沒有換行符改為有換行符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/outbox/index.js:43</code> 檔案結尾缺少換行符</summary>

檔案結尾原本沒有換行符，此 PR 加入了換行符。這通常是好的，但需確認是否符合專案的風格指南。

**判斷依據**：diff 顯示檔案結尾從沒有換行符改為有換行符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/core/server/services/outbox/jobs/outbox-job.js:33</code> 檔案結尾缺少換行符</summary>

檔案結尾原本沒有換行符，此 PR 加入了換行符。這通常是好的，但需確認是否符合專案的風格指南。

**判斷依據**：diff 顯示檔案結尾從沒有換行符改為有換行符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/outbox/index.test.js:49</code> 檔案結尾缺少換行符</summary>

檔案結尾原本沒有換行符，此 PR 加入了換行符。這通常是好的，但需確認是否符合專案的風格指南。

**判斷依據**：diff 顯示檔案結尾從沒有換行符改為有換行符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/core/test/unit/server/services/stats/mrr.test.js:362</code> 檔案結尾缺少換行符</summary>

檔案結尾原本沒有換行符，此 PR 加入了換行符。這通常是好的，但需確認是否符合專案的風格指南。

**判斷依據**：diff 顯示檔案結尾從沒有換行符改為有換行符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 46733 (cache hit 1536) ｜ completion tokens 1512 ｜ PR #7</sub>