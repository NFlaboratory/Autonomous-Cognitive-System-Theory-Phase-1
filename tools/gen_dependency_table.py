#!/usr/bin/env python3
"""命題・補題の依存一覧を本文から生成する（外部パッケージ不要）。

使い方: python3 -I tools/gen_dependency_table.py paper docs/dependency_table.md

抽出の規則（限界は出力の冒頭に記す）:
- 対象は section1〜section9 の proposition・lemma 環境。
- 環境の本文と、その直後（空行・コメントだけを挟む）の proof 環境の中の \\ref を数える。
- 「用いない」「用いず」「使わない」を含む文（「。」で区切る）の中の参照は依存から除き、末尾に列挙する。
"""
import re
import sys
from pathlib import Path

SECTIONS = [
    "section1_intro.tex", "section2_definition.tex", "section3_principles.tex",
    "section4_tipa.tex", "section5_extended_dynamics.tex", "section6_relational.tex",
    "section7_collapse.tex", "section8_organizational_acs.tex", "section9_limitations.tex",
]
KINDS = {"proposition": "命題", "lemma": "補題"}
NEG = ("用いない", "用いず", "使わない")
REF = re.compile(r"\\(?:eq)?ref\{([^}]*)\}")


def strip_comments(s):
    return re.sub(r"(?<!\\)%.*", "", s)


def env_block(text, start, name):
    """start は \\begin{name} の位置。対応する \\end{name} の直後の位置を返す（入れ子対応）。"""
    pat = re.compile(r"\\(begin|end)\{" + name + r"\}")
    depth = 0
    for m in pat.finditer(text, start):
        depth += 1 if m.group(1) == "begin" else -1
        if depth == 0:
            return m.end()
    raise ValueError(f"unterminated {name} at {start}")


def refs_split(body):
    used, excluded = [], []
    for sent in body.split("。"):
        keys = [k.strip() for m in REF.finditer(sent) for k in m.group(1).split(",")]
        (excluded if any(n in sent for n in NEG) else used).extend(keys)
    return used, excluded


def uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main(paper, out):
    paper = Path(paper)
    rows, all_ass, excl_rows = [], [], []
    for i, fn in enumerate(SECTIONS, 1):
        text = strip_comments((paper / fn).read_text(encoding="utf-8"))
        all_ass += re.findall(r"\\begin\{assumption\}(?:\[[^\]]*\])?\s*\\label\{(ass:[^}]+)\}", text)
        for m in re.finditer(r"\\begin\{(proposition|lemma)\}", text):
            kind = m.group(1)
            end = env_block(text, m.start(), kind)
            body = text[m.start():end]
            rest = text[end:]
            pm = re.match(r"\s*\\begin\{proof\}", rest)
            if pm:
                pend = env_block(rest, pm.start() + rest[pm.start():].index("\\begin"), "proof")
                body += rest[:pend]
            tm = re.match(r"\\begin\{" + kind + r"\}\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]", body)
            title = tm.group(1).strip() if tm else ""
            lm = re.search(r"\\label\{([^}]+)\}", body)
            label = lm.group(1) if lm else "(no label)"
            used, excl = refs_split(body)
            used = [k for k in uniq(used) if k != label]
            excl = [k for k in uniq(excl) if k not in used and k != label]
            rows.append({
                "sec": f"§{i}", "kind": KINDS[kind], "label": label, "title": title,
                "ass": [k for k in used if k.startswith("ass:")],
                "ndef": len([k for k in used if k.startswith("def:")]),
                "pl": [k for k in used if k.startswith(("prop:", "lem:"))],
            })
            for k in excl:
                excl_rows.append((label, k))
    nprop = sum(r["kind"] == "命題" for r in rows)
    nlem = sum(r["kind"] == "補題" for r in rows)
    code = lambda ks: " ".join(f"`{k}`" for k in ks)
    L = ["# 命題・補題の依存一覧（自動生成）", "",
         f"- 生成：`python3 -I tools/gen_dependency_table.py paper docs/dependency_table.md`",
         f"- 対象：本文（§1〜§9）の命題 {nprop}・補題 {nlem}。各命題・補題の主張と、その直後の証明の中で `\\ref` により参照される仮定・定義・命題・補題を列挙する。",
         "- 「仮定~\\ref{…} を用いない」のように不使用を述べる文（「用いない」「用いず」「使わない」を含む文）の中の参照は依存から除いた（除外した参照は末尾に記す）。",
         "- **抽出の限界**：`\\ref` を使わず言葉だけで依拠している場合、定義の整形式性を通じた間接的な依存、および備考・地の文での参照は数えていない。文の区切りによる除外は機械的であり、一つの文に使用と不使用が混在する場合は使用も除外される。依存関係の完全な記述ではなく、照合を始めるための索引である。",
         "", "| 節 | 種類 | ラベル | 表題 | 参照する仮定 | 参照する定義の数 | 参照する命題・補題 |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['sec']} | {r['kind']} | `{r['label']}` | {r['title'].replace('|', '\\|')} | {code(r['ass'])} | {r['ndef']} | {code(r['pl'])} |")
    L += ["", "## 仮定ごとの使用（命題・補題とその証明の中での参照）", "", "| 仮定 | 参照する命題・補題 |", "|---|---|"]
    unused = 0
    for a in all_ass:
        users = [r["label"] for r in rows if a in r["ass"]]
        unused += not users
        L.append(f"| `{a}` | {code(users) if users else '（なし）'} |")
    L += ["", f"命題・補題とその証明から参照されない仮定：{unused} 件（{len(all_ass)} 件中）。定義・備考・地の文での参照は別に数える必要がある。",
          "", "## 依存から除いた参照（不使用を述べる文）", ""]
    L += [f"- `{l}` の中の `{k}`" for l, k in excl_rows] or ["（なし）"]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"propositions={nprop} lemmas={nlem} assumptions={len(all_ass)} unused={unused} excluded={len(excl_rows)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
