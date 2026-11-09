#!/usr/bin/env python3
"""CI 用の判定ゲート（外部パッケージ不要）。問題があれば終了コード 1 を返す。

使い方:
  python3 -I tools/ci_gate.py paper      原稿の静的検査（check_acs.py の出力を判定）
  python3 -I tools/ci_gate.py log main.log   組版ログの未定義参照・未定義引用・エラーの判定

check_acs.py は問題があっても終了コード 0 を返すため、その出力の定型文で判定する。
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def gate_paper(paper):
    out = subprocess.run([sys.executable, "-I", str(HERE / "check_acs.py"), paper],
                         capture_output=True, text=True)
    text = out.stdout
    sys.stdout.write(text)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        return [f"check_acs.py の終了コード {out.returncode}"]
    need = {
        "ラベル重複なし": "OK（重複なし",
        "未解決参照なし": "OK（すべて解決）",
        "未定義の引用なし": "未定義の引用（要 .bib 追加）: なし",
        "\\textnormal なし": "[8] \\textnormal 使用（全廃方針）\n  OK（なし）",
    }
    return [name for name, s in need.items() if s not in text]


def gate_log(log):
    text = Path(log).read_text(encoding="utf-8", errors="replace")
    bad = []
    pats = {
        "未定義の参照": r"LaTeX Warning: Reference .* undefined",
        "未定義の引用": r"(LaTeX|Package biblatex) Warning: Citation .* undefined",
        "参照の再実行要求": r"Rerun to get (cross-references|citations) right|Please \(re\)run Biber",
        # 箱の内容の書き出し（"! \OML/..." のように \ で始まる行）はエラーではないので除く
        "TeX のエラー": r"^! (?!\\)",
    }
    for name, p in pats.items():
        n = len(re.findall(p, text, flags=re.M))
        print(f"{name}: {n}")
        if n:
            bad.append(name)
    return bad


def main():
    if len(sys.argv) == 2:
        bad = gate_paper(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[1] == "log":
        bad = gate_log(sys.argv[2])
    else:
        sys.exit(__doc__)
    if bad:
        print("NG: " + "、".join(bad))
        sys.exit(1)
    print("GATE OK")


if __name__ == "__main__":
    main()
