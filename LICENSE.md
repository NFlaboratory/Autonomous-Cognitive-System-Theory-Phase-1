# ライセンス（License）

Copyright (c) 2026 NF

本リポジトリでは、ファイルの種類と用途に応じて、次の二つのライセンスを適用する。

## MIT License（コード）

- すべての Python ソースファイル（`*.py`）
- `.github/workflows/` 内の GitHub Actions 設定ファイル（`*.yml`、`*.yaml`）
- `paper/.latexmkrc`
- `.gitignore`

全文：[`LICENSE-MIT`](LICENSE-MIT)

## Creative Commons Attribution-ShareAlike 4.0 International（CC BY-SA 4.0：論文・文書・データ）

上の MIT の対象と、ライセンス文書そのもの（`LICENSE.md`、`LICENSE-MIT`、`LICENSE-CC-BY-SA-4.0`）を除く、本リポジトリのすべてのファイル。

これには、論文原稿（`paper/*.tex`）、参考文献データ（`references.bib`）、説明文書（`docs/`、各 README）、`CITATION.cff`、実験の報告・仕様・結果・検証記録・登録記録・ハッシュ一覧（`toy/reports/`、`toy/specs/`、`toy/results/`、`toy/outputs/`、`toy/replication/`、`toy/verification/out/`、`toy/registry.log`、`toy/MANIFEST.md5` など）を含む。

全文：[`LICENSE-CC-BY-SA-4.0`](LICENSE-CC-BY-SA-4.0)（Creative Commons が公表する法的条文の平文版）

## 注記

- ファイルごとの割り当ては `python3 tools/check_licenses.py` で機械的に確かめられる。この検査は、ライセンス文書 3 件を除く収録ファイルを MIT か CC BY-SA 4.0 の一方に分類し、MIT に分類されないコード様の拡張子のファイルがないこと、ライセンス文書 3 件がそろっていることを確かめる。ライセンス文書の法的な正確さや、`CITATION.cff` との一致は検査しない。
- 事前登録実験の記録・仕様・ハッシュは、ライセンス表示のために変更しない。ライセンスはこの宣言によって適用し、個々のファイルに表記を書き加えない。
- 実験データのうち事実や数値そのものには、著作権が成立しない部分がありうる。この宣言は、事実そのものへの排他的な権利を生むものではない。
- 本ライセンス宣言は、第三者が権利をもつ素材について、その第三者の許諾の範囲を超える権利を与えるものではない。
- 論文 §9 の平和利用の文は著者の志向の表明であり、上の二つのライセンスの利用条件を変更・追加するものではない。

---

This repository uses two licenses. The MIT License applies to all Python sources (`*.py`), the GitHub Actions workflow files in `.github/workflows/`, `paper/.latexmkrc` and `.gitignore`. All other files, except the license documents themselves, are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). This includes the manuscript, the bibliography, the documents, `CITATION.cff`, and the experiment reports, specifications, results, verification records, registry and hash lists. The statement on peaceful use in §9 of the manuscript expresses the author's intention and does not add conditions to either license.
