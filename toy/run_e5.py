# -*- coding: utf-8 -*-
"""E5: classifications of the standard viability formulation set beside the ACS classifications, on the same
finite models and the same closed-loop records.  Descriptive only: no hypothesis is tested and nothing is tuned.

Baseline (standard viability formulation with a disturbance e; NOT sets of the paper):
  K                     the constraint set (= SM)
  R_all                 guaranteed kernel: largest subset of K invariant for SOME u against ALL e in E_ext
  O_any                 optimistic kernel: largest subset of K invariant for SOME u and SOME e in E_ext
ACS side (the paper's sets, computed by the common judgment layer):
  Viab_f(K)             E_req-relative robust kernel (exists u, all e in E_req(x))
  B1 / B2               the two kinds of blockage (prop:blockage_dichotomy)
  e not in E_req(x)     the environment-attributed part
  Z3, Recover           full stop of the base functions (not collapse) and recoverability by Upsilon_adm
python3 run_e5.py [outdir]
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acsjudge.judge import Judge, pair_table            # noqa: E402
from acsjudge import trajectory as gtr                  # noqa: E402
from domains import minacs_domain as dm                 # noqa: E402
from domains.furnace import model as fm                 # noqa: E402
from domains.furnace import mind as fd                  # noqa: E402
from e4.adapters import minacs_background, furnace_background, BG_LEN   # noqa: E402
from e4.prereg import sweep_points                      # noqa: E402

SEEDS = list(range(11, 61))
T = 60


def kernel(J, quant):
    """largest subset S of K with: exists u, (all | any) e in E_ext: f(x,u,e) in S."""
    S = {x for x in J.XS if J.inK(x)}
    q = all if quant == "all" else any
    changed = True
    while changed:
        changed = False
        for x in list(S):
            if not any(q(J._succ[(x, u, e)] in S for e in J.ES) for u in J.U):
                S.discard(x)
                changed = True
    return S


def fx(x):
    return "".join(str(v) for v in x)


def state_level(J):
    K = {x for x in J.XS if J.inK(x)}
    V = J.viab_core()
    R = kernel(J, "all")
    O = kernel(J, "any")
    resp = J.viab_resp()
    piX = {x for (x, o) in resp}
    pairs = pair_table(J)
    blk = [p for p in pairs if p["blk"]]
    out = {
        "|X|": len(J.XS), "|K|": len(K), "|Viab_f(K)|": len(V), "|R_all|": len(R), "|O_any|": len(O),
        "|pi_X(Viab_resp)|": len(piX),
        "R_all subset Viab": R <= V, "Viab subset O_any": V <= O, "O_any subset K": O <= K,
        "Viab minus R_all": sorted(fx(x) for x in V - R),
        "O_any minus Viab": sorted(fx(x) for x in O - V),
        "K minus O_any": sorted(fx(x) for x in K - O),
        "piX(resp) minus Viab": sorted(fx(x) for x in piX - V),
        "pairs": len(pairs), "blocked pairs": len(blk),
        "blocked pairs with x in K": sum(1 for p in blk if J.inK(p["x"])),
        "B1": sum(p["B1"] for p in blk), "B2": sum(p["B2"] for p in blk),
        "B1 with x in K": sum(1 for p in blk if p["B1"] and J.inK(p["x"])),
        "B2 with x in K": sum(1 for p in blk if p["B2"] and J.inK(p["x"])),
        "pairs x in Viab, e not in E_req(x)": sum(1 for p in pairs if p["x"] in V and not p["e_in_Ereq"]),
        "pairs x in Viab, e not in E_req(x), blocked": sum(1 for p in pairs if p["x"] in V and not p["e_in_Ereq"]
                                                           and p["blk"]),
    }
    return out, K, V, R, O


def trajectory_level(J, mind, runs, sets):
    K, V, R, O = sets
    c = Counter()
    ex = {}
    for (seed, pt, rows) in runs:
        alive = [r for r in rows if not r["Col"]]
        c["runs"] += 1
        c["collapsed runs"] += 1 if len(alive) < len(rows) else 0
        c["alive steps"] += len(alive)
        for k, r in enumerate(alive):
            x = tuple(r["x"])
            inV = r["Viab"]
            inR = x in R
            inO = x in O
            if inV and not inR:
                c["steps x in Viab, not in R_all"] += 1
            if inO and not inV:
                c["steps x in O_any, not in Viab"] += 1
            if not r["inK"]:
                c["steps outside K (alive)"] += 1
            if r["blk"]:
                c["blocked steps"] += 1
                c["blocked B1"] += 1 if r["B1"] else 0
                c["blocked B2"] += 1 if r["B2"] else 0
            if inV and not r["e_in_Ereq"]:
                c["steps x in Viab, e not in E_req"] += 1
            if "Z3" in r["zones"]:
                c["Z3 steps (all base functions stopped, not collapse)"] += 1
                if r["Recover"] not in ("undef",) and "1" in r["Recover"]:
                    c["Z3 steps with Recover by some upsilon"] += 1
                    ex.setdefault("Z3 recoverable", (seed, pt, r["t"], r["x"], r["Recover"]))
            if any(z in r["zones"] for z in ("Z1", "Z2", "Z3", "Z4")) and r["Recover"] != "undef":
                c["pre-collapse-band steps (Z1-Z4)"] += 1
                if "1" in r["Recover"]:
                    c["pre-collapse-band steps with Recover"] += 1
        # K exits followed by an autonomous return to K before any collapse
        k = 0
        while k < len(alive):
            if not alive[k]["inK"]:
                j = k
                while j < len(alive) and not alive[j]["inK"]:
                    j += 1
                c["K-exit episodes"] += 1
                if j < len(alive):
                    c["K-exit episodes ending in autonomous return to K"] += 1
                    ex.setdefault("K exit and return", (seed, pt, alive[k]["t"], alive[j]["t"]))
                k = j
            else:
                k += 1
        if alive and len(alive) < len(rows):
            last = alive[-1]
            c["collapses preceded by blockage at the last alive step"] += 1 if last["blk"] else 0
    return dict(c), ex


def run_domain(name, J, mind, x0, o0, M0, bgfun, sweep, policy=None):
    pts = sweep_points(sweep)
    core, V = J.viab_core(), J.viab_stages()
    H = J.hor(V)
    runs = []
    for s in SEEDS:
        for pt in pts:
            bg = bgfun(s, pt)
            rows = gtr.run(J, mind, bg, T, x0, o0, M0, learn=True, recover=True, policy=policy,
                           core=core, V=V, H=H)
            runs.append((s, pt, rows))
    return runs


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {}
    # MinACS
    Jm = Judge(dm.D)
    sm, K, V, R, O = state_level(Jm)
    runs = run_domain("MinACS", Jm, dm.MIND, dm.X0, dm.O0, dm.M0,
                      lambda s, p: minacs_background(s, BG_LEN, p["cold_len"], p["regrow_period"], p["gift_events"],
                                                     gift_window=T),
                      {"cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]})
    tm, exm = trajectory_level(Jm, dm.MIND, runs, (K, V, R, O))
    res["MinACS"] = {"state_level": sm, "trajectory_level (P-mech)": tm, "examples": exm}
    # Furnace
    Jf = Judge(fm.D)
    sf, K, V, R, O = state_level(Jf)
    runs = run_domain("Furnace", Jf, fd.Mind(), fm.X0, fm.O0, fd.M0,
                      lambda s, p: furnace_background(s, BG_LEN, p["hot_len"], p["deliv_period"], p["draught"]),
                      {"hot_len": [4, 5, 6], "deliv_period": [2, 3, 4], "draught": [1, 2]})
    tf, exf = trajectory_level(Jf, fd.Mind(), runs, (K, V, R, O))
    res["Furnace"] = {"state_level": sf, "trajectory_level (P-mech)": tf, "examples": exf}
    with open(os.path.join(outdir, "e5_summary.json"), "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "outputs", "out_e5"))
