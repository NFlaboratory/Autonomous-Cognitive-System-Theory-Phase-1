# 自律認知システム理論（ACS理論）Phase 1：決定論的定式化

論文「自律認知システム理論：倫理的協調知性の数理的基盤（Phase 1：決定論的定式化）」（NF）の LaTeX 原稿と、本文の定義の一部を有限モデルの上で計算する補助資料（トイモデル）を収める。トイモデルは本文の命題を補強する証拠ではない。

> 論文とトイモデルには版番号を付けない。公開物の識別は公開日と DOI（Zenodo）で行う。公開日と DOI は公開時に記入する。ライセンスは下の「ライセンス」を参照（文書・データは CC BY-SA 4.0、コードは MIT）。

## English summary

This repository contains the Japanese LaTeX manuscript of *Autonomous Cognitive System Theory, Phase 1: a deterministic formulation* and a companion toy-model package.

- **What the paper does.** It defines an autonomous cognitive system (ACS) as a 7-tuple $\Sigma=(X,U,E,f,\Pi,M,\mathrm{Update})$ in discrete time. The tuple includes a set $E$ of *required environmental factors*, each a map $\eta:X\times E_{\mathrm{ext}}\to\{0,1\}$. On this basis the paper formulates three principles as separate constraint axes: self-maintenance (SM), environmental utilization (EU) and feasible response (FR). It also gives a viability kernel relative to the required-environment set $E_{\mathrm{req}}(x)$, a standard mechanism form (TIPA, PSL, ISL) and a minimal relational structure. Finally it separates *blockage* (no feasible action), *loss of well-formed realization*, *functional termination* and *collapse* (non-recoverable loss of structural identity), and applies the framework to organizations.
- **What it does not claim.** The paper is descriptive, not normative. It makes no empirical claim about real agents and gives no general law of action selection. It does not claim that following the three principles, or having the mechanism, makes an agent survive longer. Several results are definitional or standard in viability theory. The manuscript says which results are conditional and which assumptions they need.
- **Relation to viability theory.** The kernel $\mathrm{Viab}_f(K)$ uses the same exists-for-all quantifier type as discriminating and robust viability kernels; the definitions are not claimed identical. What is specific is the state-dependent disturbance range $E_{\mathrm{req}}(x)$. See `docs/ACS_Phase1_overview_en.md` for a 2–4 page English overview.
- **Toy models (auxiliary material).** The `toy/` directory computes some of the paper's definitions exactly on small finite models. It is not evidence for the paper's propositions. It runs mechanisms that see only their own observations and records preregistered experiments. Its results illustrate existence and the distinctions between concepts. They do not support claims of better survival. Independent AI-assisted code checks have been performed. No independent human third-party verification of the code or mathematical arguments has yet been conducted.

## 構成

| パス | 内容 |
|---|---|
| `paper/` | 原稿 15 ファイル（`main.tex`、`abstract.tex`、§1〜§9、付録 A〜C、`references.bib`）と `.latexmkrc` |
| `tools/` | 原稿の静的検査：`check_acs.py`（ラベル・参照・引用）、`ci_gate.py`（CI 用の判定。問題があれば終了コード 1）、`env_guard.py`（保護対象の環境の同一性）、`forbid.py`（禁止表現の件数）、`gen_appendix_c.py`（付録 C の生成）、`gen_dependency_table.py`（依存一覧の生成）、`logic_audit.py`（論理確認のための要確認箇所の抽出：記号の初出、仮定の使用、参照の循環、備考の断定文、節をまたぐ参照）、`prose_extract.py`（§2〜§8 の地の文の抽出。結果の JSON は `-o` で指定したファイル、または標準出力に書く）、`kernel_inclusion_check.py`（可行性核の包含関係の有限検査）、`check_licenses.py`（全ファイルのライセンスの割り当ての検査） |
| `toy/` | トイモデル一式（`toy/README.md` を参照）。検証スイートは `toy/verification/`（§4・§5 の 83 定義のうち照合済み 24 件・例示 19 件・未実施 40 件。`toy/verification/README.md`） |
| `docs/ACS_Phase1_overview_en.md` | 英語の概要（2〜4 ページ。本文の要約で、新しい結果は含まない） |
| `docs/reading_guide.md` | 最初に読む定義 20 と命題 10 |
| `docs/dependency_table.md` | 命題・補題が参照する仮定・定義の索引（本文から自動生成。抽出の限界は同ファイルに記す） |
| `.github/workflows/` | 論文のビルドと検査の自動実行（下書き） |
| `CITATION.cff` | 引用情報（下書き） |

## 原稿のビルド

`paper/` で次を実行する。upLaTeX・biber・dvipdfmx を含む TeX Live（jsclasses 2023-02-12 版以降）が必要である。

```
cd paper
latexmk main.tex
```

- `main.tex` は `\documentclass[dvipdfmx,a4paper]{jsarticle}` と biblatex（biber）を使い、upLaTeX で組む（設定は `paper/.latexmkrc`）。
- 付録 C（`appendix_index.tex`）は本文から生成する。手で編集しない。

```
python3 -I tools/gen_appendix_c.py paper paper/appendix_index.tex abstract.tex section1_intro.tex section2_definition.tex section3_principles.tex section4_tipa.tex section5_extended_dynamics.tex section6_relational.tex section7_collapse.tex section8_organizational_acs.tex section9_limitations.tex
```

## 検査

```
python3 -I tools/ci_gate.py paper       # ラベルの重複、未解決参照、引用キーと .bib の対応（問題があれば終了コード 1）
python3 -I tools/ci_gate.py log paper/main.log   # 組版後：未定義の参照・引用、TeX のエラー
cd toy && python3 regress_minacs.py     # 共通判定層と MinACS 専用の解析の一致（54 項目）
cd toy && python3 run_e8_checks.py      # 炉番と MinACS の全数検査
```

## 主張の範囲

- 本論文は記述理論・構造理論であり、規範理論ではない。倫理的判断そのものは与えない。
- 本論文は Phase 1 の範囲（決定論的・離散時間・コンパクト空間・非分岐性・単一ACS中心）に限られる。
- 個別の領域での経験的な当てはまりは、本論文の主張に含まれない。
- トイモデルが示すのは、存在と区別の例示までである。

## 引用

`CITATION.cff` を参照。DOI 10.5281/zenodo.24095633。

## ライセンス

ファイルの種類と用途に応じて、二つのライセンスを適用する。適用範囲の正本は [`LICENSE.md`](LICENSE.md)。

| 対象 | ライセンス | 全文 |
|---|---|---|
| すべての Python ソース（`*.py`）、`.github/workflows/` の設定ファイル（`*.yml`・`*.yaml`）、`paper/.latexmkrc`、`.gitignore` | MIT | [`LICENSE-MIT`](LICENSE-MIT) |
| 上記とライセンス文書を除くすべてのファイル（論文原稿、`references.bib`、`docs/`、各 README、`CITATION.cff`、実験の報告・仕様・結果・検証記録・登録記録・ハッシュ一覧） | CC BY-SA 4.0 | [`LICENSE-CC-BY-SA-4.0`](LICENSE-CC-BY-SA-4.0) |

- 割り当ては `python3 -I tools/check_licenses.py` で機械的に確かめられる。
- 事前登録実験の記録・仕様・ハッシュは、ライセンス表示のために変更しない（個々のファイルにライセンス表記を書き加えない）。
- 本ライセンス宣言は、第三者が権利をもつ素材について、その第三者の許諾の範囲を超える権利を与えるものではない。
- 論文 §9 の平和利用の文は著者の志向の表明であり、ライセンスの利用条件ではない。

## 生の実験記録

各登録実験の単位ごとの生記録（`units.jsonl`、計約 24MB）はリポジトリに含めず、別に保存する（Zenodo。DOI は公開時に記入）。各ファイルの SHA-256 と、再計算の照合状況は `toy/results/UNITS_SHA256.md` にある。

## 問い合わせ・指摘

誤りの指摘や質問は、GitHub の Issues で受け付ける。指摘には、該当するファイルとラベル（例 `def:viab_core`）または行を添えてほしい。
