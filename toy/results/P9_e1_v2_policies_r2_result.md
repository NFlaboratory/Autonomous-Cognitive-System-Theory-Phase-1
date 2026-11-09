# P9_e1_v2_policies_r2：事前登録実験の結果

- 登録 md5：`1c985741ee96499207d37c9d034eafdd`
- 登録記録：`2026-10-26T13:35:46.538388+00:00	1c985741ee96499207d37c9d034eafdd	/home/claude/E4/specs/P9_e1_v2_policies_r2.json	P9_e1_v2_policies_r2`
- 実行：2026-10-26T13:52:52.789752+00:00（1023.5 秒、Python 3.13.16）
- 逸脱：なし
- 評価単位：条件ごとに 450（評価 seed 50 本 × 掃引点 9）

| 仮説 | 判定規則の変種 | 判定 | 件数 |
|---|---|---|---|
| H1a | R0 | supported | {'n': 1800, 'holds': 1800} |
| H1b | R0 | supported | {'n': 1800, 'holds': 1800} |
| H2-alone | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |
| H3-alone | R0 | not supported | {'n': 450, 'a>=b': 149, 'a>b': 147, 'a<b': 301, 'a==b': 2} |
| H4-alone | R0 | not supported | {'n': 450, 'a>=b': 282, 'a>b': 239, 'a<b': 168, 'a==b': 43} |
| H5a-alone | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |
| H5b-alone | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |
| H2-default | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |
| H3-default | R0 | not supported | {'n': 450, 'a>=b': 183, 'a>b': 179, 'a<b': 267, 'a==b': 4} |
| H4-default | R0 | not supported | {'n': 450, 'a>=b': 192, 'a>b': 143, 'a<b': 258, 'a==b': 49} |
| H5a-default | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |
| H5b-default | R0 | supported | {'n': 450, 'a>=b': 450, 'a>b': 450, 'a<b': 0, 'a==b': 0} |

- H1a：（回帰検査）証明書つきの核維持応答 u∈U^Viab_cert(x_t) を選んで証明書の集合から出るのは、e_t∉E_req(x_t) の時刻に限られる（prop:kernel_maintenance の一段の形）。
- H1b：（回帰検査）判定層の後続表 f(x,u,lam|rel) は、世界で実現した後続と一致する（局所像による列挙の正確さ）。
- H2-alone：（alone）核維持応答を選ぶ方策の崩壊到達時刻は、一段先だけを見る方策（後続の energy・temp・integ 最大）以上である。
- H3-alone：（alone）核維持応答を選ぶ方策の崩壊到達時刻は、TIPA 機構以上である。
- H4-alone：（alone）TIPA 機構の崩壊到達時刻は、記憶をもたない観測反射以上である。
- H5a-alone：（alone）TIPA 機構の崩壊到達時刻は、固定行動列以上である。
- H5b-alone：（alone）TIPA 機構の崩壊到達時刻は、常に待機する方策以上である。
- H2-default：（default）核維持応答を選ぶ方策の崩壊到達時刻は、一段先だけを見る方策（後続の energy・temp・integ 最大）以上である。
- H3-default：（default）核維持応答を選ぶ方策の崩壊到達時刻は、TIPA 機構以上である。
- H4-default：（default）TIPA 機構の崩壊到達時刻は、記憶をもたない観測反射以上である。
- H5a-default：（default）TIPA 機構の崩壊到達時刻は、固定行動列以上である。
- H5b-default：（default）TIPA 機構の崩壊到達時刻は、常に待機する方策以上である。
