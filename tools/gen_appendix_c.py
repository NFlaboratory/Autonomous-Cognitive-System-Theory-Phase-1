#!/usr/bin/env python3
# G11b-C：付録 C（定義・命題等の一覧）を本文から生成する。
# 選定：本文（abstract と §1〜§9）の definition・theorem・assumption・proposition・lemma・observation・problem はすべて、
#       remark は本文（abstract と §1〜§9）から参照されているものだけ。付録からの参照は数えない。
# 並び：節ごと、本文の出現順。番号・ページは \ref・\pageref で LaTeX に解決させる。
# 使い方：python3 -I gen_appendix_c.py 作業ディレクトリ 出力ファイル 本文ファイル…（本文の順）
import sys, os, re
d, out = sys.argv[1], sys.argv[2]
BODY = sys.argv[3:]
KIND = {'definition': '定義', 'theorem': '定理', 'assumption': '仮定', 'proposition': '命題',
        'lemma': '補題', 'observation': '観察記録', 'problem': '問題', 'remark': '備考'}
ALL = [k for k in KIND if k != 'remark']
REFCMD = r'\\(?:ref|eqref|pageref|autoref|cref|Cref|nameref|vref)\*?\{([^}]*)\}|\\hyperref\[([^\]]*)\]'

def opt_arg(t, i):
    """t[i] が '[' のとき、波括弧の入れ子を考慮して対応する ']' までの中身と次の位置を返す。"""
    assert t[i] == '['
    depth_b = 0; depth_s = 0; j = i
    while True:
        c = t[j]
        if c == '\\': j += 2; continue
        if c == '{': depth_b += 1
        elif c == '}': depth_b -= 1
        elif c == '[' and depth_b == 0: depth_s += 1
        elif c == ']' and depth_b == 0:
            depth_s -= 1
            if depth_s == 0: return t[i+1:j], j + 1
        j += 1

texts = {}
for f in BODY:
    t = open(os.path.join(d, f), encoding='utf-8').read()
    texts[f] = re.sub(r'(?<!\\)%[^\n]*', '', t)      # コメントを除く

# 参照の数え上げ（本文のみ）
refcount = {}
other_cmds = {}
for f, t in texts.items():
    for m in re.finditer(REFCMD, t):
        for lab in (m.group(1) or m.group(2)).split(','):
            refcount[lab.strip()] = refcount.get(lab.strip(), 0) + 1
    for c in ['autoref', 'cref', 'Cref', 'nameref', 'vref', 'hyperref']:
        other_cmds[c] = other_cmds.get(c, 0) + len(re.findall(r'\\' + c + r'\b', t))

entries = []   # (file, section label, kind, label, title)
envpat = re.compile(r'\\begin\{(' + '|'.join(KIND) + r')\}')
stat = {}
for f, t in texts.items():
    sec = re.search(r'\\section\{([^\n]*)\}\s*\n\\label\{([^}]*)\}', t)
    seclab = (sec.group(1), sec.group(2)) if sec else None
    for m in envpat.finditer(t):
        kind = m.group(1); i = m.end()
        while t[i] in ' \t': i += 1
        title = None
        if t[i] == '[':
            title, i = opt_arg(t, i)
        lm = re.match(r'\s*\\label\{([^}]*)\}', t[i:])
        assert lm, (f, kind, t[m.start():m.start()+120])
        lab = lm.group(1)
        assert title, (f, lab)
        stat.setdefault(kind, [0, 0])[0] += 1
        if kind == 'remark' and refcount.get(lab, 0) == 0:
            continue
        stat[kind][1] += 1
        entries.append((f, seclab, kind, lab, ' '.join(title.split())))

# 書き出し
o = ["""%======================================================================
\\section{定義・命題等の一覧}
\\label{app:index}

本付録は、本文の定義、仮定、命題、補題、観察記録および問題のすべてと、
本文中で参照される備考を、節ごとに本文での出現順に並べた参照用の一覧である。
各項目の内容は本文による。
"""]
cur = None; n = 0
for f, seclab, kind, lab, title in entries:
    if f != cur:
        if cur is not None:
            o.append('\\end{longtable}\n\\endgroup\n')
        cur = f
        head = '要旨' if seclab is None else '%s（\\S\\ref{%s}）' % seclab
        o.append("""
%%----------------------------------------------------------------------
\\subsection*{%s}

\\begingroup
\\small
\\setlength{\\tabcolsep}{4pt}
\\renewcommand{\\arraystretch}{1.12}
\\begin{longtable}{p{2.4cm} p{10.4cm} r}
""" % head)
    o.append('%s~\\ref{%s} & %s & \\pageref{%s} \\\\\n' % (KIND[kind], lab, title, lab))
    n += 1
o.append('\\end{longtable}\n\\endgroup\n')
open(out, 'w', encoding='utf-8', newline='\n').write(''.join(o))
print('entries', n)
print('per-kind (本文の件数, 一覧の件数):', {KIND[k]: v for k, v in stat.items()})
print('参照命令（\\ref・\\eqref・\\pageref 以外）:', other_cmds)
per = {}
for e in entries: per[e[0]] = per.get(e[0], 0) + 1
print('per-file:', per)
