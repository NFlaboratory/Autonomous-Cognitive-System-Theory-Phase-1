# -*- coding: utf-8 -*-
"""Generate the appendix-style tables of E6 (markdown) from the exact computation."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minacs import model as mm                                  # noqa: E402
from minacs.analysis import Model, state_table                  # noqa: E402


def fx(x):
    return f"({x.p},{x.en},{x.tp},{x.s})"


def main(outdir):
    M = Model("base")
    rows, V, core = state_table(M)
    resp = M.viab_resp()
    piX = {x for (x, o) in resp}
    L = []
    L.append("| x=(p,en,tp,s) | Π | K | Crit⁽¹⁾ | U^rob | Viab_f(K) | Hor_f | U^Viab | π_X(Viab^resp) | |E_viab⁽¹⁾| |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        x = r["x"]
        if x.s == 0:
            continue
        L.append(f"| {fx(x)} | {r['Pi']} | {'○' if r['inK'] else '×'} | {'+'.join(r['Crit']) or '—'} | "
                 f"{'+'.join(r['U_rob']) or '∅'} | {'○' if r['Viab'] else '×'} | "
                 f"{'∞' if r['Hor'] == 'inf' else ('—' if r['Hor'] is None else r['Hor'])} | "
                 f"{'+'.join(r['U_viab']) if r['Viab'] else '—'} | {'○' if x in piX else '×'} | {r['E_viab1_n']} |")
    with open(os.path.join(outdir, "state_table_s1.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "out_e6"))
