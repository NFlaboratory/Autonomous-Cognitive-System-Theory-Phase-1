#!/usr/bin/env python3
"""論理確認の第 1 段：人が読む前に、要確認の箇所を本文から機械的に抽出する（外部パッケージ不要）。

使い方: python3 -I tools/logic_audit.py paper out_dir [audit_status.tsv]

状態台帳（audit_status.tsv）を与えると、各候補の判定（検出／本文確認済み・問題なし／修正提案／保留／著者承認済み）を
ID で引き継いで書き戻す。省略時は out_dir/audit_status.tsv を使う。

out_dir に次の 5 つの報告（Markdown）と要約 summary.md を書く。
  A_symbol_first_use.md   付録 B の記号ごとに、定義箇所より前の本文での使用を列挙する。
  B_assumption_use.md     仮定ごとに、命題・補題（証明を含む）、定義、備考・地の文からの参照を数える。
  C_dependency_graph.md   定義・仮定・命題・補題の参照グラフの循環と、後方の命題・補題を引く証明を列挙する。
  D_remark_assertions.md  備考の中で、断定の語を含み、\\ref も証明も伴わない文を列挙する。
  E_cross_section.md      節をまたぐ参照（\\S\\ref と \\ref）を、参照元と参照先の節の組で列挙する。

いずれも候補の抽出であり、判定ではない。抽出の規則と限界は各報告の冒頭に記す。
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

FILES = [
    "abstract.tex", "section1_intro.tex", "section2_definition.tex", "section3_principles.tex",
    "section4_tipa.tex", "section5_extended_dynamics.tex", "section6_relational.tex",
    "section7_collapse.tex", "section8_organizational_acs.tex", "section9_limitations.tex",
]
SEC = {f: ("要旨" if f == "abstract.tex" else f"§{f[7]}") for f in FILES}
ENVS = ["definition", "assumption", "proposition", "lemma", "theorem", "observation",
        "remark", "problem", "proof"]
KIND_JA = {"definition": "定義", "assumption": "仮定", "proposition": "命題", "lemma": "補題",
           "theorem": "定理", "observation": "観察記録", "remark": "備考", "problem": "問題",
           "proof": "証明"}
REF = re.compile(r"\\(?:eq|page)?ref\{([^}]*)\}")
NEG = ("用いない", "用いず", "使わない")


ITEMS = []  # (id, 区分, 位置, 要旨)
STATUSES = ("検出", "要再照合", "本文確認済み・問題なし", "修正提案", "保留", "著者承認済み")


DEPS = {}  # id -> (依存するラベルまたは位置の列, 文)


def item(iid, cat, where, summary, deps=(), text=None):
    """候補を登録する。deps（ラベルまたは本文中の位置）と text から判定根拠のハッシュを作る。"""
    ITEMS.append((iid, cat, where, summary))
    DEPS[iid] = (list(deps), text)
    return iid


def basis_hash(doc, iid):
    import hashlib
    deps, text = DEPS.get(iid, ([], None))
    parts = []
    for d in deps:
        pos = doc.labels.get(d) if isinstance(d, str) else d
        if pos is None:
            parts.append(f"<missing:{d}>")
            continue
        e = doc.env_at(pos, ENVS)
        if e is not None:
            body = doc.text[e["begin"]:e["end"]]
            if e["kind"] in ("proposition", "lemma", "theorem") and re.match(r"\s*\\begin\{proof\}", doc.text[e["end"]:]):
                pe = next((x for x in doc.envs if x["kind"] == "proof" and x["begin"] >= e["end"]), None)
                if pe:
                    body += doc.text[e["end"]:pe["end"]]
        else:
            a = doc.text.rfind("。", 0, pos) + 1
            b = doc.text.find("。", pos)
            body = doc.text[a:(b + 1 if b >= 0 else pos + 300)]
        parts.append(re.sub(r"\s+", "", body))
    if text is not None:
        parts.append(re.sub(r"\s+", "", text))
    return hashlib.md5("\x1e".join(sorted(set(parts))).encode("utf-8")).hexdigest()[:12]


def blank_comments(s):
    """% 以降を同じ長さの空白に置き換える（位置を保つ）。"""
    return re.sub(r"(?<!\\)%[^\n]*", lambda m: " " * len(m.group(0)), s)


class Doc:
    def __init__(self, paper):
        self.text, self.starts, self.raw = "", {}, {}
        for f in FILES:
            t = blank_comments((paper / f).read_text(encoding="utf-8"))
            self.starts[f] = len(self.text)
            self.raw[f] = t
            self.text += t + "\n"
        self.envs = self._envs()
        self.labels = {}
        for m in re.finditer(r"\\label\{([^}]+)\}", self.text):
            self.labels.setdefault(m.group(1), m.start())

    def where(self, pos):
        f = max((f for f in FILES if self.starts[f] <= pos), key=lambda f: self.starts[f])
        line = self.text.count("\n", self.starts[f], pos) + 1
        return f, line

    def _envs(self):
        pat = re.compile(r"\\(begin|end)\{(" + "|".join(ENVS) + r")\}")
        stack, out = [], []
        for m in pat.finditer(self.text):
            if m.group(1) == "begin":
                stack.append((m.group(2), m.start()))
            else:
                while stack:
                    k, b = stack.pop()
                    if k == m.group(2):
                        body = self.text[b:m.end()]
                        lm = re.search(r"\\label\{([^}]+)\}", body)
                        out.append({"kind": k, "begin": b, "end": m.end(),
                                    "label": lm.group(1) if lm and k != "proof" else None})
                        break
        out.sort(key=lambda e: e["begin"])
        return out

    def env_at(self, pos, kinds=None):
        best = None
        for e in self.envs:
            if e["begin"] <= pos < e["end"] and (kinds is None or e["kind"] in kinds):
                if best is None or e["begin"] >= best["begin"]:
                    best = e
        return best

    def def_pos(self, label):
        """ラベルを含む環境の開始位置（環境がなければラベルの位置）。"""
        p = self.labels.get(label)
        if p is None:
            return None
        e = self.env_at(p)
        return e["begin"] if e and e["kind"] != "proof" else p

    def section_of_label(self, label):
        p = self.labels.get(label)
        return SEC[self.where(p)[0]] if p is not None else "?"


def loc(doc, pos):
    f, line = doc.where(pos)
    return f"{SEC[f]} {f}:{line}"


def esc(s):
    return s.replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------- A
def norm(s):
    return re.sub(r"\s+", "", s)


def top_split(m):
    """括弧の外のカンマと \\ （空白）、\\quad で区切る。"""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(m):
        c = m[i]
        if c in "{([":
            depth += 1
        elif c in "})]":
            depth -= 1
        if depth == 0 and c == ",":
            parts.append(cur)
            cur = ""
        elif depth == 0 and m.startswith("\\quad", i):
            parts.append(cur)
            cur = ""
            i += 5
            continue
        else:
            cur += c
        i += 1
    parts.append(cur)
    return [re.sub(r"^\\\s|\\\s$|^\\,|\\,$", "", p.strip()).strip() for p in parts]


def split_symbols(cell):
    out = []
    for m in re.finditer(r"\$([^$]+)\$", cell.strip()):
        out += [p for p in top_split(m.group(1)) if p]
    return out


def report_A(doc, paper):
    tb = blank_comments((paper / "appendix_symbols.tex").read_text(encoding="utf-8"))
    rows = re.findall(r"\n(\$[^\n]*?)\s*&(.*?)&(.*?)&(.*?)\\\\", tb, flags=re.S)
    ntext = norm(doc.text)
    # 正規化後の位置から元の位置へ戻す表
    idx = [i for i, c in enumerate(doc.text) if not c.isspace()]
    out, skipped, checked = [], [], 0
    # 同じ記号が付録 B の複数の行（節ごとの表）に現れる場合は、最も前の定義箇所を採る
    first = {}
    entries = []
    for symcell, name, _role, defcell in rows:
        labels = [k.strip() for m in REF.finditer(defcell) for k in m.group(1).split(",")]
        labels = [k for k in labels if k in doc.labels]
        if not labels:
            continue
        dpos = min(doc.def_pos(k) for k in labels)
        for sym in split_symbols(symcell):
            ns = norm(sym)
            if ns not in first or dpos < first[ns][0]:
                first[ns] = (dpos, labels, name, sym)
    seen = set()
    for ns0, (dpos, labels, name, sym0) in first.items():
        for sym in [sym0]:
            ns = norm(sym)
            if len(re.sub(r"\\[a-zA-Z]+|[{}_^]", "", ns)) < 2 and not re.search(r"\\math(bb|cal|frak|sf)", ns):
                skipped.append(sym)
                continue
            checked += 1
            hits = []
            for m in re.finditer(re.escape(ns), ntext):
                p = idx[m.start()]
                if p >= dpos:
                    break
                # 直後が添字・識別子の続きなら別の記号とみなす
                nxt = ntext[m.end():m.end() + 1]
                if nxt.isalpha():
                    continue
                # 添字のない記号は、添字付きの別の記号の一部としては数えない
                if nxt in "_^" and not re.search(r"[_^]", ns):
                    continue
                hits.append(p)
            if hits:
                out.append((sym, name.strip(), labels, dpos, hits))
    PROT = ("definition", "assumption", "proposition", "lemma", "theorem", "proof", "observation", "problem")
    # 1 文字の基礎記号：数式の中のトークンとして照合する
    FONT = re.compile(r"\\(?:math(?:cal|rm|bb|frak|sf|bf|it|scr)|operatorname|text(?:rm|sf|bf|it)?|mathsf)\s*(?:\{[^{}]*\}|[A-Za-z])")
    maths = [(m.start(), FONT.sub(lambda f: " " * len(f.group(0)), m.group(0)))
             for m in re.finditer(r"\$[^$]+\$|\\\[.*?\\\]", doc.text, flags=re.S)]
    base_rows = []
    for ns0, (dpos, labels, name, sym0) in first.items():
        if sym0 not in skipped or sym0 in ("\\ldots", "\\dots", "\\cdots"):
            continue
        tok = re.escape(norm(sym0))
        pat = re.compile(r"(?<![A-Za-z\\])" + tok + r"(?![A-Za-z_^])")
        hp = []
        for st, seg in maths:
            if st >= dpos:
                break
            for m in pat.finditer(seg):
                h = st + m.start()
                e = doc.env_at(h, PROT)
                if e is not None and doc.where(h)[0] not in ("abstract.tex", "section1_intro.tex"):
                    hp.append((h, e))
        if hp:
            base_rows.append((sym0, labels, dpos, hp))

    def in_prot(h):
        e = doc.env_at(h, PROT)
        return e is not None
    L = ["# A. 記号の初出と定義箇所（付録 B による）", "",
         "- 規則：付録 B の各行について、「定義・初出」の列のラベルのうち最も前のもの（定義等の環境はその開始位置、節・小節のラベルはラベルの位置）を定義箇所とし、"
         "その位置より前の本文（要旨・§1〜§9、コメントを除く）に記号の LaTeX 表記（空白を除いて一致）が現れる箇所を列挙する。",
         "- 限界：表記の揺れ（`\\mathrm` と `\\operatorname` など）は拾えない。1 文字の記号（$X$、$f$ など）は A1・A2 の対象外とし、A0 で数式中のトークンとして別に照合する。"
         "§1・要旨での言及は概観としての先行言及でありうるので、§2〜§9 の前方使用と分けて示す。",
         f"- 対象：付録 B の記号 {checked} 個（1 文字の記号 {len(skipped)} 個は対象外）。", ""]
    early = [r for r in out if any(doc.where(h)[0] not in ("abstract.tex", "section1_intro.tex") for h in r[4])]
    intro_only = [r for r in out if r not in early]
    prot_rows = []
    for sym, name, labels, dpos, hits in early:
        hp = [h for h in hits if doc.where(h)[0] not in ("abstract.tex", "section1_intro.tex") and in_prot(h)]
        if hp:
            prot_rows.append((sym, labels, dpos, hp))
    L += [f"## A1. 定義箇所より前に、保護対象の環境（定義・仮定・命題・補題・証明・観察記録・問題）の中で使われる記号：{len(prot_rows)} 個", "",
          "環境の中での前方使用は、その環境の主張が後の定義に依存することを意味しうる（型A・型C の点検対象）。", "",
          "| ID | 記号 | 定義箇所 | 使用した環境（最初の 5 件） | 件数 |", "|---|---|---|---|---|"]
    for sym, labels, dpos, hp in prot_rows:
        envs = []
        for h in hp[:5]:
            e = doc.env_at(h, PROT)
            envs.append(f"{loc(doc, h)}（{KIND_JA[e['kind']]} `{e['label'] or '証明'}`）")
        iid = item(f"A:{norm(sym)}", "A1 記号の前方使用（保護対象の環境）", loc(doc, hp[0]), f"`{sym}` の定義箇所 {', '.join(labels)} より前の使用 {len(hp)} 件",
                   deps=[h for h in hp] + labels)
        L.append(f"| {iid} | `{esc(sym)}` | {loc(doc, dpos)}（{', '.join(labels)}） | {'; '.join(envs)} | {len(hp)} |")
    L += ["", f"## A0. 1 文字の基礎記号の前方使用（保護対象の環境の中、数式中のトークンとして照合）：{len(base_rows)} 個", "",
          "A1 では対象外とした 1 文字の記号（$X$・$U$・$E$・$f$・$K$・$\\Pi$・$M$ など）を、数式の中で前後が識別子でないトークンとして照合する。"
          "添字・上付きの付いた別の記号（$K_{\\mathrm{req}}$ など）は数えない。", "",
          "| ID | 記号 | 定義箇所 | 使用した環境（最初の 5 件） | 件数 |", "|---|---|---|---|---|"]
    for sym, labels, dpos, hp in base_rows:
        envs = [f"{loc(doc, h)}（{KIND_JA[e['kind']]} `{e['label'] or '証明'}`）" for h, e in hp[:5]]
        iid = item(f"A0:{norm(sym)}", "A0 基礎記号の前方使用", loc(doc, hp[0][0]), f"`{sym}` の定義箇所 {', '.join(labels)} より前の使用 {len(hp)} 件",
                   deps=[h for h, _ in hp] + labels)
        L.append(f"| {iid} | `{esc(sym)}` | {loc(doc, dpos)}（{', '.join(labels)}） | {'; '.join(envs)} | {len(hp)} |")
    L += ["", f"## A2. §2〜§9 の地の文・備考で定義箇所より前に使われる記号：{len(early)} 個（A1 を含む）", "",
          "節・小節の冒頭の「本小節で新たに用いる記号は…」の予告や、後の節への言及が多く含まれる。", "",
          "| 記号 | 名称 | 定義箇所 | 定義より前の使用（§2〜§9、最初の 5 件） | 件数 |", "|---|---|---|---|---|"]
    for sym, name, labels, dpos, hits in early:
        hs = [h for h in hits if doc.where(h)[0] not in ("abstract.tex", "section1_intro.tex")]
        L.append(f"| `{esc(sym)}` | {esc(name)} | {loc(doc, dpos)}（{', '.join(labels)}） | "
                 f"{'; '.join(loc(doc, h) for h in hs[:5])} | {len(hs)} |")
    L += ["", f"## A3. 要旨・§1 でだけ先行して言及される記号：{len(intro_only)} 個", "",
          "| 記号 | 定義箇所 | 先行言及（最初の 3 件） |", "|---|---|---|"]
    for sym, name, labels, dpos, hits in intro_only:
        L.append(f"| `{esc(sym)}` | {loc(doc, dpos)} | {'; '.join(loc(doc, h) for h in hits[:3])} |")
    return L, {"A_checked": checked, "A_in_protected_env": len(prot_rows), "A0_base_symbols_checked": len(skipped), "A0_base_forward": len(base_rows), "A_early_any": len(early), "A_intro_only": len(intro_only)}


# ---------------------------------------------------------------- B, C
def statement_blocks(doc):
    """命題・補題・定理・定義・仮定・観察記録・問題・備考ごとに、本文（命題・補題・定理は直後の証明を含む）を返す。"""
    blocks = []
    envs = [e for e in doc.envs if e["kind"] != "proof"]
    proofs = [e for e in doc.envs if e["kind"] == "proof"]
    for e in envs:
        if not e["label"]:
            continue
        body = doc.text[e["begin"]:e["end"]]
        if e["kind"] in ("proposition", "lemma", "theorem"):
            rest = doc.text[e["end"]:]
            m = re.match(r"\s*\\begin\{proof\}", rest)
            if m:
                pr = next((p for p in proofs if p["begin"] >= e["end"]), None)
                if pr:
                    body += doc.text[e["end"]:pr["end"]]
        blocks.append((e, body))
    return blocks


def refs_in(body, label):
    used, excl = [], []
    for sent in body.split("。"):
        keys = [k.strip() for m in REF.finditer(sent) for k in m.group(1).split(",")]
        (excl if any(n in sent for n in NEG) else used).extend(k for k in keys if k != label)
    return used, excl


ROLE_SCOPE = re.compile(r"範囲を限定|適用する\s*ACS\s*の範囲|命題の前提としては用いない|対象から除く|対象から除外")


def role_sentences(doc, e):
    body = doc.text[e["begin"]:e["end"]]
    out = []
    for sent in body.split("。"):
        t = re.sub(r"\s+", " ", sent).strip()
        if "本仮定は" in t or "依拠箇所" in t or "役割" in t or "命題の前提" in t or "対象から除" in t:
            out.append(t[-200:])
    return out


def report_B(doc):
    aenv = {e["label"]: e for e in doc.envs if e["kind"] == "assumption" and e["label"]}
    ass = list(aenv)
    use = {a: defaultdict(list) for a in ass}
    for e, body in statement_blocks(doc):
        used, excl = refs_in(body, e["label"])
        for a in set(used):
            if a in use:
                use[a][e["kind"] if e["kind"] in ("proposition", "lemma", "theorem", "definition") else "other_env"].append(e["label"])
        for a in set(excl):
            if a in use:
                use[a]["excluded"].append(e["label"])
    # 環境の外（地の文）での参照。証明の中の参照は直前の命題・補題に帰属させてあるので地の文に数えない
    for m in REF.finditer(doc.text):
        for k in (x.strip() for x in m.group(1).split(",")):
            if k in use and doc.env_at(m.start(), ENVS) is None:
                use[k]["prose"].append(loc(doc, m.start()))
    rows, counts = [], defaultdict(int)
    for a in ass:
        u = use[a]
        pl = sorted(set(u["proposition"] + u["lemma"] + u["theorem"]))
        roles = role_sentences(doc, aenv[a])
        if pl:
            role = "証明前提"
        elif any(ROLE_SCOPE.search(r) for r in roles):
            role = "適用対象の限定（本文に明記）"
        elif u["definition"]:
            role = "型・整形式性（定義から参照）"
        elif any("依拠箇所" in r for r in roles):
            role = "依拠箇所を節単位で明記"
        else:
            role = "その他（役割を要確認）"
        counts[role] += 1
        rows.append((a, u, pl, role, roles))
    L = ["# B. 仮定の使用と役割", "",
         "- 規則：仮定ごとに、命題・補題・定理（直後の証明を含む）、定義、その他の環境（備考・観察記録・問題・仮定）、"
         "環境の外の地の文からの `\\ref` を数える。「用いない」「用いず」「使わない」を含む文の中の参照は「不使用の言及」に分ける。",
         "- 役割の分類（機械的）：命題・補題・定理（証明を含む）から参照される → **証明前提**。"
         "参照されず、仮定自身の本文に「範囲を限定」「命題の前提としては用いない」等の記載がある → **適用対象の限定（本文に明記）**。"
         "参照されず、定義から参照される → **型・整形式性（定義から参照）**。参照されず、「依拠箇所」で節を示す → **依拠箇所を節単位で明記**。それ以外 → **その他（役割を要確認）**。",
         "- 参照が 0 であることは不使用の証明ではない。また、命題から参照されないことは理論体系で使われないことを意味しない"
         "（適用対象を限定する仮定、定義の型を支える仮定がある）。分類は点検の入口であり、役割の妥当性の判定ではない。", "",
         "| 役割の分類 | 件数 |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in counts.items()]
    L += ["", "| ID | 仮定 | 節 | 役割の分類 | 命題・補題・定理 | 定義 | その他の環境 | 地の文 | 不使用の言及 |", "|---|---|---|---|---|---|---|---|---|"]
    for a, u, pl, role, roles in rows:
        iid = item(f"B:{a}", "B 仮定の役割", loc(doc, aenv[a]["begin"]), f"`{a}`：{role}", deps=[a] + pl)
        L.append(f"| {iid} | `{a}` | {doc.section_of_label(a)} | {role} | {len(pl)}：{' '.join(f'`{x}`' for x in pl[:6])}{' …' if len(pl) > 6 else ''} | "
                 f"{len(set(u['definition']))} | {len(set(u['other_env']))} | {len(u['prose'])} | {len(set(u['excluded']))} |")
    L += ["", "## 仮定自身の本文にある役割の記載（「本仮定は」「依拠箇所」「役割」を含む文）", ""]
    for a, u, pl, role, roles in rows:
        L.append(f"- `{a}`（{role}）")
        for r in roles[:3]:
            L.append(f"  - …{esc(r)}。")
        if not roles:
            L.append("  - （該当する文なし）")
    return L, {"B_assumptions": len(ass), **{f"B_{k}": v for k, v in counts.items()}}


META = re.compile(r"依拠箇所|にだけ用いる|に用いる|ために用いる|用いられる|先取り|後掲|後述|で示す|で扱う|で定める|で導入")


def refs_logical(body, label):
    """論理的な依存とみなす参照。不使用の文と、役割・予告の文（META）の中の参照を除く。"""
    used = []
    for sent in body.split("。"):
        if any(n in sent for n in NEG) or META.search(sent):
            continue
        used.extend(k.strip() for m in REF.finditer(sent) for k in m.group(1).split(",") if k.strip() != label)
    return used


DEFSENT = re.compile(r":=|\\\[|と定め|とおく|と呼ぶ|と書く|\\in\b|\\to\b|\\times|写像|の型|値域|定義域")


def segments(doc):
    """(環境, 部分, 本文) を返す。部分は stmt（主張・定義本体）または proof（直後の証明）。"""
    proofs = [e for e in doc.envs if e["kind"] == "proof"]
    out = []
    for e in doc.envs:
        if e["kind"] == "proof" or not e["label"]:
            continue
        out.append((e, "stmt", doc.text[e["begin"]:e["end"]]))
        if e["kind"] in ("proposition", "lemma", "theorem"):
            if re.match(r"\s*\\begin\{proof\}", doc.text[e["end"]:]):
                pr = next((p for p in proofs if p["begin"] >= e["end"]), None)
                if pr:
                    out.append((e, "proof", doc.text[pr["begin"]:pr["end"]]))
    return out


def classify_edge(src_kind, part, sent, dst):
    if any(n in sent for n in NEG) or META.search(sent):
        return "役割・予告"
    if part == "proof":
        return "証明依存"
    if src_kind in ("proposition", "lemma", "theorem"):
        return "主張の前提"
    if src_kind == "assumption":
        return "仮定の注"
    if src_kind == "definition" and dst.startswith("ass:"):
        return "適用条件"
    if src_kind == "definition":
        return "定義依存" if DEFSENT.search(sent) else "説明参照"
    return "その他"


STRICT = ("証明依存", "主張の前提", "定義依存")


def sccs_of(graph):
    index, low, onst, st, out, cnt = {}, {}, set(), [], [], [0]
    sys.setrecursionlimit(10000)

    def strong(v):
        index[v] = low[v] = cnt[0]
        cnt[0] += 1
        st.append(v)
        onst.add(v)
        for w in graph.get(v, []):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in onst:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = st.pop()
                onst.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1 or v in graph.get(v, []):
                out.append(sorted(comp))

    for v in list(graph):
        if v not in index:
            strong(v)
    return out


def report_C(doc):
    kinds = ("definition", "assumption", "proposition", "lemma", "theorem")
    nodes = {e["label"]: e for e in doc.envs if e["kind"] in kinds and e["label"]}
    edges = defaultdict(list)  # (a,b) -> [(class, sentence)]
    for e, part, body in segments(doc):
        if e["kind"] not in kinds:
            continue
        for sent in body.split("。"):
            for m in REF.finditer(sent):
                for k in (x.strip() for x in m.group(1).split(",")):
                    if k in nodes and k != e["label"]:
                        edges[(e["label"], k)].append((classify_edge(e["kind"], part, sent, k), re.sub(r"\s+", " ", sent.strip())[-160:]))
    ecount = defaultdict(int)
    for v in edges.values():
        for c, _ in v:
            ecount[c] += 1
    strict = defaultdict(list)
    allg = defaultdict(list)
    for (a, b), v in edges.items():
        allg[a].append(b)
        if any(c in STRICT for c, _ in v):
            strict[a].append(b)
    sc_strict = sccs_of(strict)
    sc_all = sccs_of({k: [x for x in vs if not all(c == "役割・予告" for c, _ in edges[(k, x)])] for k, vs in allg.items()})
    L = ["# C. 参照グラフ：辺の種類・循環・後方参照", "",
         "- 節点：定義・仮定・命題・補題・定理。辺：各環境の本文（命題・補題・定理は主張と直後の証明を分ける）の中の `\\ref`。",
         "- 辺の種類（機械的な分類）：",
         "  - **証明依存**：証明の中の参照。",
         "  - **主張の前提**：命題・補題・定理の主張の中の参照。",
         "  - **定義依存**：定義の中で、定義式・型・写像・値域・定義域を述べる文（`:=`、表示数式、「と定め」「とおく」「と呼ぶ」「写像」「値域」等を含む文）の中の参照。",
         "  - **説明参照**：定義の中で、上記に当たらない文の中の参照（関係の説明、区別の注記など）。",
         "  - **適用条件**：定義から仮定への参照。",
         "  - **仮定の注**：仮定の本文の中の参照（依拠箇所・役割の注を含む）。",
         "  - **役割・予告**：「用いない」等の不使用の文、または「依拠箇所」「後掲」「後述」「〜で示す」「〜で扱う」「〜で定める」「〜で導入」「先取り」を含む文の中の参照。",
         "- **厳格グラフ**は証明依存・主張の前提・定義依存の辺だけからなる。論理的な循環の候補は厳格グラフの循環である。"
         "参照グラフ全体（役割・予告だけの辺を除く）の循環は、説明上の相互参照を含むので別に示す。",
         "- 限界：文の分類は語による機械的なもので、定義依存と説明参照の境界は誤りうる。言葉だけの依拠は辺にならない。", "",
         "| 辺の種類 | 件数 |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(ecount.items(), key=lambda x: -x[1])]
    L += ["", f"## C1. 厳格グラフの循環：{len(sc_strict)} 組", ""]
    for c in sc_strict:
        iid = item("C:" + "+".join(c), "C1 厳格グラフの循環", loc(doc, nodes[c[0]]["begin"]), " ↔ ".join(c), deps=c)
        L.append(f"- **{iid}**")
        for a in c:
            for b in c:
                for cl, snt in edges.get((a, b), [])[:2]:
                    L.append(f"  - `{a}` → `{b}`（{cl}）：…{esc(snt)}。")
    if not sc_strict:
        L.append("（なし）")
    L += ["", f"## C2. 参照グラフ全体の循環（役割・予告だけの辺を除く）：{len(sc_all)} 組", "",
          "厳格グラフの循環でないものは、説明参照・適用条件・仮定の注を含む相互参照であり、論理的な循環とは限らない。", ""]
    for c in sc_all:
        iid = item("C2:" + "+".join(c), "C2 参照の循環（説明参照を含む）", loc(doc, nodes[c[0]]["begin"]), " ↔ ".join(c), deps=c)
        L.append(f"- **{iid}**{'（厳格グラフでも循環）' if c in sc_strict else ''}")
        for a in c:
            for b in c:
                for cl, snt in edges.get((a, b), [])[:1]:
                    L.append(f"  - `{a}` → `{b}`（{cl}）：…{esc(snt)}。")
    fwd = []
    for (a, b), v in edges.items():
        cls = sorted(set(c for c, _ in v) - {"役割・予告"})
        if cls and nodes[b]["begin"] > nodes[a]["begin"]:
            fwd.append((a, b, cls))
    fwd.sort(key=lambda r: nodes[r[0]]["begin"])
    L += ["", f"## C3. 後方の環境への参照（役割・予告だけの辺を除く）：{len(fwd)} 件", "",
          "| 参照元 | 位置 | 参照先 | 位置 | 辺の種類 |", "|---|---|---|---|---|"]
    for a, b, cls in fwd:
        L.append(f"| `{a}` | {loc(doc, nodes[a]['begin'])} | `{b}` | {loc(doc, nodes[b]['begin'])} | {'・'.join(cls)} |")
    uniq = {tuple(c) for c in sc_strict} | {tuple(c) for c in sc_all}
    L.insert(L.index(f"## C1. 厳格グラフの循環：{len(sc_strict)} 組"), f"C1・C2 の記録は計 {len(sc_strict) + len(sc_all)} 件、固有の循環候補は {len(uniq)} 組（同じ節点集合が C1 と C2 の両方に現れる場合は 1 組と数える）。\n")
    return L, {"C_nodes": len(nodes), "C_edges": sum(len(v) for v in edges.values()), "C_cycle_records": len(sc_strict) + len(sc_all), "C_cycles_unique": len(uniq), "C_cycles_strict": len(sc_strict),
               "C_cycles_all": len(sc_all), "C_forward": len(fwd)}


# ---------------------------------------------------------------- D
ASSERT = re.compile(r"ならば|したがって|よって|ゆえに|から従う|導かれ|成り立つ|成立する|含意|同値|帰結|一致する|に等しい")
SCOPE = re.compile(r"置かない|主張しない|要求しない|仮定しない|規定しない|含めない|表さない|意味しない|"
                   r"用いない|扱わない|与えない|述べない|定めない|排除しない|限らない|しない。$")
DEFWORD = re.compile(r"呼ぶ|と書く|とおく|とする|読み")
MODAL = re.compile(r"しうる|ありうる|うる。")
NEGMATH = re.compile(r"成立しない|成り立たない|存在しない|含意しない|導かれない|一般には|満たさない|属さない|定まらない|"
                     r"一致しない|等しくない|含まれない|空である|空でない|非空")


def nonproof_units(doc):
    """非証明文の単位：備考、図の説明文、要旨・§1・§9 の地の文。(種類, ラベル, 開始位置, 本文)"""
    out = [("備考", e["label"], e["begin"], doc.text[e["begin"]:e["end"]]) for e in doc.envs if e["kind"] == "remark"]
    for m in re.finditer(r"\\caption\{", doc.text):
        depth, i = 1, m.end()
        while depth and i < len(doc.text):
            depth += {"{": 1, "}": -1}.get(doc.text[i], 0)
            i += 1
        fig = re.search(r"\\label\{(fig:[^}]+)\}", doc.text[i:i + 200])
        out.append(("図の説明文", fig.group(1) if fig else "caption", m.start(), doc.text[m.start():i]))
    for f in ("abstract.tex", "section1_intro.tex", "section9_limitations.tex"):
        st, en = doc.starts[f], doc.starts[f] + len(doc.raw[f])
        segs, cur = [], st
        for e in doc.envs:
            if e["begin"] >= st and e["end"] <= en and e["begin"] >= cur:
                segs.append((cur, e["begin"]))
                cur = e["end"]
        segs.append((cur, en))
        for a_, b_ in segs:
            if doc.text[a_:b_].strip():
                out.append((f"{SEC[f]}の地の文", f, a_, doc.text[a_:b_]))
    return out


def report_D(doc):
    import hashlib
    d1, d2, d3 = [], [], defaultdict(int)
    units = nonproof_units(doc)
    for kind, lab, off, body in units:
        pos = 0
        for sent in re.split(r"(?<=。)", body):
            st = sent.strip()
            p = off + pos
            pos += len(sent)
            if not st:
                continue
            plain = re.sub(r"\s+", " ", st)
            sec = SEC[doc.where(p)[0]]
            if SCOPE.search(plain):
                d3[sec] += 1
                continue
            if REF.search(plain):
                continue
            h = hashlib.md5(plain.encode()).hexdigest()[:8]
            if NEGMATH.search(plain) and not DEFWORD.search(plain):
                d2.append((kind, lab, p, plain, h))
            elif ASSERT.search(plain.rstrip("。")) and not (DEFWORD.search(plain) or MODAL.search(plain) or "ではない" in plain):
                d1.append((kind, lab, p, plain, h))
    by = lambda rows: {sec: sum(1 for r in rows if SEC[doc.where(r[2])[0]] == sec) for sec in ["要旨", "§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9"]}
    b1, b2 = by(d1), by(d2)
    L = ["# D. 非証明文の主張の候補（備考・図の説明文・要旨・§1・§9 の地の文）", "",
         "- 対象：備考環境、図の説明文（`\\caption`）、要旨・§1・§9 の環境の外の地の文。他の節の地の文は対象外（未検査）。",
         "- 各文（「。」で区切る）を次に分ける。`\\ref` を含む文は D1・D2 から除く（参照先との照合は E と第 2 段で行う）。",
         "  - **D3 射程宣言**：「主張しない」「置かない」「要求しない」「仮定しない」「規定しない」「用いない」「扱わない」等を含む文。件数だけを数える（本論文の非主張の書き方 (a) に当たる文で、証明を要しない）。",
         "  - **D2 数学的な否定・非成立の主張**：「成立しない」「存在しない」「含意しない」「導かれない」「一般には」「満たさない」「属さない」「一致しない」「空である」等を含む文（D3 を除く）。"
         "反例・証明を要する主張でありうる（書き方 (b)）。単なる適用範囲の限定との区別を確かめる。",
         "  - **D1 肯定的な断定**：断定の語（ならば・したがって・よって・ゆえに・から従う・導かれ・成り立つ・成立する・含意・同値・帰結・一致する・に等しい）を含み、"
         "定義の語（呼ぶ・とおく・とする）・可能性の語（しうる）・「ではない」を含まない文（D2・D3 を除く）。",
         "- 点検：D1・D2 の各文について、支える定義・命題が本文にあるか（型A）、主張が根拠より強くないか（型E）。直前の文の参照を受ける文は誤検出として含まれる。", "",
         "| 節 | D1 肯定的な断定 | D2 否定・非成立 | D3 射程宣言（件数のみ） |", "|---|---|---|---|"]
    for sec in ["要旨", "§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9"]:
        L.append(f"| {sec} | {b1[sec]} | {b2[sec]} | {d3.get(sec, 0)} |")
    for title, rows, tag in [("D2. 数学的な否定・非成立の主張の候補", d2, "D2"), ("D1. 肯定的な断定の候補", d1, "D1")]:
        L += ["", f"## {title}：{len(rows)} 文", "", "| ID | 種類 | 単位 | 位置 | 文 |", "|---|---|---|---|---|"]
        dseen = Counter()
        for kind, lab, p, plain, h in rows:
            dkey = f"{tag}:{lab}:{h}"
            dseen[dkey] += 1
            if dseen[dkey] > 1:
                dkey += f"#{dseen[dkey]}"  # 同じ単位に同じ文が複数ある場合の識別
            iid = item(dkey, {"D1": "D1 非証明文の肯定的な断定", "D2": "D2 非証明文の否定・非成立の主張"}[tag], loc(doc, p), plain[:80], text=plain)
            L.append(f"| {iid} | {kind} | `{lab}` | {loc(doc, p)} | {esc(plain[:220])}{'…' if len(plain) > 220 else ''} |")
    return L, {"D_units": len(units), "D1_assertions": len(d1), "D2_negative": len(d2), "D3_scope": sum(d3.values())}


# ---------------------------------------------------------------- E
def report_E(doc):
    rows = []
    for m in re.finditer(r"(\\S)?\\(?:eq)?ref\{([^}]*)\}", doc.text):
        src = doc.where(m.start())[0]
        for k in (x.strip() for x in m.group(2).split(",")):
            if k not in doc.labels:
                continue
            dst = doc.where(doc.labels[k])[0]
            if dst != src:
                e = doc.env_at(m.start(), [x for x in ENVS])
                rows.append((SEC[src], SEC[dst], k, m.start(), KIND_JA[e["kind"]] if e else "地の文"))
    pairs = defaultdict(int)
    for s, d, *_ in rows:
        pairs[(s, d)] += 1
    L = ["# E. 節をまたぐ参照", "",
         "- 規則：参照元のファイルと参照先のラベルのファイルが異なる `\\ref`・`\\S\\ref` をすべて列挙する。",
         "- 点検：参照先に、参照元が述べる内容が実際にあるか（型A）。`\\ref` が解決することは内容の確認にならない。",
         f"- 件数 {len(rows)}。", "",
         "## E1. 参照元と参照先の節の組", "", "| 参照元 | 参照先 | 件数 |", "|---|---|---|"]
    for (s, d), n in sorted(pairs.items()):
        L.append(f"| {s} | {d} | {n} |")
    crit = [r for r in rows if r[4] in ("証明", "命題", "補題", "定理", "仮定")]
    bykind = defaultdict(int)
    for r in rows:
        bykind[r[4]] += 1
    L += ["", "## E1b. 参照元の環境の種類", "", "| 種類 | 件数 |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(bykind.items(), key=lambda x: -x[1])]
    seen = defaultdict(int)

    def eid(p, k):
        e = doc.env_at(p, [x for x in ENVS if x != "proof"]) or doc.env_at(p)
        src = (e["label"] if e and e["label"] else None)
        if src is None:
            # 証明は直前の命題・補題に帰属させる
            prev = [x for x in doc.envs if x["kind"] in ("proposition", "lemma", "theorem") and x["end"] <= p]
            src = (prev[-1]["label"] + "/proof") if prev else doc.where(p)[0]
        key = f"E:{src}->{k}"
        seen[key] += 1
        return key + (f"#{seen[key]}" if seen[key] > 1 else "")

    L += ["", f"## E1c. 証明・命題・補題・定理・仮定の中の節をまたぐ参照：{len(crit)} 件（優先して内容を照合する）", "",
          "| ID | 参照元の位置 | 参照元の環境 | 参照先 | 参照先の節 |", "|---|---|---|---|---|"]
    for s_, d, k, p, kind in crit:
        iid = item(eid(p, k), "E1c 節をまたぐ参照（証明・命題・仮定）", loc(doc, p), f"{kind} から `{k}`（{d}）", deps=[p, k])
        L.append(f"| {iid} | {loc(doc, p)} | {kind} | `{k}` | {d} |")
    defs = [r for r in rows if r[4] == "定義"]
    L += ["", f"## E1d. 定義の中の節をまたぐ参照：{len(defs)} 件（定義域・値域に関わるものを照合する）", "",
          "| ID | 参照元の位置 | 参照先 | 参照先の節 |", "|---|---|---|---|"]
    for s_, d, k, p, kind in defs:
        iid = item(eid(p, k), "E1d 節をまたぐ参照（定義）", loc(doc, p), f"定義から `{k}`（{d}）", deps=[p, k])
        L.append(f"| {iid} | {loc(doc, p)} | `{k}` | {d} |")
    L += ["", "## E2. 一覧", "", "| 参照元の位置 | 参照元の環境 | 参照先 | 参照先の節 |", "|---|---|---|---|"]
    for s, d, k, p, kind in rows:
        L.append(f"| {loc(doc, p)} | {kind} | `{k}` | {d} |")
    return L, {"E_cross_refs": len(rows), "E_pairs": len(pairs), "E_in_proof_prop_ass": len(crit), "E_in_definitions": len(defs)}


def load_status(path):
    """旧台帳を読む。列：ID・状態・注記・判定者と日付・根拠ハッシュ（旧形式では欠ける）・区分・位置・要旨。"""
    st = {}
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
        head = lines[0].split("\t") if lines else []
        hcol = head.index("根拠ハッシュ") if "根拠ハッシュ" in head else None
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) >= 3:
                h = parts[hcol] if hcol is not None and len(parts) > hcol else ""
                st[parts[0]] = (parts[1], parts[2], parts[3] if len(parts) > 3 else "", h)
    return st


def main(paper, out, status_path=None):
    paper, out = Path(paper), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    status_path = Path(status_path) if status_path else out / "audit_status.tsv"
    old = load_status(status_path)
    doc = Doc(paper)
    stats = {}
    for name, fn in [("A_symbol_first_use", lambda: report_A(doc, paper)), ("B_assumption_use", lambda: report_B(doc)),
                     ("C_dependency_graph", lambda: report_C(doc)), ("D_remark_assertions", lambda: report_D(doc)),
                     ("E_cross_section", lambda: report_E(doc))]:
        L, s = fn()
        stats.update(s)
        (out / f"{name}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # 状態台帳：前回の判定を ID で引き継ぐ。ただし判定の根拠（対象の環境・依存先・文）のハッシュが
    # 変わった場合は、判定を履歴として注記に残し、状態を「要再照合」に戻す。
    # 旧形式の台帳（ハッシュ列なし）からの移行時は、今回のハッシュを判定時の根拠として記録する。
    cur = {iid for iid, *_ in ITEMS}
    T = ["ID\t状態\t注記\t判定者・日付\t根拠ハッシュ\t区分\t位置\t要旨"]
    cnt = defaultdict(int)
    final = {}
    for iid, cat, where, summ in ITEMS:
        h = basis_hash(doc, iid)
        stt, note, who, oh = old.get(iid, ("検出", "", "", ""))
        if oh and oh != h and stt not in ("検出", "要再照合"):
            note = f"［前回：{stt}｜{who}｜根拠 {oh}］{note}"
            stt, who = "要再照合", ""
        final[iid] = stt
        cnt[stt] += 1
        T.append("\t".join([iid, stt, note, who, h, cat, where, summ.replace("\t", " ")]))
    for iid, (stt, note, who, oh) in old.items():
        if iid not in cur:
            T.append("\t".join([iid, stt if stt.startswith("消滅") else "消滅（今回の抽出で検出されない）", note, who, oh, "", "", ""]))
            cnt["消滅"] += 1
    status_path.write_text("\n".join(T) + "\n", encoding="utf-8")
    bycat = defaultdict(lambda: defaultdict(int))
    for iid, cat, where, summ in ITEMS:
        bycat[cat][final[iid]] += 1
    S = ["# 論理確認 第 1 段の要約（自動生成）", "",
         "抽出は候補の発見であり、監査範囲の確定ではない。網羅性は未検証である（下の「抽出の対象外」を参照）。", "",
         "## 候補の件数と状態", "", "| 区分 | 件数 | " + " | ".join(STATUSES) + " |", "|---|---|" + "---|" * len(STATUSES)]
    for cat in sorted(bycat):
        S.append(f"| {cat} | {sum(bycat[cat].values())} | " + " | ".join(str(bycat[cat].get(x, 0)) for x in STATUSES) + " |")
    S += ["", f"状態台帳：`{status_path.name}`（ID・状態・注記・判定者と日付）。状態は {'、'.join(STATUSES)} のいずれか。"
          "判定は台帳の状態列を書き換えて記録する。再実行時、判定の根拠（対象の環境・依存先・文）のハッシュが変わらない限り ID で引き継ぎ、変わった場合は旧判定を注記に残して「要再照合」に戻す。", "",
          "## 抽出器の統計", "", "| 項目 | 値 |", "|---|---|"]
    S += [f"| {k} | {v} |" for k, v in stats.items()]
    S += ["", "## 抽出の対象外（この段では検査していないもの）", "",
          "- 証明の中身（量化・場合分け・端点・仮定の使い方）。第 2 段で 52 件を依存の順に確認する。",
          "- `\\ref` を使わず言葉だけで依拠している箇所（依存の辺にならない）。",
          "- §2〜§8 の環境の外の地の文の主張（D の対象は備考・図の説明文・要旨・§1・§9 の地の文だけ）。",
          "- `\\ref` を含む断定文の内容（参照先に内容があるかは E と第 2 段で照合する）。",
          "- 付録 B に載っていない記号の前方使用、および表記揺れのある記号。",
          "- 定義の整形式性そのもの（型が閉じているか）。A・C・E は入口を示すだけである。"]
    (out / "summary.md").write_text("\n".join(S) + "\n", encoding="utf-8")
    for k, v in stats.items():
        print(f"{k}={v}")
    print("status=" + ", ".join(f"{k}:{v}" for k, v in cnt.items()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
