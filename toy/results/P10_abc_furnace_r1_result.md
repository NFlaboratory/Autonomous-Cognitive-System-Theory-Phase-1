# P10_abc_furnace_r1：事前登録実験の結果

- 登録 md5：`2ab8b9bc5400855c26b347ad0cd9adb2`
- 登録記録：`2026-10-27T08:31:58.864712+00:00	2ab8b9bc5400855c26b347ad0cd9adb2	/home/claude/release/acs-toy/specs/P10_abc_furnace_r1.json	P10_abc_furnace_r1`
- 実行：2026-10-27T08:32:04.434355+00:00（0.7 秒、Python 3.13.16）
- 逸脱：なし
- 評価単位：条件ごとに 900（評価 seed 50 本 × 掃引点 18）

| 仮説 | 判定規則の変種 | 判定 | 件数 |
|---|---|---|---|
| H1 | R0 | supported | {'n': 900, 'holds': 900} |

- H1：（回帰検査）両前件が成り立つ時刻（OK）に核から出る例はない（prop:kernel_maintenance の一段の形）。
