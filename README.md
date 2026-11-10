自律認知システム理論（ACS理論）Phase 1：決定論的定式化
Autonomous Cognitive System Theory, Phase 1: a deterministic formulation
論文「自律認知システム理論：倫理的協調知性の数理的基盤（Phase 1：決定論的定式化）」（NF）の LaTeX 原稿と、本文の定義の一部を有限モデルの上で計算する補助資料（トイモデル）を収める。トイモデルは本文の命題を補強する証拠ではない。
> 公開日：2026-11-10。DOI：\[10.5281/zenodo.24095633](https://doi.org/10.5281/zenodo.24095633)（すべての版を指す DOI）。2026-11-10 公開版だけを指す DOI は \[10.5281/zenodo.24095634](https://doi.org/10.5281/zenodo.24095634)。論文とトイモデルには版番号を付けず、公開日と DOI で識別する。ライセンスは下の「ライセンス」を参照（文書・データは CC BY-SA 4.0、コードは MIT）。
English summary
This repository contains the Japanese LaTeX manuscript of Autonomous Cognitive System Theory, Phase 1: a deterministic formulation and a companion toy-model package.
What the paper does. It defines an autonomous cognitive system (ACS) as a 7-tuple $\Sigma=(X,U,E,f,\Pi,M,\mathrm{Update})$ in discrete time. The tuple includes a set $E$ of required environmental factors, each a map $\eta:X\times E_{\mathrm{ext}}\to{0,1}$. On this basis the paper formulates three principles as separate constraint axes: self-maintenance (SM), environmental utilization (EU) and feasible response (FR). It also gives a viability kernel relative to the required-environment set $E_{\mathrm{req}}(x)$, a standard mechanism form (TIPA, PSL, ISL) and a minimal relational structure. Finally it separates blockage (no feasible action), loss of well-formed realization, functional termination and collapse (non-recoverable loss of structural identity), and applies the framework to organizations.
What it does not claim. The paper is descriptive, not normative. It makes no empirical claim about real agents and gives no general law of action selection. It does not claim that following the three principles, or having the mechanism, makes an agent survive longer. Several results are definitional or standard in viability theory. The manuscript says which results are conditional and which assumptions they need.
Relation to viability theory. The kernel $\mathrm{Viab}f(K)$ is the union of the subsets $K'\subseteq K{\mathrm{req}}$ such that every $x\in K'$ admits some $u\in U$ with $f(x,u,e)\in K'$ for all $e\in E_{\mathrm{req}}(x)$. This exists-for-all order is the quantifier type of discriminating and robust viability kernels; the definitions are not claimed identical. What is specific is the state-dependent disturbance range $E_{\mathrm{req}}(x)$. See `docs/ACS\_Phase1\_overview\_en.md` for a 2–4 page English overview.
Toy models (auxiliary material). The `toy/` directory computes some of the paper's definitions exactly on small finite models. It is not evidence for the paper's propositions. In the full models (MinACS, the furnace model and the v2 grid model), the mechanisms see only their own observations, and every step is judged separately with the true model. The verification suite also uses partial models that have no mechanism. The package records preregistered experiments. Its results illustrate existence and the distinctions between concepts. They do not support claims of better survival. Independent AI-assisted code checks have been performed. No independent human third-party verification of the code or mathematical arguments has yet been conducted.
構成
パス	内容
`paper/`	原稿 15 ファイル（`main.tex`、`abstract.tex`、§1〜§9、付録 A〜C、`references.bib`）と `.latexmkrc`
`tools/`	原稿の静的検査：`check\_acs.py`（ラベル・参照・引用）、`ci\_gate.py`（CI 用の判定。問題があれば終了コード 1）、`env\_guard.py`（保護対象の環境の同一性）、`forbid.py`（禁止表現の件数）、`gen\_appendix\_c.py`（付録 C の生成）、`gen\_dependency\_table.py`（依存一覧の生成）、`logic\_audit.py`（論理確認のための要確認箇所の抽出：記号の初出、仮定の使用、参照の循環、備考の断定文、節をまたぐ参照）、`prose\_extract.py`（§2〜§8 の地の文の抽出。結果の JSON は `-o` で指定したファイル、または標準出力に書く）、`kernel\_inclusion\_check.py`（可行性核の包含関係の有限検査）、`check\_licenses.py`（全ファイルのライセンスの割り当ての検査）
`toy/`	トイモデル一式（`toy/README.md` を参照）。検証スイートは `toy/verification/`（§4・§5 の 83 定義のうち照合済み 24 件・例示 19 件・未実施 40 件。`toy/verification/README.md`）
`docs/ACS\_Phase1\_overview\_en.md`	英語の概要（2〜4 ページ。本文の要約で、新しい結果は含まない）
`docs/reading\_guide.md`	最初に読む定義 20 と命題 10
`docs/dependency\_table.md`	命題・補題が参照する仮定・定義の索引（本文から自動生成。抽出の限界は同ファイルに記す）
`.github/workflows/`	論文のビルドと検査を行う GitHub Actions の設定（実行の結果はリポジトリの Actions タブにある）
`CITATION.cff`	リポジトリの引用情報
原稿のビルド
`paper/` で次を実行する。upLaTeX・biber・dvipdfmx を含む TeX Live（jsclasses 2023-02-12 版以降）が必要である。
```
cd paper
latexmk main.tex
```
`main.tex` は `\\documentclass\[dvipdfmx,a4paper]{jsarticle}` と biblatex（biber）を使い、upLaTeX で組む（設定は `paper/.latexmkrc`）。
付録 C（`appendix\_index.tex`）は本文から生成する。手で編集しない。
```
python3 -I tools/gen\_appendix\_c.py paper paper/appendix\_index.tex abstract.tex section1\_intro.tex section2\_definition.tex section3\_principles.tex section4\_tipa.tex section5\_extended\_dynamics.tex section6\_relational.tex section7\_collapse.tex section8\_organizational\_acs.tex section9\_limitations.tex
```
検査
リポジトリの最上位で実行する。2 行目は、原稿のビルドの後に実行する。
```
python3 -I tools/ci\_gate.py paper                # ラベルの重複、未解決参照、引用キーと .bib の対応（問題があれば終了コード 1）
python3 -I tools/ci\_gate.py log paper/main.log   # 組版後：未定義の参照・引用、TeX のエラー
(cd toy \&\& python3 regress\_minacs.py)            # 共通判定層と MinACS 専用の解析の一致（54 項目）
(cd toy \&\& python3 run\_e8\_checks.py)             # 炉番と MinACS の全数検査
```
括弧で囲んだ行は、実行の後に元のフォルダに戻る。
主張の範囲
本論文は記述理論・構造理論であり、規範理論ではない。倫理的判断そのものは与えない。
本論文は Phase 1 の範囲（決定論的・離散時間・コンパクト空間・非分岐性・単一ACS中心）に限られる。
個別の領域での経験的な当てはまりは、本論文の主張に含まれない。
トイモデルが示すのは、存在と区別の例示までである。
引用
`CITATION.cff` を参照。
すべての版を指す DOI：10.5281/zenodo.24095633
2026-11-10 公開版の DOI：10.5281/zenodo.24095634
生の実験記録のデータセット：下の「生の実験記録」を参照
ライセンス
ファイルの種類と用途に応じて、二つのライセンスを適用する。適用範囲の正本は `LICENSE.md`。
対象	ライセンス	全文
すべての Python ソース（`\*.py`）、`.github/workflows/` の設定ファイル（`\*.yml`・`\*.yaml`）、`paper/.latexmkrc`、`.gitignore`	MIT	`LICENSE-MIT`
上記とライセンス文書を除くすべてのファイル（論文原稿、`references.bib`、`docs/`、各 README、`CITATION.cff`、実験の報告・仕様・結果・検証記録・登録記録・ハッシュ一覧）	CC BY-SA 4.0	`LICENSE-CC-BY-SA-4.0`
割り当ては `python3 -I tools/check\_licenses.py` で機械的に確かめられる。
事前登録実験の記録・仕様・ハッシュは、ライセンス表示のために変更しない（個々のファイルにライセンス表記を書き加えない）。
本ライセンス宣言は、第三者が権利をもつ素材について、その第三者の許諾の範囲を超える権利を与えるものではない。
論文 §9 の平和利用の文は著者の志向の表明であり、ライセンスの利用条件ではない。
生の実験記録
事前登録実験の評価単位ごとの生記録（`<実験ID>\_units.jsonl`、14 件、計 66,150 単位・22,371,864 バイト）はリポジトリに含めず、Zenodo のデータセットとして公開している（DOI：10.5281/zenodo.24104195）。照合表 `toy/results/UNITS\_SHA256.md`（2026-10-29 作成）も、同じデータセットに収めた。
14 件は、2026-11-10 に公開したコードで再生成したものである。再生成した各ファイルの SHA-256 とバイト数は、照合表に記録された値と一致した。各ファイルの評価単位は、登録済みの仕様（`toy/specs/`）の組み合わせと過不足なく対応した。
再生成には `toy/run\_prereg.py` の `--deviation` を用いた。登録後に共通のソースファイルを拡張したため、登録時のソースの md5 と一致しないからである（`toy/README.md` 7 節）。再生成のときに作られた判定・報告のファイルはデータセットに含めない。登録済み実験の判定と集計は `toy/results/` にある。
`P1\_minacs\_learning\_r1`（背景の生成に誤りを含み、r2 として登録し直した版）の生記録は保存されておらず、修正後のコードでは同じ記録を作れないため、データセットに含めない。その判定と集計は `toy/results/P1\_minacs\_learning\_r1\_result.json` と `.md` にある。
照合表と `toy/replication/SUMMARY.md` にある「P10 v2 r3 は再計算していない」は、2026-10-29 時点の記録である。2026-11-10 の再生成で、P10 v2 r3 の SHA-256 も照合表の値と一致した。
照合をやり直すには、データセットの 14 件を `toy/results/` に置き、`toy/` で `python3 replicate.py <実験ID>` を実行する。このとき `toy/replication/` の記録が書き換わり、`SUMMARY.md` に行が追記される。公開時の記録と比べるときは、リポジトリの複製の上で行う。
問い合わせ・指摘
誤りの指摘や質問は、GitHub の Issues で受け付ける。指摘には、該当するファイルとラベル（例 `def:viab\_core`）または行を添えてほしい。
