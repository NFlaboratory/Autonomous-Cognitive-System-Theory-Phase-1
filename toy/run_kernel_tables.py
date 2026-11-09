# -*- coding: utf-8 -*-
"""Experiment A (exact part): for every state x of Viab_f(K) in MinACS and in the furnace keeper, one
kernel-maintaining response u in U^Viab(x) and the check that f(x, u, e) stays in Viab_f(K) for every
e in E_req(x).  This is an instance of prop:viab_core_max / prop:kernel_maintenance (already proved), written out
as a finite table: with the selector sigma(x) = the listed u, every trajectory that starts in the kernel and
meets e_s in E_req(x_s) at every step stays in the kernel for all time.
python3 run_kernel_tables.py  -> outputs/kernel_tables/<domain>.csv and summary.md
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acsjudge.judge import Judge                 # noqa: E402
from domains import minacs_domain as dm          # noqa: E402
from domains.furnace import model as fm          # noqa: E402


def table(J):
    core = J.viab_core()
    rows = []
    for x in sorted(core):
        uv = J.U_viab(x, core)
        u = uv[0]
        ok = all(J._succ[(x, u, e)] in core for e in J.Ereq(x))
        rows.append({"x": "".join(str(v) for v in x), "U_Viab": "+".join(uv), "sigma(x)": u,
                     "|E_req(x)|": len(J.Ereq(x)), "checked": ok})
    return core, rows


def main():
    out = os.path.join(HERE, "outputs", "kernel_tables")
    os.makedirs(out, exist_ok=True)
    L = ["# 実験 A：核維持応答の表（全数）", "", "| 領域 | 核の状態数 | 表の行のうち検査が成り立った行 | U^Viab の大きさの範囲 |", "|---|---|---|---|"]
    for name, D in (("MinACS", dm.D), ("Furnace", fm.D)):
        J = Judge(D)
        core, rows = table(J)
        with open(os.path.join(out, name + ".csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        sizes = [len(r["U_Viab"].split("+")) for r in rows]
        L.append(f"| {name} | {len(core)} | {sum(r['checked'] for r in rows)} | {min(sizes)}〜{max(sizes)} |")
    L += ["", "- 各行：核の状態 x、核維持応答集合 U^Viab(x)、選んだ応答 σ(x)（U の順で最初）、|E_req(x)|、"
          "σ(x) のもとですべての e∈E_req(x) について後続が核に入るかの検査。",
          "- これは証明済みの命題（prop:viab_core_max、prop:kernel_maintenance）の有限の例であり、新しい証明ではない。"]
    with open(os.path.join(out, "summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
