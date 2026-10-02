# Qodo PR-Review-Bench 評估集（2026-09-25 建立）

> 用途：在**修改型 PR** 上量 kit 的 recall。補上兩個缺口：
> AACR-Bench 只能評「判斷一則 comment 對不對」、量不到 recall；
> 合成標的 harness 三個 diff 都是整檔新增，量不到上下文類的做法。
> 報告：本機的 HTML 報告，沒有公開；結論見主 repo 實測紀錄的 qodo-bench 頁

## 資料

- Qodo/PR-Review-Bench（MIT、無門檻），revision `a73957c450a70693a743260e5637fffc44625f16`（`data/revision.txt`）
- 100 個 PR（`agentic-review-benchmarks` org 的 fork，注入的缺陷）、580 則標準答案：309 則功能性缺陷、271 則違反 repo 規則（規則在 `data/rules_for_repo.jsonl`）
- 每個 PR 的 diff 與 metadata 快照在 `prs/<repo>-<n>/`（`pull/{n}` 帶 diff media type，等同 `git diff base...head`）

## 流程（四支腳本，都在 `scripts/`）

| 步驟 | 指令 | 成本 |
|---|---|---|
| 抓資料 | `fetch_prs.py`（已抓過的跳過） | $0 |
| 定錨 | `build_evalset.py` → `evalset.json` | $0 |
| 跑一輪 | `run_bench.py <標籤> [--rubric <檔>]`（參數照 CI；可續跑；key 從 keychain 讀、送出前驗形狀） | 換 rubric 約 $0.74、同 rubric 重跑約 $0.24（離峰） |
| 評分 | `score_bench.py candidates <標籤>` → 盲標 → `score_bench.py report <標籤>` | 標記要人工 |
| 信度 | `reliability.py <標籤A> <標籤B>` | $0 |
| 報告數字 | `make_values.py <輸出.json>` | $0 |

### 定錨（為什麼不用標準答案的行號）

標準答案的 `start_line` 538 則只有 285 則剛好對上新檔同一行 → 改用片段：各行（去空白 ≥ 8 字元）比對 diff 新檔側的 + 行與 context 行，取涵蓋最多片段行的一段；只在刪除行 → 刪除處的新檔位置；都找不到 → 退回 GT 行號；再不行就是 diff 外。
結果：功能性 296/309、規則 265/271 定得到錨點。驗證：有行號的 520 則中 364 則落在錨點內、104 則差 1–3 行、22 則差 >10 行。

### 命中兩層

- **位置命中**：定位後的行號落在錨點 ±3 行內（程式判定；會把「位置準、機制錯」算進來 → 上限）
- **同一個問題**：盲標。判準用 Martian 的規則：一個改動能同時修掉兩者才算 `same`；同處、相關但主張不同，或指對地方但講錯機制 → `partial`
- 候選配對：同檔，且 (a) 定位後行號在錨點 ±5；或 (b) 定位失敗、模型行號 ±10；或 (c) 共用有辨識度的識別字且 ≤ 40 行

## 基準線結果（rubric = v1.4.0，sha256 開頭 `2e0703249d9bbcc7`）

| 範圍 | 則數 | 位置命中 | 同一個問題 | 含 partial |
|---|---|---|---|---|
| 功能性（全部） | 309 | 57.3% | **44.3%** | 55.7% |
| 功能性（diff 內定得到錨點） | 296 | 59.8% | 46.3% | 58.1% |
| 規則（全部，未給規則） | 271 | 27.3% | 10.7% | 15.5% |
| 規則（diff 內） | 265 | 27.9% | 10.9% | 15.8% |

- base-1：100/100 成功、347 筆 finding、$0.738；base-2：100/100、362 筆、$0.241（prompt 快取命中 94.3 萬／94.9 萬 token）
- **雜訊**：功能性位置命中 base-1 0.573 vs base-2 0.576（差 0.3pp）。只有兩輪，還估不了變異數
- **信度**：同一 PR 兩輪的 finding 位置 Jaccard 中位數 0.40（平均 0.49、四分位 0.25–0.67）；base-1 的 finding 有 61% 在 base-2 同位置出現 → **個別 finding 不穩、整體 recall 很穩**
- 位置命中但不是同一個問題的功能性缺陷：46 則（57.3% → 44.3% 的落差）
- 定位退回模型行號（`locate.py` 第 3 層，信心 ≥0.7 會照模型行號貼 inline）：base-1 7/347、base-2 3/362
- 描述統計（不是 precision）：對上 GT 的 finding 有 84% 信心 ≥0.7，其他 finding 72%。其他不等於誤報，Qodo 只列注入的缺陷

## 盲標

- 430 組分給 4 個 subagent（各約 108 組，只准讀自己那份標記單，看不到 confidence／severity）→ `labels-part{1..4}.csv` 合併成 `labels.csv`（same 167／partial 52／no 211）
- 主 session 在看到標記員結果**之前**分層抽 30 組自己標（位置命中 20、其他 10，`spot-sample.json`、`spot-main.csv`）：**四類完全一致 29/30，same 與否 30/30**；唯一分歧是 partial vs no
- 標記員回報的邊界：「同一行、兩個獨立缺陷」標 no（改成 partial 會動到約 6 組）；finding 抓到一半的問題、或嚴重度講錯但修法相同 → 各自判 partial／same。所以「含 partial」那欄比「同一個問題」軟

## 拿它做 A/B 的方法

1. `run_bench.py <新標籤> --rubric <新 rubric>`（注入規範檔要改 prompt 組法時，另寫 runner 分支，保持其他參數不變）
2. `score_bench.py candidates <新標籤>`，位置命中立刻有；「同一個問題」要重新盲標（可沿用上面的指令與判準）
3. 比功能性缺陷的 recall；**規則類那 271 則是「注入 repo 規範檔」的對照組**（這輪沒給規則：10.7%）

## 限制

- 注入的缺陷，而且標準答案不完整 → 只量 recall，不量 precision
- 資料集 2026-02 公開，可能已被模型看過
- 標記員與被評的都是語言模型（Claude 標 DeepSeek）；沒有人類標記對照
- 只有兩輪
