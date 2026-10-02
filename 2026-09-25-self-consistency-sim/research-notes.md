# 競品技術調查：效度與信度（2026-09-25）

> 四路平行調查（信度／上下文擴充／LLM judge 以外的過濾／量測），加上同目錄的 $0 模擬。
> 標記：✅ = 主 session 親自對過原文或原始資料；（agent）= 只經 agent 轉述，引用前要再核對。
> 原始下載（論文 txt、clone）在 session scratchpad，session 結束會消失；要重看就用下面的 URL 重抓。

## 兩個前提更正（最重要）

### 1. 「只看 diff ⇒ 理論上限 47.4%」不成立 ✅

- AACR 論文（arXiv 2601.19494）Table 1 的 754／518／233 只算**正確的** 1,505 則（50.1／34.4／15.5%）；
  我們的 47.4／34.7／17.9% 是把 2,145 則全部算進去（含 640 則錯的）
- **Table 4：No context（一次只看一個 hunk + PR title）的 recall，DeepSeek-V3.2 是 Diff 39.26／File 32.43／Repo 36.91%**；
  GPT-5.2 是 50.66／43.82／42.92%。context 標籤是「標註者寫這則需要多少上下文」，不是偵測的硬上限
- Table 3：DeepSeek-V3.2 在 **agent 模式（Claude Code）F1 6.67，低於 No context 的 9.71**
  （agent 每個 patch 平均 0.15 則、recall 4.78%、precision 11.00%；No context 2.29 則、36.54%、5.60%）
- 命中判定：行號範圍重疊 + Qwen3-235B 判斷「核心意圖與技術實質相同」。⚠️ Table 3/4 用的是 Line Correct 還是
  Semantically Correct，論文沒寫明
- precision 普遍很低（5–40%），因為 GT 不完整；而且留言數由模型自己決定（分母自控）

### 2. 我們的 harness 量不到上下文類的做法 ✅

三個合成標的都是整檔新增（`@@ -0,0 +1,N @@`），模型本來就看得到整個檔案。
上下文擴充、錨點檢查要用**修改型 PR** 來評（Qodo／Martian／AACR 的 diff）。

## 信度：多次取樣／投票

| 來源 | 做法 | 數字 |
|---|---|---|
| paper-lantern ✅ | 3 輪 T=0.8、≥2 票、行號 ±5 配對 | 100 個 Python PR：P 0.270→0.315、R 0.578→0.529、F1 0.351→0.395。**它自己寫：每個 flag 都有人工複核時，投票只會掉 recall** |
| Snyk VulnBench（arXiv 2606.15762）✅ | 同一份 code 跑 5 次 | 命中參考答案的 158 個有 134 個五次全出現；沒命中的 161 個有 80 個只出現一次、22 個五次全出現 |
| Cursor Bugbot（agent） | 8 輪、打亂 diff 順序、多數決；後來改 agentic | resolution rate 52%→70%+，40 個實驗疊加，沒拆出投票的貢獻 |
| SWR-Bench（arXiv 2509.01494）（agent） | N 份 review + 1 次 LLM 彙整 | 主要拉 recall（n=10 時 +118.83%），precision 幾乎不動；n>5 報酬遞減 |
| mira（agent） | 選配多數決，同行同類別算同一筆 | 沒數據 |
| Semantic entropy（Farquhar 2024, Nature）（agent） | 固定位置重問機制，答案分散 = confabulation | QA 任務 AUROC 0.790；**沒有人在 code review 上試過** |

我們的模擬（見 README）：inline precision 跟現有 confidence 門檻比沒有穩定改善；聯集拉 recall；
現行 rubric 下一致性 + confidence 的 AUC +0.028。**不建議當過濾器**。

## 效度：上下文擴充

| 做法 | 出處 | 證據 |
|---|---|---|
| 注入 repo 規範檔（AGENTS.md 等） | pr-agent `configuration.toml:36-43`、`github_provider.py:1590-1606`（agent） | 預設從 default branch 讀、上限 500 行、文件寫明 never read from head。效果只有廠商數字（OpenAI custom rules 召回 58.3%→98%，分母未揭露） |
| hunk 擴到所在函式（`git diff -W`） | pr-agent `git_patch_processing.py:78-216`（agent） | arXiv 2606.01859 ✅：no context 21.83%、塞 149 行**隨機** code 23.04%、鄰近 code 23.62%；arXiv 2505.17928 ✅：KBI 23.70→31.85，但誤報率沒降（agent） |
| 每個檔附最近 5 筆 commit subject | mira（agent） | 無量化證據 |
| 被呼叫端簽章、呼叫端 | kodus-graph、mira（agent） | +2pp 左右；單次呼叫無法查證，容易生出沒根據的 finding |

⚠️ **context 變多，誤報也會變多**：SWR-Bench ✅ 把靜態分析報告塞進 prompt，DeepSeek-R1 precision 9.79→3.33、
每個 PR 的誤報 2.20→7.60 → **不要把 01/02 的輸出餵進 AI review 的 prompt**

token 倍數（agent 實測）：本 repo 21 個 commit，`-W` ×2.13、送整檔 ×3.47；hono 65 個 TS commit，`-W` ×2.79（p90 ×7.8）。
實作限制：GitHub inline comment 只能掛在 PR diff 的行上 → prompt 用 `-W`，定位仍要用 `-U3` 的 diff。

安全：規範檔一律在 post 階段、用 Contents API 從 default branch 讀；剝掉 Unicode tag／bidi／zero-width；不展開 @import。
Copilot 自 2026-07-17 起改讀 head（agent 讀的官方 changelog）；arXiv 2603.18740 改寫 PR 描述的攻擊 33 例成功 32 例（agent）。

## 效度：LLM judge 以外的過濾

| 做法 | 出處 | 證據 |
|---|---|---|
| **claim 型 finding + grep 反駁** | kodus `claim-checker.ts`（AGPL，只能借概念） | ✅ 誤發 15/20 → 0/20、該報的 0/20 漏掉；只用一個模型、4/8/6 個合成 case |
| 錨點健全性 | pr-agent `pr_code_suggestions.py:1715-1740`（agent） | 舊寫法只在 base、新寫法已在 head → 分數歸零（建議 PR 已經做的事） |
| 分桶先驗（檔案型態 × 類別） | AutoCommenter、uReview、BitsAI-CR（agent） | AutoCommenter useful ratio 54%→66%（in-sample） |
| embedding 回饋過濾 | Greptile 部落格（agent） | address rate 19%→55%+；同類要 ≥3 則倒讚，我們的量做不到 |
| LLM judge 事實檢查 | RovoDev（arXiv 2601.01129）✅ | 原文「the Factual Correctness Check has a minimal impact on the RovoDev's overall effectiveness」，跟我們 filter 失敗一致；同文的 Actionability Check（ModernBERT 分類器）讓位置正確的 comment 多 15% |

## 量測：能補 recall 的 benchmark

| 名稱 | 授權／gated | 內容 | 適合拿來做什麼 |
|---|---|---|---|
| **Qodo PR-Review-Bench** ✅ | MIT／否 | 100 PR、580 則 GT（309 功能性 + 271 規則違反，附 `rules_for_repo.jsonl`）；片段 580/580 有值，`file_path` 543、`start_line` 544；PR 在 `agentic-review-benchmarks` org | 修改型 PR 的 recall；可沿用片段比對判命中（agent 實測 89.8% 的 GT 片段首行在 diff 裡逐字找得到）；規則違反那 271 則正好測「注入規範檔」 |
| **Martian Code Review Bench** ✅ | GitHub MIT／HF CC-BY-4.0／否 | 50 PR、GitHub 版 173 則 golden（HF 版 136，要釘版本），沒有行號 | 跟 18+ 個商用工具比排名；n 小（CI 約 ±7pp），要 LLM judge |
| SWR-Bench（agent） | MIT | 1,000 PR（含 500 個 clean），Python | 要窄 CI 時用，約 $10 |
| MCR-Bench（agent） | Apache-2.0 | 558 PR／1,138 defect，5 種語言 | 同上，約 $6 |

注意：Greptile／Augment／Martian／Entelligence 用的是**同一批 50 個 PR**，不是四份獨立證據（agent）。

## 量測：線上代理指標

- outdated rate／addressed：agent 用 Martian 150 筆人工標註交叉比對 → 被處理的 90.6% 是真問題，但真問題有 33.6% 沒人處理 → precision 被低估約 20pp
- 本 repo 59 個 thread：outdated 5.1%、26 個留言後沒有新 commit、`isResolved` 0/59（agent）→ **我們的量與習慣下，線上指標目前沒用**

## 信度量測協定（agent 整理）

分開報「位置一致率」與「議題一致率」，就能把「同一位置、兩次理由不同」量化。
配對三層：位置 → 內容指紋（CodeQL `primaryLocationLineHash` 做法）→ LLM 判定是否同議題（Martian 規則：同一個 code change 能一起修掉才算同一個）。

## 來源

- AACR-Bench 論文 https://arxiv.org/abs/2601.19494
- paper-lantern https://github.com/paperlantern-ai/paper-lantern-challenges （`experiments/code_review/README.md`）
- Snyk VulnBench https://arxiv.org/abs/2606.15762
- Cursor Bugbot https://cursor.com/blog/building-bugbot
- SWR-Bench https://arxiv.org/abs/2509.01494 ／ https://github.com/ZZR0/SWRench
- Semantic entropy https://www.nature.com/articles/s41586-024-07421-0
- kodus-ai https://github.com/kodustech/kodus-ai （`evals/kody-rules/RESULT-1826-FINAL.txt`）
- pr-agent https://github.com/The-PR-Agent/pr-agent
- arXiv 2606.01859（上下文消融）、2505.17928、2511.07017、2509.14856（CodeFuse-CR-Bench）
- RovoDev https://arxiv.org/abs/2601.01129 ；BitsAI-CR https://arxiv.org/abs/2501.15134 ；AutoCommenter https://arxiv.org/abs/2405.13565
- Greptile https://www.greptile.com/blog/make-llms-shut-up
- Qodo https://huggingface.co/datasets/Qodo/PR-Review-Bench
- Martian https://github.com/withmartian/code-review-benchmark ／ https://huggingface.co/datasets/code-review-bench/code-review-bench
- Sun et al.（addressed 判定）https://arxiv.org/abs/2508.18771
