# 收尾清單第 2 項：prompt 兩個已知問題（2026-10-01）

> **結案：不改（子超 10-01）。** 追加判準（四輪合併 precision 差 ≥ −3pp）兩個標記版本都沒過（−3.5pp／−5.2pp）；
> 改動沒有量到好處（缺測試 8 輪都是 0），而改 rubric 會讓 Qodo 等既有基準失去可比性，所以不拆開量、維持現行 prompt。
> 重開條件：之後因為別的理由要改 rubric 或 `python.md` 時，順手處理這兩個問題，並用同一套判準（含 precision）量。

子超 10-01 選定改法：第 6 條刪掉「新增分支沒有對應測試」那半條，`python.md` 那行一起刪；
rubric 另一句跟 v1.6.0 對不上的（「0.7 以上貼成行內留言」）不併，之後再討論。

## B 組的三個改動（`scripts/make_variants.py` 產生，A 是 repo 現行的逐位元組副本）

1. rubric 開頭 5 行 blockquote（寫給維護者的說明）刪掉。違反 README §4.9 的判準；資訊已在 README 省錢開關第 7 點、SETUP-CHECKLIST
2. rubric 第 6 條：「**可測試性與可觀測性**：新增分支沒有對應測試、錯誤被吞掉、失敗時無足夠 log/context。」
   →「**可觀測性**：錯誤被吞掉、失敗時無足夠 log/context。」（README §4.9：有作用的是「錯誤被吞掉」那半條）
3. `prompts/rules/python.md` 刪掉「不要報「缺少測試」——你看不到測試檔案是否存在於這次 diff 之外。」

## 跑前定稿（寫在跑之前）

- **這次量的是「改了不會變差」，不是改善**：兩條規則現在都沒在作用（confidence-loop 6 輪、每輪 80–90 筆，缺測試 finding 0 筆）
- harness：`2026-09-24-confidence-loop`（三標的 × 5 次、`deepseek-v4-pro`、參數照 CI；兩個 Python 標的會套到 `python.md`）
- 輪次：`ph-A1` → `ph-B1` → `ph-A2` → `ph-B2`，同一時段交錯跑（輸出在 confidence-loop 的 `rounds/`）
- 標記：`label_round.py` 半自動；人工的部分盲標（標記單不含 confidence、severity），由主 session 標
- 判準（兩輪合併、在全部 finding 上重算，`analyze_pooled.py --min-delta -1/20`）：
  - 主：嚴格版 AUC(B) − AUC(A) ≥ −0.05（loop 的 keep 門檻反過來；同一份 prompt 重跑差 0.016–0.017）
  - anti-criteria a–e 沿用 loop 的定義，baseline 換成 A 的合併值
  - 寬鬆版 AUC 一起報；兩版結論不同就照實寫
  - 另外數「缺測試」finding：預期 A、B 都是 0
- 通過 → 開 PR 改 kit（rubric、`python.md`、README §4.9 補現況、CHANGELOG）並發版；
  不通過 → 不改，三個改動拆開各量一次再決定

## 結果（2026-10-01，07:56–07:59 UTC 跑，尖峰時段約 $0.44）

跑前檢查：`make_variants.py` A 跟 repo 逐位元組相同、B 只差三處；Guard 前三項過（hash 只對不上兩支剛改的 harness 腳本、
以及 09-24 之後本來就改過的 `deepseek_review.py`、`review-rubric.md`；A／B 用同一份 reviewer）。
四輪各 15/15 成功；盲標：四輪人工判定 110 筆合併、打亂、換匿名編號（`blind/`），抽查 29 筆推翻 3 筆。

**跑前定稿的判定：B 通過。**

| | A（ph-A1+A2） | B（ph-B1+B2） |
|---|---|---|
| findings | 177 | 178 |
| AUC 嚴格（CI） | 0.720（0.654–0.788） | 0.779（0.718–0.836） |
| AUC 寬鬆 | 0.740 | 0.810 |
| A 類召回 probe／python／shell | 6／49／50 | 5／49／50 |
| 缺測試 finding | 0 | 0 |

合併 AUC 差 +0.059（門檻 ≥ −0.05）；anti-criteria a–e 全過。

**事後才看到、不在判準裡的：precision 掉了。**

- 成立／不成立：A 147／30（83.1%）、B 137／41（77.0%）。分輪：A1 81.8%、A2 84.3%、B1 80.2%、B2 73.9%
- 不成立增加的部分，分散在十幾個項目，每項差 1–3 筆，也有幾項變少；找不到對應到某個改動的項目
- 事後置換檢定（`scripts/posthoc_permutation.py`，以一次跑為單位、標的內分組、5,000 次）：
  precision −6.1pp 雙尾 p = 0.088；AUC +0.059 p = 0.203。兩者都沒過 0.05，precision 是邊緣值、方向不利
- 跑前判準漏了 precision：anti-criteria b 只擋「finding 數減半」，擋不到「成立變少、不成立變多」

## 追加：各補兩輪（子超 10-01 選定；跑前定稿於 08:09 UTC）

- 輪次：`ph-A3` → `ph-B3` → `ph-A4` → `ph-B4`，同樣交錯跑、同一套 variants
- **判準：A1–A4 與 B1–B4 各四輪合併，precision 差（B − A）≥ −3pp → 出貨；否則三個改動拆開量**
  - precision＝成立／全部 finding（嚴格：disputed 算不成立）。−3pp 取自 A1、A2 之間的差距（2.5pp）
  - AUC（嚴格／寬鬆）、anti-criteria a–e、缺測試 finding 照樣在四輪合併上報，但不改變上面的判定
- **只補這一次**：結果不滿意也不再加跑（加跑到滿意為止就是 optional stopping）
- 盲標：新四輪的人工判定一樣合併、打亂、換匿名編號（`blind2/`），標記者與前例同一套；標記時看不出 A／B，
  但標記者已經知道第一批的結果

### 追加的結果（08:09–08:12 UTC 跑；四輪各 15/15；缺測試 finding 8 輪全是 0）

第二批盲標：人工判定 98 筆、抽查 29 筆推翻 5 筆。抽查發現自動規則會在 PR-A1／PR-X1／PR-X2 套錯
（只看位置與關鍵字、不看講的後果），於是**加了一次殘差檢查（不在跑前定稿裡）**：8 輪裡自動標成
PR-A1／X1／X2／B2、沒被人工覆蓋的 61 筆全部打亂盲看（`blind3/`），改掉 20 筆（A 組 7、B 組 13）。
所以判定兩個版本都算（`scripts/final_check.py`）：

| 標記版本 | A（四輪） | B（四輪） | precision 差 | 判定（≥ −3pp 出貨） | 置換 p |
|---|---|---|---|---|---|
| (i) 跑前定稿的流程 | 283/351 = 80.6% | 276/358 = 77.1% | −3.5pp | **不出貨** | 0.171 |
| (ii) 加上殘差檢查 | 276/351 = 78.6% | 263/358 = 73.5% | −5.2pp | **不出貨** | 0.069 |

**兩個版本都低於門檻 → 照跑前定稿：不出貨。** 置換檢定兩版都沒過 0.05，但方向一致。

四輪合併的其他數字（版本 ii）：AUC 嚴格 A 0.738 → B 0.756（+0.019）；anti-criteria a–e 全過；
precision 的下降集中在 probe（陷阱最多的標的）：A 42/75 = 56.0% → B 34/82 = 41.5%；
python 82.0% → 79.9%、shell 87.6% → 86.1%。probe 的 A 類召回 11/20 → 7/20（anti-criteria d 剛好壓線通過）。
是三個改動裡的哪一個造成的，這份資料分不出來。

附帶發現（harness 本身）：自動規則在 PR-A1／X1／X2 的套錯率是 20/61，會把「後果寫錯」的 finding 算成 valid，
兩組都受影響；之後用這個 harness 時，這三項要人工看過，或把規則改成連後果一起比對。

## harness 腳本的改動（confidence-loop 已結案，Guard 快照因此會對不上 `scripts/*.py`）

- `run_round.py` 加 `--rules-dir`（不給就是 repo 的 `prompts/rules`，行為照舊）；manifest 多記 `rules_dir`
- `analyze_pooled.py` 加 `--min-delta`（不給就是原本的 +1/20）；判定那行改成「B 通過／維持 A」
