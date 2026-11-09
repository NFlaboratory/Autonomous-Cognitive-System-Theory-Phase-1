#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_acs.py — ACS理論論文 LaTeX 整合性リンタ（v1）
使い方: python3 check_acs.py [対象ディレクトリ]  (既定: カレント)

検査項目:
  1. ラベル重複（同一 \\label が複数箇所）
  2. 未解決参照（\\ref/\\eqref 先のラベルが集合内に無い）
  3. 孤立ラベル（定義されるが一度も参照されない＝情報提供）
  4. 句読点（全角 ， U+FF0C / ． U+FF0E の残存）
  5. 旧記号の残存（Ω/Θ/Φ_t/χ_fast/O_t/V_t^{(5)}/D_parasitic 等）
  6. 禁止表現（完全/究極/絶対的/必然/自明/明らか 等。決定論的は除外）
  7. Phase 1 違反（確率記号 \\mathbb{E}/\\Pr/期待値的/統計的/平均的）
  8. \\textnormal の使用（全廃方針）
  9. 仮定の採番監査（assumptioninner のラベル出現順）
 10. 引用（.bib 定義キー vs \\cite 使用キー：未定義・未使用）
注意: あくまで静的検査。最終判断は著者。主張の強さ≤証明の強さ。
"""
import re, sys, glob, os, collections

DIRECTORY = sys.argv[1] if len(sys.argv) > 1 else "."
texs = sorted(glob.glob(os.path.join(DIRECTORY, "*.tex")))
bibs = sorted(glob.glob(os.path.join(DIRECTORY, "*.bib")))

def read(f): return open(f, encoding="utf-8").read()
def short(f): return os.path.basename(f)

def src_line(src_map, fname, ln):
    for f, s in src_map.items():
        if short(f) == fname:
            lines = s.splitlines()
            return lines[ln-1] if 0 <= ln-1 < len(lines) else ""
    return ""

# 行番号付きで全 .tex を読む
src = {f: read(f) for f in texs}

def find_all(pat, flags=0):
    """(file, lineno, match) を返す"""
    out = []
    for f, s in src.items():
        for m in re.finditer(pat, s, flags):
            ln = s.count("\n", 0, m.start()) + 1
            out.append((short(f), ln, m))
    return out

print("=" * 70)
print(f"ACS整合性リンタ  対象: {DIRECTORY}  / .tex {len(texs)}件 .bib {len(bibs)}件")
print("=" * 70)

# --- 1. ラベル ---
label_locs = collections.defaultdict(list)
for f, ln, m in find_all(r'\\label\{([^}]*)\}'):
    label_locs[m.group(1)].append((f, ln))
all_labels = set(label_locs)

print("\n[1] ラベル重複")
dups = {k: v for k, v in label_locs.items() if len(v) > 1}
if not dups:
    print(f"  OK（重複なし・総ラベル {len(all_labels)} 件）")
else:
    for k, v in sorted(dups.items()):
        print(f"  DUP {k}: " + ", ".join(f"{f}:{ln}" for f, ln in v))

# --- 2. 参照 ---
ref_locs = collections.defaultdict(list)
for f, ln, m in find_all(r'\\(?:ref|eqref|autoref|cref|Cref)\{([^}]*)\}'):
    for key in m.group(1).split(","):
        ref_locs[key.strip()].append((f, ln))
all_refs = set(ref_locs)

print("\n[2] 未解決参照（集合内にラベル定義が無い）")
unresolved = sorted(all_refs - all_labels)
if not unresolved:
    print("  OK（すべて解決）")
else:
    print("  ※ 他セクション（§2/§5/§7 等）が対象外の場合はここに出る。")
    print("     全セクションを同一ディレクトリに揃えると本物の欠落だけが残る。")
    for k in unresolved:
        locs = ", ".join(f"{f}:{ln}" for f, ln in ref_locs[k][:4])
        print(f"  ??? {k}  ← {locs}")

# --- 3. 孤立ラベル ---
print("\n[3] 孤立ラベル（定義のみ・未参照／情報提供）")
orphans = sorted(all_labels - all_refs)
# 章節ラベルは未参照でも正常なことが多い
sec_like = [o for o in orphans if o.startswith(("sec:", "subsec:", "subsubsec:"))]
other = [o for o in orphans if o not in sec_like]
print(f"  章節系 {len(sec_like)}件 / その他 {len(other)}件")
for o in other:
    print(f"    - {o}  ({label_locs[o][0][0]}:{label_locs[o][0][1]})")

# --- 4. 句読点 ---
print("\n[4] 句読点（全角 ，／．の残存）")
bad_punct = find_all(r'[\uFF0C\uFF0E]')
if not bad_punct:
    print("  OK（残存なし）")
else:
    for f, ln, m in bad_punct[:40]:
        print(f"  {f}:{ln}  '{m.group(0)}'")
    if len(bad_punct) > 40: print(f"  …他 {len(bad_punct)-40} 件")

# --- 5. 旧記号 ---
print("\n[5] 旧記号の残存")
old_syms = {
    r'\\Omega(?![a-zA-Z])': "Ω→X",
    r'\\Theta(?![a-zA-Z])': "Θ→K",
    r'\\chi_\{\\mathrm\{fast\}\}': "χ_fast→on_t^cfi",
    r'\\Phi_t(?![a-zA-Z])': "Φ_t→χ_EI(t)",
    r'O_t(?![a-zA-Z])': "O_t→x_t（文脈確認）",
    r'V_t\^\{\(5\)\}': "V_t^{(5)}→V_t^{(S5)}",
    r'B_t(?![a-zA-Z])': "B_t→β_t（文脈確認）",
    r'D_\{?\\mathrm\{parasitic\}\}?|D_parasitic': "D_parasitic 廃止",
    r'寄生的縮退|parasitic degeneration|寄生中心性': "寄生中心性撤廃",
    r'def:viability_margin': "def:viability_margin→def:Pi",
    r'sec:principles(?!_)': "sec:principles→sec:three_principles",
}
any_old = False
for pat, msg in old_syms.items():
    hits = [(f, ln) for f, ln, m in find_all(pat)
            if "% " not in src_line(src, f, ln)]  # コメント行は除外（後述）
    if hits:
        any_old = True
        print(f"  [{msg}] {len(hits)}件: " + ", ".join(f"{f}:{ln}" for f, ln in hits[:6]))
if not any_old:
    print("  OK（本文に旧記号なし／コメント内は除外）")

# --- 6. 禁止表現 ---
print("\n[6] 禁止表現（査読方針）")
banned = ["完全", "究極", "完璧", "絶対的", "必然", "自明", "明らか",
          "よく知られ", "革命的", "我々は達成", "初めて示し"]
# 「決定論的」は許容（誤検出回避）
hit6 = collections.defaultdict(list)
for f, s in src.items():
    for w in banned:
        for m in re.finditer(w, s):
            ln = s.count("\n", 0, m.start()) + 1
            line = s.splitlines()[ln-1] if ln-1 < len(s.splitlines()) else ""
            if w == "完全" and "不完全" in line: continue
            if "決定論的" in line and w in ("必然",): pass
            hit6[w].append((short(f), ln))
if not any(hit6.values()):
    print("  OK（検出なし）")
else:
    for w, v in hit6.items():
        if v: print(f"  「{w}」{len(v)}件: " + ", ".join(f"{f}:{ln}" for f, ln in v[:6]))

# --- 7. Phase 1 違反 ---
print("\n[7] Phase 1 違反（確率記号・統計語）")
phase1 = [r'\\mathbb\{E\}', r'\\Pr(?![a-zA-Z])', r'\\mathbb\{P\}',
          r'期待値的', r'統計的', r'平均的']
hit7 = False
for pat in phase1:
    hits = find_all(pat)
    if hits:
        hit7 = True
        print(f"  [{pat}] " + ", ".join(f"{f}:{ln}" for f, ln, m in hits[:6]))
if not hit7:
    print("  OK（検出なし）")

# --- 8. \textnormal ---
print("\n[8] \\textnormal 使用（全廃方針）")
tn = find_all(r'\\textnormal')
print("  OK（なし）" if not tn else
      "  " + ", ".join(f"{f}:{ln}" for f, ln, m in tn[:20]))

# --- 9. 仮定採番 ---
print("\n[9] 仮定（assumptioninner）の出現順")
asm = find_all(r'\\begin\{assumptioninner\}.*?\\label\{([^}]*)\}', re.S)
# 簡易: ファイル順・行順でラベルを列挙
asm_seq = []
for f in texs:
    s = src[f]
    for m in re.finditer(r'\\begin\{assumptioninner\}', s):
        tail = s[m.start():m.start()+400]
        lm = re.search(r'\\label\{([^}]*)\}', tail)
        if lm: asm_seq.append((short(f), lm.group(1)))
if asm_seq:
    for f, lab in asm_seq:
        print(f"    {f}: {lab}")
else:
    print("  （assumptioninner なし）")

# --- 10. 引用 ---
print("\n[10] 引用（.bib vs \\cite）")
bib_keys = set()
for b in bibs:
    for m in re.finditer(r'@\w+\{([^,]+),', read(b)):
        bib_keys.add(m.group(1).strip())
cited = set()
for f, ln, m in find_all(r'\\cite[tp]?\{([^}]*)\}'):
    for k in m.group(1).split(","):
        cited.add(k.strip())
print(f"  .bib 定義キー {len(bib_keys)}件 / 使用キー {len(cited)}件")
undef = sorted(cited - bib_keys)
unused = sorted(bib_keys - cited)
print("  未定義の引用（要 .bib 追加）: " + (", ".join(undef) if undef else "なし"))
print("  未使用キー（エラーにはならない）: " + (", ".join(unused) if unused else "なし"))

print("\n" + "=" * 70)
print("完了。?? や DUP が出た箇所を確認。全セクションを揃えると未解決参照が激減する。")
print("=" * 70)
