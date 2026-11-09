# -*- coding: utf-8 -*-
"""Domain-independent exhaustive checks (the [EXACT] part of E6, with domain references replaced by D)."""
from collections import Counter

from .judge import pair_table


def exact_checks(J):
    D = J.D
    out = []

    def chk(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    WF = D.WF
    cr1 = J.CR1(WF)
    for n in J.ETA:
        r = cr1[n]
        chk(f"CR-1a(i) eta_{n}", r["i"] is not None, str(r["i"]) if r["i"] else "")
        chk(f"CR-1c eta_{n}", r["c"] is not None, str(r["c"][3]) if r["c"] else "")
        chk(f"CR-1a(ii) eta_{n}", r["ii"], f"cycle among WF=1 nodes: {r['ii_cycle_found']}; "
                                           f"WF=0 absorbing: {r['ii_wf0_absorbing']}")
    chk("CR-1b joint satisfiability", cr1["b"] is not None, str(cr1["b"]))
    chk("(SC-2) toy rule: WF=0 invariant under every (u,e) and every upsilon",
        all(WF(J._succ[(x, u, e)]) == 0 for x in J.XS if WF(x) == 0 for u in J.U for e in J.ES) and
        all(WF(D.upsilon(x, a)) == 0 for x in J.XS if WF(x) == 0 for a in D.UPSILON))
    chk("ass:f_decomposition f(x,u_empty,e)=f_auto(x,e)",
        all(J.f(x, D.U_EMPTY, e) == D.f_auto(x, e) for x in J.XS for e in J.ES))
    chk("ass:env_input_nondegeneracy", any(J._succ[(x, u, e)] != J._succ[(x, u, e2)]
                                           for x in J.XS for u in J.U for e in J.ES for e2 in J.ES))
    chk("ass:env_viable_nondegeneracy", any(J.A(x, e) != J.A(x, e2) for x in J.XS for e in J.ES for e2 in J.ES))
    chk("ass:viable_realizability", any(J.inK(x) and any(J.A(x, e) for e in J.Ereq(x)) for x in J.XS))
    pairs = pair_table(J)
    crit = {x: J.Crit(x) for x in J.XS}
    V = J.viab_stages()
    core = J.viab_core()
    chk("prop:blockage_dichotomy", all((p["B1"] != p["B2"]) for p in pairs if p["blk"]) and
        all(p["blk"] for p in pairs if p["B1"]), f"{sum(p['blk'] for p in pairs)} blocked pairs of {len(pairs)}")
    chk("prop:eu_blockage (i)", all(not J.A(x, e) for x in J.XS for n in crit[x] for e in J.ES if J.ETA[n](x, e) == 0))
    chk("prop:eu_sm_next", all(not J.inK(J._succ[(x, u, e)]) for x in J.XS for n in crit[x] for e in J.ES
                               if J.ETA[n](x, e) == 0 for u in J.U))
    chk("prop:eu_fire_domain", all(x in J.D_eta(n) for x in J.XS for n in crit[x]))
    chk("prop:fr_mu_eff (i)", all(p["blk"] == (p["mu_eff"] == 0) for p in pairs))
    chk("prop:viab_stage_fr", all(J.D_FR(x, e, crit[x]) and J.A(x, e) for x in V[1] for e in J.Ereq(x)))
    chk("prop:selection_responsibility", all(not J.inK(J._succ[(x, u, e)]) for x in J.XS for e in J.ES for u in J.U
                                             if u not in J.A(x, e)))
    chk("prop:blockage_viability_kernel", all(p["x"] not in core for p in pairs if p["blk"] and p["e_in_Ereq"]))
    chk("prop:viab_stage_nested", all(V[k + 1] <= V[k] for k in range(len(V) - 1)))
    chk("prop:viab_stage_core", all(core <= Vk for Vk in V) and core == V[-1])
    chk("prop:viab_core_max", all(any(all(J._succ[(x, u, e)] in core for e in J.Ereq(x)) for u in J.U) for x in core))
    chk("prop:robust_nonresponse_viab", all(x not in core and all(x not in Vk for Vk in V[1:])
                                            for x in J.XS if not J.U_rob(x)))
    chk("prop:kernel_maintenance one-step form",
        all(J._succ[(x, u, e)] in core and J.A(x, e) for x in core for u in J.U_viab(x, core) for e in J.Ereq(x)))
    resp = J.viab_resp()
    chk("prop:viab_resp_max", J.resp_invariant(resp))
    return out, pairs, V, core, resp


def summary(J, pairs, V, core, resp):
    piX = {x for (x, o) in resp}
    combo = Counter()
    for p in pairs:
        x = p["x"]
        if J.D.CS(x):
            continue
        eu = p["D_FR"]
        combo[(J.inK(x), eu, (not p["blk"]) if eu else None)] += 1
    return {"|X|": len(J.XS), "|U|": len(J.U), "|E_ext|": len(J.ES), "|K|": sum(J.inK(x) for x in J.XS),
            "|K_req|": len(J.K_req()), "stages |V^(nu)|": [len(v) for v in V], "|Viab_f(K)|": len(core),
            "|Viab^resp| (pairs)": len(resp), "|pi_X(Viab^resp)|": len(piX),
            "|all-e robust kernel|": len(J.robust_all_e_kernel()),
            "Viab minus piX(resp)": len(core - piX), "piX(resp) minus Viab": len(piX - core),
            "pairs": len(pairs), "blocked pairs": sum(p["blk"] for p in pairs),
            "B1": sum(p["B1"] for p in pairs), "B2": sum(p["B2"] for p in pairs),
            "mu_eff distribution": dict(sorted(Counter(p["mu_eff"] for p in pairs).items())),
            "Crit distribution": dict(Counter("+".join(J.Crit(x)) or "-" for x in J.XS)),
            "(SM,EU,FR) combinations (CS=0)": {str(k): v for k, v in sorted(combo.items(), key=str)}}
