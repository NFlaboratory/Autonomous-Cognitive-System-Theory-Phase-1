#!/usr/bin/env python3
"""編集工程（L-A3.69）用：保護対象の環境が編集の前後で変わっていないかを確かめる。
使い方：python3 -I env_guard.py BEFORE_DIR AFTER_DIR
保護対象：definition, assumption, proposition, lemma, theorem, proof, observation, problem
（remark は編集対象なので比較しないが、件数とラベルの増減は報告する）
"""
import sys, re, os, hashlib

PROT = ['definition', 'assumption', 'proposition', 'lemma', 'theorem', 'proof', 'observation', 'problem']
FILES = ['abstract.tex'] + [f'section{i}' for i in range(1, 10)]


def files_in(d):
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith('.tex') and (f == 'abstract.tex' or f.startswith('section')):
            out.append(f)
    return out


def envs(text, kind):
    pat = re.compile(r'\\begin\{' + kind + r'\}(.*?)\\end\{' + kind + r'\}', re.S)
    return [m.group(0) for m in pat.finditer(text)]


def labels(text):
    return re.findall(r'\\label\{([^}]*)\}', text)


def main(a, b):
    bad = 0
    for f in files_in(a):
        ta = open(os.path.join(a, f), encoding='utf-8').read()
        pb = os.path.join(b, f)
        if not os.path.exists(pb):
            print(f'MISSING {f}'); bad += 1; continue
        tb = open(pb, encoding='utf-8').read()
        for k in PROT:
            ea, eb = envs(ta, k), envs(tb, k)
            if ea != eb:
                bad += 1
                print(f'CHANGED {f} {k}: before {len(ea)} after {len(eb)}')
                for i, (x, y) in enumerate(zip(ea, eb)):
                    if x != y:
                        lab = (labels(x) or ['(no label)'])[0]
                        print(f'   first diff at #{i+1} {lab}')
                        break
        ra, rb = envs(ta, 'remark'), envs(tb, 'remark')
        la, lb = set(labels(ta)), set(labels(tb))
        gone, new = sorted(la - lb), sorted(lb - la)
        print(f'{f}: protected envs identical={all(envs(ta,k)==envs(tb,k) for k in PROT)} '
              f'remark {len(ra)}->{len(rb)} labels {len(la)}->{len(lb)}'
              + (f' removed={gone}' if gone else '') + (f' added={new}' if new else ''))
    print('RESULT', 'OK' if bad == 0 else f'NG ({bad})')
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) else 0)
