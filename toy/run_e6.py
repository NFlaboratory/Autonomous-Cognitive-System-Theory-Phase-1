# -*- coding: utf-8 -*-
"""E6: MinACS — exact, exhaustive computation and checks.  python3 run_e6.py [outdir]"""
import csv
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minacs import model as mm                       # noqa: E402
from minacs import mind as md                        # noqa: E402
from minacs.analysis import Model, state_table, pair_table   # noqa: E402
from minacs import trajectory as tr                  # noqa: E402


def fx(x):
    return "".join(str(v) for v in x)                # p en tp s


def fe(e):
    return f"c{e.c}g{e.g}ρ{e.rho}r{e.r}"


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    M = Model("base")
    rows, V, core = state_table(M)
    pairs = pair_table(M)
    resp = M.viab_resp()
    allk = M.robust_all_e_kernel()
    lines = []

    def chk(name, ok, detail=""):
        lines.append(f"[EXACT] {'OK ' if ok else 'NG '} {name}" + (f" -- {detail}" if detail else ""))

    WF = lambda x: x.s
    # ------------------------------------------------------------ CR-1 (exact over the finite model)
    cr1 = M.CR1(WF)
    for n in M.ETA:
        r = cr1[n]
        chk(f"CR-1a(i) eta_{n}: witness of a WF=1 state with eta=1 followed by eta=0 forever", r["i"] is not None,
            f"x_t0-1={fx(r['i'][0])}, u={r['i'][1]}, e={fe(r['i'][2])}, x_t0={fx(r['i'][3])}" if r["i"] else "")
        chk(f"CR-1c eta_{n}: witness with x_t0 in D_eta", r["c"] is not None,
            f"x_t0={fx(r['c'][3])}" if r["c"] else "")
        chk(f"CR-1a(ii) eta_{n}: every infinite eta=0 sequence reaches WF=0 and stays (no WF=1 cycle; WF=0 absorbing)",
            r["ii"], f"cycle among WF=1 nodes: {r['ii_cycle_found']}; WF=0 absorbing: {r['ii_wf0_absorbing']}")
    chk("CR-1b joint satisfiability", cr1["b"] is not None, f"x={fx(cr1['b'][0])}, e={fe(cr1['b'][1])}")
    # ------------------------------------------------------------ (SC-2), (FT-2) toy rules
    sc2 = all(M._succ[(x, u, e)].s == 0 for x in M.XS if x.s == 0 for u in M.U for e in M.ES) and \
        all(mm.upsilon(x, a).s == 0 for x in M.XS if x.s == 0 for a in mm.UPSILON)
    chk("(SC-2) toy rule: s=0 invariant under every (u,e) and every upsilon", sc2)
    ft_rec = all(mm.base_active(mm.upsilon(x, "inject")) for x in M.XS if x.s == 1 and x.en == 0)
    chk("FT rule: (FT-1) with s=1 (en=0) is recoverable by upsilon=inject, so FTS=1 iff s=0 (FT and CS coincide in MinACS)",
        ft_rec)
    # ------------------------------------------------------------ assumptions of sec.2
    chk("ass:f_decomposition f=(+)(f_auto,f_dir), f(x,u_empty,e)=f_auto(x,e)",
        all(mm.f(x, "wait", e) == mm.f_auto(x, e) for x in M.XS for e in M.ES))
    chk("ass:env_input_nondegeneracy", any(M._succ[(x, u, e)] != M._succ[(x, u, e2)]
                                           for x in M.XS for u in M.U for e in M.ES for e2 in M.ES))
    chk("ass:env_viable_nondegeneracy", any(M.A(x, e) != M.A(x, e2) for x in M.XS for e in M.ES for e2 in M.ES))
    chk("ass:viable_realizability", any(M.inK(x) and any(M.A(x, e) for e in M.Ereq(x)) for x in M.XS))
    # ------------------------------------------------------------ propositions, exhaustively over all (x,e)
    crit = {x: M.Crit(x) for x in M.XS}
    Vsets = V
    chk("prop:blockage_dichotomy (exactly one of B1, B2 whenever A=empty; B1 => A=empty)",
        all((p["B1"] != p["B2"]) for p in pairs if p["blk"]) and all(p["blk"] for p in pairs if p["B1"]),
        f"{sum(p['blk'] for p in pairs)} blocked pairs of {len(pairs)}")
    chk("prop:eu_blockage (i) (x in Crit_eta and eta=0 => A=empty)",
        all(not M.A(x, e) for x in M.XS for n in crit[x] for e in M.ES if M.ETA[n](x, e) == 0))
    chk("prop:eu_sm_next (antecedent => f(x,u,e) not in K for every u)",
        all(not M.inK(M._succ[(x, u, e)]) for x in M.XS for n in crit[x] for e in M.ES if M.ETA[n](x, e) == 0
            for u in M.U))
    chk("prop:eu_fire_domain (Crit_eta subset of D_eta)",
        all(x in M.D_eta(n) for x in M.XS for n in crit[x]))
    chk("prop:fr_mu_eff (i) (A=empty <=> mu_eff=0)", all(p["blk"] == (p["mu_eff"] == 0) for p in pairs))
    chk("prop:viab_stage_fr (x in V^(nu), nu>=1, e in E_req(x) => (x,e) in D_FR and A nonempty)",
        all(M.D_FR(x, e, crit[x]) and M.A(x, e) for x in Vsets[1] for e in M.Ereq(x)))
    chk("prop:selection_responsibility (u not in A => f not in K)",
        all(not M.inK(M._succ[(x, u, e)]) for x in M.XS for e in M.ES for u in M.U if u not in M.A(x, e)))
    chk("prop:blockage_viability_kernel (e in E_req(x) and A=empty => x not in Viab_f(K))",
        all(p["x"] not in core for p in pairs if p["blk"] and p["e_in_Ereq"]))
    chk("prop:viab_stage_nested (V^(nu+1) subset of V^(nu))", all(Vsets[k + 1] <= Vsets[k] for k in range(len(Vsets) - 1)))
    chk("prop:viab_stage_core (Viab_f(K) subset of every V^(nu); equals the stabilised stage in this finite model)",
        all(core <= Vk for Vk in Vsets) and core == Vsets[-1])
    chk("prop:viab_core_max (Viab_f(K) is E_req-invariant)",
        all(any(all(M._succ[(x, u, e)] in core for e in M.Ereq(x)) for u in M.U) for x in core))
    chk("prop:robust_nonresponse_viab (U_rob=empty => not in Viab and not in V^(nu), nu>=1)",
        all(x not in core and all(x not in Vk for Vk in Vsets[1:]) for x in M.XS if not M.U_rob(x)))
    chk("prop:kernel_maintenance one-step form (x in Viab, u in U^Viab(x), e in E_req(x) => f in Viab and A nonempty)",
        all(M._succ[(x, u, e)] in core and M.A(x, e) for x in core for u in M.U_viab(x, core) for e in M.Ereq(x)))
    chk("prop:viab_resp_max (Viab^resp is invariant with response)", _resp_invariant(M, resp))
    # ------------------------------------------------------------ robust non-inclusion in this model
    piX = {x for (x, o) in resp}
    d1 = sorted(core - piX)
    d2 = sorted(piX - core)
    lines.append(f"[EXACT] info prop:robust_noninclusion in MinACS: Viab\\piX(Viab^resp) = {[fx(x) for x in d1]}; "
                 f"piX(Viab^resp)\\Viab = {[fx(x) for x in d2]}")
    # ------------------------------------------------------------ CR-2 witnesses (mechanism)
    M0 = md.M_(0, 1, "none")
    e0 = mm.E_(0, 0, 0, 1)
    e1 = mm.E_(1, 0, 0, 1)
    xa, xb = mm.X_(2, 3, 2, 1), mm.X_(2, 1, 2, 1)
    w1 = md.P_sens(xa, e0) != md.P_sens(xb, e0)
    w2 = md.P_sens(xa, e0) != md.P_sens(xa, e1)
    w3 = md.M1(md.P_sens(xa, e0), M0) != md.M1(md.P_sens(xa, e1), M0)
    xin, xout = mm.X_(2, 3, 2, 1), mm.X_(2, 3, 0, 1)
    v_in = md.M2(*md.M1(md.P_sens(xin, e0), M0), M0)
    v_out = md.M2(*md.M1(md.P_sens(xout, e0), M0), M0)
    w4 = M.inK(xin) and not M.inK(xout) and (v_in[0] >= 0) != (v_out[0] >= 0)
    w5 = len({md.operate(M0, x, e0)["u"] for x in M.XS if x.s == 1}) >= 2
    for nm, ok in (("CR-2b(i) sensing: fixed e, x differs -> I differs", w1),
                   ("CR-2b(i) sensing: fixed x, e differs -> I differs", w2),
                   ("CR-2b(ii) discrimination: e differs -> internal representation differs", w3),
                   ("CR-2b(iii) valuation, feasibility sensitivity: x in K vs not in K -> Pi_eval sign differs", w4),
                   ("CR-2b(iv) action: response differs across representations", w5)):
        lines.append(f"[WITNESS] {'OK ' if ok else 'NG '} {nm}")
    # ------------------------------------------------------------ principle predicates: realised combinations
    combo = Counter()
    for p in pairs:
        x, e = p["x"], p["e"]
        if x.s == 0:
            continue                              # T_P = {s=1} exactly in MinACS (FTS iff s=0)
        sm = M.inK(x)
        eu = p["D_FR"]
        fr = (not p["blk"]) if eu else None
        combo[(sm, eu, fr)] += 1
    # ------------------------------------------------------------ degenerate variants (7-tuple components)
    variants = [Model("base")]
    variants.append(Model("E=empty (no required factor)", ETA={}))
    variants.append(Model("U={u_empty}", U=("wait",)))
    variants.append(Model("f ignores e (e fixed to c0g0rho0r1)", f=lambda x, u, e: mm.f(x, u, mm.E_(0, 0, 0, 1))))
    variants.append(Model("Pi without the temperature threshold", Pi=lambda x: min(x.en - 1, x.s - 1)))
    vrows = []
    for Vm in variants:
        try:
            cr = Vm.CR1(WF) if Vm.ETA else None
        except Exception as ex:                   # noqa: BLE001
            cr = None
        cr_ok = (cr is not None and all(cr[n]["i"] and cr[n]["c"] and cr[n]["ii"] for n in Vm.ETA) and cr["b"] is not None)
        pr = pair_table(Vm)
        cv = Vm.viab_core()
        vrows.append({"variant": Vm.name, "|K|": sum(Vm.inK(x) for x in Vm.XS), "|K_req|": len(Vm.K_req()),
                      "|Viab_f(K)|": len(cv), "|all-e robust kernel|": len(Vm.robust_all_e_kernel()),
                      "blocked pairs": sum(p["blk"] for p in pr), "B1": sum(p["B1"] for p in pr),
                      "B2": sum(p["B2"] for p in pr), "max mu_eff": max(p["mu_eff"] for p in pr),
                      "EC states": sum(Vm.EC(x) for x in Vm.XS),
                      "CR-1": ("E empty: not an ACS (E nonempty required)" if not Vm.ETA else ("OK" if cr_ok else "fails"))})
    # ------------------------------------------------------------ trajectories (closed loop, exact judgement)
    trajs = {}
    for bname in ("mild", "cold", "famine"):
        trajs[(bname, "learn")] = tr.run(M, bname, learn=True)
        trajs[(bname, "no-learn")] = tr.run(M, bname, learn=False)
    secs = round(time.time() - t0, 2)
    # ------------------------------------------------------------ outputs
    with open(os.path.join(outdir, "state_table.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x(p,en,tp,s)", "Pi", "inK", "|E_req(x)|", "D_heat", "D_food", "Crit", "U_rob", "EC",
                    "Viab_f(K)", "Hor_f", "U_Viab", "|E_viab1(x)|", "in pi_X(Viab_resp)", "in all-e kernel"])
        for r in rows:
            x = r["x"]
            w.writerow([fx(x), r["Pi"], int(r["inK"]), r["Ereq_n"], int(r["D_heat"]), int(r["D_food"]),
                        "+".join(r["Crit"]), "+".join(r["U_rob"]), int(r["EC"]), int(r["Viab"]), r["Hor"],
                        "+".join(r["U_viab"]) if r["Viab"] else "", r["E_viab1_n"], int(x in piX), int(x in allk)])
    with open(os.path.join(outdir, "pair_table.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x", "e", "A", "blocked", "e_in_E_req", "D_FR", "B1", "B2", "mu_eff", "weak_point"])
        for p in pairs:
            w.writerow([fx(p["x"]), fe(p["e"]), "+".join(p["A"]), int(p["blk"]), int(p["e_in_Ereq"]), int(p["D_FR"]),
                        int(p["B1"]), int(p["B2"]), p["mu_eff"], int(p["weak"])])
    for (bname, mode), tr_rows in trajs.items():
        with open(os.path.join(outdir, f"traj_{bname}_{mode}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            ks = list(tr_rows[0].keys())
            w.writerow(ks)
            for r in tr_rows:
                w.writerow([json.dumps(r[k], ensure_ascii=False) if isinstance(r[k], (tuple, list)) else r[k] for k in ks])
    with open(os.path.join(outdir, "checks.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    summary = {
        "seconds": secs, "|X|": len(M.XS), "|U|": len(M.U), "|E_ext|": len(M.ES), "|M|": len(md.MS),
        "|K|": sum(M.inK(x) for x in M.XS), "|D_req|": len(M.D_req()), "|K_req|": len(M.K_req()),
        "stages |V^(nu)|": [len(v) for v in V], "|Viab_f(K)|": len(core), "|Viab^resp| (pairs)": len(resp),
        "|pi_X(Viab^resp)|": len(piX), "|all-e robust kernel|": len(allk),
        "Viab minus piX(resp)": [fx(x) for x in d1], "piX(resp) minus Viab": [fx(x) for x in d2],
        "pairs": len(pairs), "blocked pairs": sum(p["blk"] for p in pairs),
        "B1": sum(p["B1"] for p in pairs), "B2": sum(p["B2"] for p in pairs),
        "mu_eff distribution": dict(Counter(p["mu_eff"] for p in pairs)),
        "Crit distribution": dict(Counter("+".join(M.Crit(x)) or "-" for x in M.XS)),
        "(SM,EU,FR) combinations on T_P (s=1)": {str(k): v for k, v in sorted(combo.items(), key=str)},
        "variants": vrows,
        "checks_NG": sum(1 for ln in lines if " NG " in ln),
        "trajectories": {f"{b}/{m}": _traj_summary(r) for (b, m), r in trajs.items()},
    }
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    print("\n".join(lines))


def _traj_summary(rows):
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    return {"T_col": tcol, "T_blk": next((r["t"] for r in rows if r["blk"] and not r["Col"]), None),
            "blocked steps": sum(1 for r in rows if r["blk"] and not r["Col"]),
            "B1": sum(1 for r in rows if r["B1"] and not r["Col"]), "B2": sum(1 for r in rows if r["B2"] and not r["Col"]),
            "e not in E_req (alive)": sum(1 for r in rows if not r["e_in_Ereq"] and not r["Col"]),
            "in Viab (alive)": sum(1 for r in rows if r["Viab"] and not r["Col"]),
            "u in U^Viab when in Viab": sum(1 for r in rows if r["u_in_Uviab"] is True),
            "u not in U^Viab when in Viab": sum(1 for r in rows if r["u_in_Uviab"] is False)}


def _resp_invariant(M, resp):
    for (x, o) in resp:
        Breq = [(e.c, e.g, e.rho) for e in M.Ereq(x) if e.r == o]
        if not any(all((M._succ[(x, u, mm.E_(b[0], b[1], b[2], o))], M.g_O(o, x, u, b)) in resp for b in Breq)
                   for u in M.U):
            return False
    return True


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "out_e6"))
