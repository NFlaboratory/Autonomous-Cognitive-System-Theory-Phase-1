# -*- coding: utf-8 -*-
"""E8: exhaustive checks of the second domain (furnace keeper) with the common judgment layer, and the
same checks on MinACS.  python3 run_e8_checks.py [outdir]"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acsjudge.judge import Judge                      # noqa: E402
from acsjudge.checks import exact_checks, summary     # noqa: E402
from domains.furnace import model as fm               # noqa: E402
from domains.furnace import mind as fd                # noqa: E402
from domains import minacs_domain as dm               # noqa: E402


def fx(x):
    return "".join(str(v) for v in x)


def cr2_witnesses():
    """CR-2b on the standard-map form.  For (iii) the valuation map M2 o M1 is applied directly to the sensed
    input of a state outside K (tp = 0): in operation the mechanism does not run there (base functions stopped),
    because in this domain K coincides with the set where the base functions are active."""
    md = fd.Mind()
    M0 = fd.M0
    e0, e1 = fm.E_(0, 0, 0, 1), fm.E_(1, 0, 0, 1)
    xa, xb = fm.X_(2, 3, 1), fm.X_(2, 2, 1)
    xin, xout = fm.X_(2, 2, 1), fm.X_(2, 0, 1)
    val = lambda x, e: md.M2(*md.M1(fd.P_sens(x, e), M0), M0)[0]
    return [
        ("CR-2b(i) sensing: fixed e, x differs -> I differs", fd.P_sens(xa, e0) != fd.P_sens(xb, e0)),
        ("CR-2b(i) sensing: fixed x, e differs -> I differs", fd.P_sens(xa, e0) != fd.P_sens(xa, e1)),
        ("CR-2b(ii) discrimination: e differs -> internal representation differs",
         md.M1(fd.P_sens(xa, e0), M0) != md.M1(fd.P_sens(xa, e1), M0)),
        ("CR-2b(iii) valuation non-constant, and x in K vs x not in K -> value differs (map applied directly)",
         len({val(x, e0) for x in fm.XS}) >= 2 and fm.Pi(xin) >= 0 > fm.Pi(xout) and val(xin, e0) != val(xout, e0)),
        ("CR-2b(iv) action: response differs across representations",
         len({md.operate(M0, x, e)["u"] for x in fm.XS if x.s == 1 for e in fm.ES}) >= 2),
    ]


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for name, D in (("furnace", fm.D), ("minacs", dm.D)):
        J = Judge(D)
        ck, pairs, V, core, resp = exact_checks(J)
        lines = [f"[EXACT] {'OK ' if ok else 'NG '} {n}" + (f" -- {d}" if d else "") for n, ok, d in ck]
        if name == "furnace":
            lines += [f"[WITNESS] {'OK ' if ok else 'NG '} {n}" for n, ok in cr2_witnesses()]
            piX = {x for (x, o) in resp}
            lines.append(f"[EXACT] info Viab\\piX(Viab^resp) = {[fx(x) for x in sorted(core - piX)]}; "
                         f"piX(Viab^resp)\\Viab = {[fx(x) for x in sorted(piX - core)]}")
            with open(os.path.join(outdir, "state_table_furnace.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["x(fu,tp,s)", "Pi", "inK", "|E_req(x)|", "Crit", "U_rob", "Viab_f(K)", "Hor_f",
                            "U_Viab", "in pi_X(Viab_resp)", "in all-e kernel"])
                H = J.hor(V)
                allk = J.robust_all_e_kernel()
                for x in J.XS:
                    w.writerow([fx(x), J.Pi(x), int(J.inK(x)), len(J.Ereq(x)), "+".join(J.Crit(x)),
                                "+".join(J.U_rob(x)), int(x in core), H[x],
                                "+".join(J.U_viab(x, core)) if x in core else "", int(x in piX), int(x in allk)])
        with open(os.path.join(outdir, f"checks_{name}.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
        s = summary(J, pairs, V, core, resp)
        s["checks_NG"] = sum(1 for ln in lines if " NG " in ln)
        s["checks_total"] = len(lines) - sum(1 for ln in lines if " info " in ln)
        res[name] = s
        print(name)
        print("\n".join(lines))
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "outputs", "out_e8"))
