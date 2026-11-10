# ACS理論 Phase 1：トイモデルと実験

論文「自律認知システム理論：倫理的協調知性の数理的基盤（Phase 1：決定論的定式化）」（NF）の付属物である。本文の定義を有限のモデルの上で計算し、形式的に与えた構造が環境の中で自律的に作動して、可行性の維持・閉塞・回復・崩壊を経る様子を、本文の定義どおりに判定して記録する。

> **English summary.** Companion code for the Phase 1 paper on Autonomous Cognitive System (ACS) theory (Japanese). It realises the paper's definitions on small finite models, runs mechanisms that only see their own observations, and judges every step exactly with the paper's sets (feasible set $`K`$, required-environment set $`E_{\mathrm{req}}`$, the $`E_{\mathrm{req}}`$-relative viability kernel, blockage, collapse). Experiments were preregistered with frozen source hashes and held-out seeds. The results are illustrations of existence and of distinctions between concepts; they do **not** show that following the three principles, or having the mechanism, improves survival. See `reports/00_総括_トイモデル_20261027.md`.

## 1. まず読むもの

- `reports/00_総括_トイモデル_20261027.md`：全実験の総括。示せたこと・示せなかったこと、予想される査読上の問いとの対応、限界を書いた。
- 各実験の個別報告：`reports/` にある（4 節の表）。

## 2. 必要なもの

- Python 3 だけで動く。外部パッケージは使わない（Python 3.13 で動作を確認した）。
- すべてリポジトリの最上位で実行する。

## 3. 構成

| パス | 内容 | 開発中のフォルダ名 |
|---|---|---|
| `acsjudge/` | 共通判定層。本文の集合と命題の検査を、領域に依存しない形で計算する | `E8/acsjudge` |
| `domains/furnace/` | 第二の領域「炉番」：モデル・機構・方策 | `E8/domains/furnace` |
| `domains/minacs_domain.py` | MinACS を共通判定層に渡すための包み | `E8/domains` |
| `minacs/` | MinACS（72 状態）：モデル・最小の機構・専用の解析・軌道 | `MINACS/minacs` |
| `acs_toy/` | v2 トイ（7×7 格子、2 個体、ドローン、組織）。§2〜§8 の構造形式を実装 | `TOY2/acs_toy` |
| `e4/` | 事前登録の手続き（`prereg.py`）、評価単位（`adapters.py`）、E1 の方策 | `E4/e4` |
| `run_prereg.py` | 登録・実行・判定 | `E4/run_prereg.py` |
| `experiments/`・`specs/`・`registry.log` | 登録前の仕様、登録済みの仕様（凍結）、追記専用の登録記録 | `E4/` |
| `results/` | 登録済み実験の結果（判定と、単位ごとの全記録） | `E4/results` |
| `replicate.py`・`replication/` | 登録済み実験の再実行と照合（7 節） | — |
| `run_v2.py` | v2 トイのシナリオ実行と検査 | `TOY2/run.py` |
| `run_e6.py`・`report_e6.py` | MinACS の全数計算（E6） | `MINACS/` |
| `run_e8_checks.py`・`regress_minacs.py` | 炉番の全数検査、共通判定層と MinACS 専用の解析の一致の確認（E8） | `E8/` |
| `run_e5.py` | 標準的な可行性の定式化との分類の比較（E5） | `E5/` |
| `run_kernel_tables.py`・`aggregate_p10.py` | 実験 A の核維持応答の表、P10（実験 A・B・C）の記述集計 | — |
| `check_cr2_variants.py` | 実験で用いた機構の全変種の CR-2b 検査 | — |
| `verification/` | 検証スイート：§3 の命題の全数照合、全模型列挙、機構の構造の検査と変異試験、新しい部分模型（綱渡り・乾眠）、Update 則の差し替え、§4・§5 の 83 定義の網羅表。詳しくは `verification/README.md` | — |
| `outputs/` | 上の各スクリプトの出力 | — |
| `reports/` | 報告書（日本語） | — |
| `MANIFEST.md5` | 全ソースの md5（最上位からの相対パス） | — |

## 4. 実験と報告

| 実験 | 問い | 領域 | 登録 | 報告 |
|---|---|---|---|---|
| v2 | §2〜§8 のすべての構造形式を備えた実現が作動するか | v2 | — | `トイモデルv2_実験報告_20261026.md`、`トイモデルv2_論文への寄与_20261026.md` |
| E6 | 全数で検証できる最小の実現 | MinACS | — | `E6_MinACS_報告_20261026.md` |
| E4 | 事前登録の手続きと試験運用（学習の有無、ドローンの有無） | MinACS・v2 | P1・P2 | `E4_報告_20261026.md` |
| E1 | 核維持応答を選ぶ方策と他の方策の比較 | MinACS | P3 | `E1_報告_20261026.md` |
| E1（v2） | 同上 | v2 | P9 | `E1v2_報告_20261026.md` |
| E2 | 原理関連構造的機能（7 群）の除去 | v2 | P4 | `E2_報告_20261026.md` |
| E3 | 判定量は崩壊の警告になるか | MinACS | P5 | `E3_報告_20261026.md` |
| E5 | 標準的な可行性の定式化との分類の比較 | MinACS・炉番 | —（記述のみ） | `E5_報告_20261027.md` |
| E7 | 推定誤差のもとでの乖離 | MinACS | P6 | `E7_報告_20261026.md` |
| E8 | 第二の領域での繰り返し（E1・E2） | 炉番 | P7・P8 | `E8_報告_20261026.md` |
| A・B・C | 条件付き長期可行性の前件の持続・核維持応答の選択と獲得・保証が外れる局面の分類 | MinACS・炉番・v2 | P10 | `ABC_P11_報告_20261027.md` |
| P11 | CR-2b を保つ変種どうしの比較（推定の分解能・更新の頻度） | MinACS・炉番 | P11 | `ABC_P11_報告_20261027.md` |

実験の設計は `reports/実験設計_査読対応_20261026.md` にある。

## 5. 実行の仕方

```
python3 run_v2.py default            # v2 トイの既定シナリオ（outputs/v2/default に出力、検査を含めて約 1 分）
python3 run_e6.py                    # MinACS の全数計算と検査（outputs/out_e6）
python3 regress_minacs.py            # 共通判定層と MinACS 専用の解析の一致（54 項目）
python3 run_e8_checks.py             # 炉番と MinACS の全数検査（outputs/out_e8）
python3 run_e5.py                    # E5（outputs/out_e5）
python3 run_kernel_tables.py         # 実験 A の核維持応答の表（outputs/kernel_tables）
python3 aggregate_p10.py             # P10 の記述集計（outputs/p10_summary.md）
python3 check_cr2_variants.py        # 機構の全変種の CR-2b 検査（outputs/cr2_variants.md）
python3 replicate.py --jobs 2        # 登録済み実験の再実行と照合（数十分〜1 時間程度）
python3 verification/run_all.py      # 検証スイート（約 3 分、結果は verification/out_run/）
```

v2 のシナリオは `default`・`harsh`・`alone`・`no_drone`・`cooperative`・`explorer`・`rocky`・`long` がある。

## 6. 事前登録の手続き

```
python3 run_prereg.py register experiments/<spec>.py         # 登録（実行はしない）
python3 run_prereg.py run specs/<id>.json [--jobs N]         # 検証してから実行・判定
```

- 登録では、仕様とソースの md5 を凍結し、仕様の md5 を `registry.log` に追記する。
- 実行前に次を検証し、どれかに当てはまれば実行を拒否する。
  - 仕様が登録後に改変されている。
  - ソースが登録時から変わっている。
  - 調整用 seed と評価用 seed が重なっている。
- 判定は、登録した規則だけで「支持／不支持／判定不能」に分け、件数を示す。確率や統計の語は用いない。
- 各仮説には、何が起きれば反するかを書く（`how_it_could_fail`）。
- 新しく登録する仕様のソースの md5 は、最上位からの相対パスで記録する。リポジトリの場所を移しても検証できる。

## 7. 登録済み実験の再現

- P10・P11 はこのリポジトリの構成で登録し、ソースの md5 を最上位からの相対パスで記録した。
- 登録済みの仕様（P1〜P8、P9 r2）は、開発中のフォルダ構成と絶対パスで登録した。その後に共通ファイルを拡張したので、ソースの md5 の照合では再検証に通らない。登録時の md5 は各仕様に残してある。
- その代わりに、`replicate.py` で全単位をこのリポジトリのコードで再計算し、記録した単位の結果および判定と照合した。結果は `replication/SUMMARY.md` にある。
  - 単位ごとの原記録（`results/*_units.jsonl`、登録時は 15 ファイル）はリポジトリに含めない。SHA-256 は `results/UNITS_SHA256.md` にある。P1 r1 を除く 14 件は、2026-11-10 に公開したコードで再生成し、SHA-256 とバイト数が照合表の値と一致することを確かめたうえで、Zenodo のデータセットとして公開した（DOI と再生成の条件は、リポジトリ最上位の `README.md` の「生の実験記録」を参照）。P1 r1 の原記録は保存されていない。照合をやり直すには、原記録を `results/` に置く。
  - 原記録がない場合、`replicate.py` と `aggregate_p10.py` は何も計算せず、見つからないファイルを示して終了コード 1 で終わる（照合の未実行を成功と取り違えないため）。`outputs/p10_summary.md` は変わらない。
  - P1 r1 は、背景の生成の誤りを含む版である。修正後のコードでは一致しないのが期待どおりの結果である（E4 報告）。
  - P9 r1 と P10 v2 r1・r2 は実行が途中で止まった版で、結果の記録がない。
  - P10（MinACS・炉番）と P11 の実行後に、P10 v2 のために `e4/adapters.py` を変えた。そのため、これらの仕様もソースの md5 の照合では再検証に通らない。最終のコードでの再計算は記録と一致した（`replication/SUMMARY.md`）。
  - v2 の組織水準の判定（`acs_toy/judge.py` の `org_layer`）と、その検査（`acs_toy/checks.py`）は、本文の組織ACSの定義に合わせて登録後に改めた。このため、相対パスで登録した P10 v2 r3 もソースの md5 の照合に通らない（v2 を用いる P2・P4・P9 は上記の理由で、もともと通らない）。登録実験の評価単位（`e4/adapters.py`）は `org_layer` を呼ばないので、登録した指標と判定はこの変更の影響を受けない（コードの点検による）。

## 8. 主張の範囲

- トイが示すのは、存在と区別の例示までである。本文の命題の補強ではない。
- 一般的な傾向は示さない。現実の系への適用可能性も示さない。
- モデルと機構は設計者（一人）が調整したものである。調整の経緯は各報告と仕様に記載した。
- 三つのトイでは、$`K`$ のどの状態でも基盤機能が作動し構造が保たれる（トイの規約）。そのためトイの中では「$`K`$ にとどまる」ことが崩壊しないことを意味するが、これは本文の一般的な帰結ではない。
- v2 の組織（`acs_toy/org.py`）は、参加者 2 体の状態を組織の状態に含めて記述している。組織水準の判定はトイの規約で、少なくとも一体の参加者が構造を保つ（integ > 0）ときに組織の整形式実現が成り立ち、すべての参加者が構造を失ったときに組織の崩壊とする。組織ACSであることの判定に参加ACS数の条件は置かない（本文 def:org_acs）。参加者がいるので、区分は個体ACS参加型組織ACSに当たる。参加ACS数だけから組織の崩壊を導くことは本文の一般的な帰結ではなく、このモデルの規約である。
- 実験で用いた機構の全変種が CR-2b を満たすことを検査した（`check_cr2_variants.py`、`outputs/cr2_variants.md`）。
- 作り手とは別に、言語モデルを用いた独立のコード監査を一度行った（2026-11-08）。MinACS・炉番について、必要環境充足集合・一段階臨界必要要因・閉塞の二分・応答多様度・$`E_{\mathrm{req}}`$ に相対する可行性核・応答込みの核を、共通判定層を使わない別実装で全数計算し、判定層の出力との不一致は 0 だった。必要環境充足集合が空になる場合などの合成の境界例 13 件も、定義どおりに判定された。この監査は、単位ごとの原記録との照合、v2 の全シナリオの詳細検査、本文の仮定全体の検査を含まない。人による第三者の検証は行われていない。
- 検証スイート（`verification/`）の新しい世界（綱渡り・乾眠）と全模型列挙は、機構をもたない部分模型であり、ACS とは呼ばない。照合の結果は、有限の範囲で本文の文言どおりに計算して反例が出なかったことを示すだけで、本文の命題を補強しない。炉番では、強仮定 ass:theta_exterior_blockage が成り立たない軌道が（行動を任意に選べば）作れる。これは系の反例ではない（`verification/README.md` 4.1）。
- 応答様式のラベル：コードの文字列 "3B-a"・"3B-b"・"3B-c" は、本文の 3B-own・3B-rel・3B-comb にそれぞれ当たる。事前登録したソースの md5 を保つため、コードの文字列は変えていない。

## 9. ライセンス

Python ソースは MIT、それ以外のファイル（報告・仕様・結果・記録・ハッシュ一覧・この README）は CC BY-SA 4.0。適用範囲はリポジトリ直下の `LICENSE.md` による。
