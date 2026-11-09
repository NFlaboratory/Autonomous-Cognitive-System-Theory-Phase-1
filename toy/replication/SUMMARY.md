# 登録済み実験の再計算と照合

| id | units | identical | different | not in record | verdicts identical |
|---|---|---|---|---|---|
| P1_minacs_learning_r1 | 7200 | 5465 | 1735 | 0 | 0/6 |
| P1_minacs_learning_r2 | 7200 | 7200 | 0 | 0 | 6/6 |
| P2_v2_drone_r1 | 900 | 900 | 0 | 0 | 2/2 |
| P3_e1_minacs_policies_r1 | 7200 | 7200 | 0 | 0 | 6/6 |
| P4_e2_v2_ablation_r1 | 4950 | 4950 | 0 | 0 | 10/10 |
| P5_e3_minacs_alarms_r1 | 3600 | 3600 | 0 | 0 | 5/5 |
| P6_e7_minacs_estimation_r1 | 5400 | 5400 | 0 | 0 | 6/6 |
| P7_e8_furnace_policies_r1 | 7200 | 7200 | 0 | 0 | 6/6 |
| P8_e8_furnace_ablation_r1 | 7200 | 7200 | 0 | 0 | 7/7 |
| P9_e1_v2_policies_r2 | 7200 | 7200 | 0 | 0 | 12/12 |
| P10_abc_minacs_r1 | 1800 | 1800 | 0 | 0 | 1/1 |
| P10_abc_furnace_r1 | 1800 | 1800 | 0 | 0 | 1/1 |
| P11_inclass_minacs_r1 | 5400 | 5400 | 0 | 0 | 7/7 |
| P11_inclass_furnace_r1 | 5400 | 5400 | 0 | 0 | 7/7 |

- 照合：登録済み実験の全評価単位を、このリポジトリのコードで再計算し、記録した単位の結果（`results/<id>_units.jsonl`）と、登録した規則による判定（`results/<id>_result.json`）を照合した（`python3 replicate.py --jobs 2`）。
- 最終のコードで照合した（2026-10-27）：P1 r2・P3・P5〜P8・P10（MinACS・炉番）・P11。P1 r1・P2・P4・P9 r2 の照合は、P10・P11 の評価単位を追加する前のコードで行った。その後の `e4/adapters.py` の変更は新しい関数の追加と、P10 v2 の関数の中の変更だけで、P1・P2・P4・P9 の関数は変えていない。
- P10 v2 r3 は最終のコードで実行したもので、ここでは再計算していない。
- P1 r1 の不一致は期待どおりの結果である。r1 は背景の生成に誤り（背景列の長さが判定規則の変種に依存していた）を含む版で、修正は r2 として登録し直した（E4 報告）。
- P9 r1、P10 v2 r1・r2 は実行が途中で止まった版で、結果の記録がないため対象外。
- 各 id の詳細（不一致の例を含む）は `replication/<id>.json`。
