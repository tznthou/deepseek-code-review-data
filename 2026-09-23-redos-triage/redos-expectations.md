# ReDoS 預期表 — 定稿 2026-09-23T05:30:20Z (量測前, 之後不改)

判準: 輸入翻倍時耗時比值 ≈2 → 線性; ≈4 → 平方。每個 case 在子行程跑, 120 s 逾時。
環境: 本機 Python 3.13 (Apple Silicon)。04 跑 ubuntu-latest, 換算時抓慢 3 倍。

## 待判的 4 筆 (走 repo 裡真正的函式)

| case | 位置 | 輸入形狀 (CodeQL 給的) | 預期成長 | 預期 16MB 或上限耗時 |
|---|---|---|---|---|
| 41_real | deepseek_review.select_rules | 'diff --git a/a b/' + 'a b/a'*k | 線性 | 16 MB < 1 s |
| 42_real | locate.index_diff | 'diff --git ' + ' b/' + ' b/a'*k | 線性 | 16 MB < 1 s |
| 44_real | post_review.parse_valid_lines | 同 42 | 線性 | 16 MB < 1 s |
| 43_real | locate.extract_snippets | '『' + '『a'*k (沒有 』) | **平方** | 16K 字元 0.01~0.5 s; 128K 字元 1~30 s |

## 對照組 (證明「為什麼安全」的推論, 不是只看結果)

| case | 做法 | 預期 | 若不符代表 |
|---|---|---|---|
| 41_bare_noM | 同一個 regex **拿掉 re.M**, 字串中段夾 '\nX' | **平方** | 我對「re.M 讓 $ 不可能被拒」的推論錯了 |
| 42_bare_multiline | _GIT_HEADER 直接 search **沒切行**的字串, 中段夾 '\nX' | **平方** | 我對「splitlines 是保護來源」的推論錯了 |
| 43_closed | 43_real 的字串尾巴補一個 』 | 線性 | 平方不是「缺結尾」造成的 |
| 41_real_crlf | 41_real 每段夾 '\r' | 線性 | \r 能讓 $ 拒絕 (我以為不能) |

## 推論 (量測要驗的)
- 41: re.M 下 $ 在每個 \n 前都成立, (.+)$ 只要 ≥1 字元就不可能失敗 → 沒有失敗就沒有回溯爆炸
- 42/44: 輸入是 splitlines() 切過的單行, 行內沒有換行字元, search 在第一個 ' b/' 就成功
- 43: re.S 讓 .+? 跨全文找 』; 沒有 』 時每個 『 起點都掃到尾 → 真的平方; 上限只剩模型輸出 8192 token
