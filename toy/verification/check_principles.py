# -*- coding: utf-8 -*-
"""G0 + G3: sec.3 statements checked exhaustively on finite domains (MinACS, Furnace, Tightrope).

Every check enumerates the whole finite range stated in the result row.  Sets are computed directly
from (X, U, E_ext, f, Pi, eta, g_O); the existing judge is used only for f/A/Ereq/Crit/mu_eff, which the
first external audit (2026-11-08) reproduced with an independent implementation (0 differences).
The strong assumption ass:theta_exterior_blockage and the corollaries are checked on the product graph
over (x, o) so that the realised environment is consistent with g_O; actions are unrestricted
(every u in U), i.e. the result covers every mechanism attached to the domain.
python3 verification/check_principles.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report, greatest_infinite, backgrounds  # noqa: E402
from acsjudge.judge import Judge                        # noqa: E402
from domains.minacs_domain import D as DM               # noqa: E402
from domains.furnace.model import D as DF               # noqa: E402
from tightrope import D as DT                           # noqa: E402

# Pi = min_k (x_k - theta_k) coordinates (toy conventions of each domain); None: Pi is not of that form
THETA = {"MinACS": {"en": 1, "tp": 1, "s": 1}, "Furnace": {"tp": 1, "s": 1}, "Tightrope": None}


def gfp_inv(J, start, cond_all):
    """largest S within start with: for x in S there is u such that every e in cond_all(x) gives f in S."""
    S = set(start)
    changed = True
    while changed:
        changed = False
        for x in list(S):
            if not any(all(J.f(x, u, e) in S for e in cond_all(x)) for u in J.U):
                S.discard(x)
                changed = True
    return S


def gfp_any(J, start):
    S = set(start)
    changed = True
    while changed:
        changed = False
        for x in list(S):
            if not any(J.f(x, u, e) in S for u in J.U for e in J.ES):
                S.discard(x)
                changed = True
    return S


def run_domain(R, D):
    J = Judge(D)
    nm = D.NAME
    X, U, ES = J.XS, J.U, J.ES
    K = {x for x in X if D.Pi(x) >= 0}
    Ereq = {x: set(J.Ereq(x)) for x in X}
    A = {(x, e): set(J.A(x, e)) for x in X for e in ES}
    Crit = {x: J.Crit(x) for x in X}
    DFR = {(x, e): J.D_FR(x, e, Crit[x]) for x in X for e in ES}
    core = J.viab_core()
    Kreq = {x for x in K if Ereq[x]}
    weak = {(x, e): any(J.N(x, u) for u in A[(x, e)]) for x in X for e in ES}
    mu = {(x, e): J.mu_eff(x, e) for x in X for e in ES}
    Urob = {x: set(J.U_rob(x)) for x in X}

    # P01 prop:sm_K_equiv (i)  (definition consistency of the implementation)
    bad = [x for x in X if (D.Pi(x) >= 0) != J.inK(x)]
    R.check("P01_sm_K_equiv", "prop:sm_K_equiv", nm, len(X), len(X), bad, "Pi(x)>=0 <=> x in K (all x)")
    # P02 prop:sm_one_step_A (i)
    bad = [(x, u, e) for x in X for e in ES for u in U
           if not ((u in A[(x, e)]) == (J.f(x, u, e) in K) == (D.Pi(J.f(x, u, e)) >= 0))]
    R.check("P02_sm_one_step_A", "prop:sm_one_step_A", nm, len(X) * len(ES) * len(U), len(X) * len(ES) * len(U), bad,
            "u in A <=> f in K <=> Pi(f)>=0 (all x,e,u)")
    # P03 prop:fr_one_step ; P04 prop:fr_next_sm
    dpairs = [(x, e) for x in X for e in ES if DFR[(x, e)]]
    bad = [(x, e) for (x, e) in dpairs if (len(A[(x, e)]) > 0) != any(J.f(x, u, e) in K for u in U)]
    R.check("P03_fr_one_step", "prop:fr_one_step", nm, len(X) * len(ES), len(dpairs), bad,
            "on D_FR: FR <=> A nonempty <=> exists u with f in K")
    prem = [(x, e) for (x, e) in dpairs if not A[(x, e)]]
    bad = [(x, e) for (x, e) in prem if any(J.f(x, u, e) in K for u in U)]
    R.check("P04_fr_next_sm", "prop:fr_next_sm", nm, len(X) * len(ES), len(prem), bad,
            "on D_FR with FR false: A empty and x_{t+1} not in K for every u")
    # P05 prop:blockage_dichotomy
    blk = [(x, e) for x in X for e in ES if not A[(x, e)]]
    bad = [(x, e) for (x, e) in blk
           if (any(J.ETA[n](x, e) == 0 for n in Crit[x])) == DFR[(x, e)]]
    R.check("P05_blockage_dichotomy", "prop:blockage_dichotomy", nm, len(X) * len(ES), len(blk), bad,
            "every blockage is exactly one of B1 / B2")
    # P06 prop:viab_core_max : invariant and maximal (independent gfp)
    g = gfp_inv(J, Kreq, lambda x: Ereq[x])
    inv = all(any(all(J.f(x, u, e) in core for e in Ereq[x]) for u in U) for x in core)
    R.check("P06_viab_core_max", "prop:viab_core_max", nm, len(Kreq), len(core),
            [] if (g == core and inv and core <= Kreq) else [("gfp", sorted(map(tuple, g ^ core)))],
            f"|K_req|={len(Kreq)} |Viab|={len(core)}: Viab is E_req-invariant and equals the independent gfp")
    # P07 prop:viab_stage_finite (+ nested)
    V = [set(Kreq)]
    while True:
        nxt = {x for x in Kreq if any(all(J.f(x, u, e) in V[-1] for e in Ereq[x]) for u in U)}
        V.append(nxt)
        if nxt == V[-2]:
            break
    nu_star = len(V) - 2
    nested = all(V[k + 1] <= V[k] for k in range(len(V) - 1))
    hor_ok = all(((x in V[-1]) == (x in core)) for x in Kreq)
    bad = [] if (nu_star <= len(Kreq) and V[-1] == core and nested and hor_ok) else [("nu*", nu_star)]
    R.check("P07_viab_stage_finite", ["prop:viab_stage_finite", "prop:viab_stage_nested"], nm, len(Kreq), len(Kreq),
            bad, f"stages {[len(v) for v in V]}, nu*={nu_star} <= |K_req|={len(Kreq)}; Hor=inf <=> Viab")
    # P08 prop:kernel_standard_comparison
    Vall = gfp_inv(J, K, lambda x: ES)
    Vany = gfp_any(J, K)
    i_ok = all(any(all(J.f(x, u, e) in Vall for e in ES) for u in U) for x in Vall) and \
        all(any(J.f(x, u, e) in Vany for u in U for e in ES) for x in Vany)
    ii_ok = core <= Vany
    Dreq = {x for x in X if Ereq[x]}
    iii_ok = (Vall <= core) == (Vall <= Dreq)
    R.check("P08_kernel_standard_comparison", "prop:kernel_standard_comparison", nm, 1, len(Vall),
            [] if (i_ok and ii_ok and iii_ok) else [(i_ok, ii_ok, iii_ok)],
            f"|Viab_all|={len(Vall)} |Viab|={len(core)} |Viab_any|={len(Vany)}; (iii) non-vacuous only if Viab_all nonempty")
    # P09 prop:robust_nonresponse_viab
    prem = [x for x in X if not Urob[x]]
    bad = [x for x in prem if x in core or any(x in V[k] for k in range(1, len(V)))]
    R.check("P09_robust_nonresponse_viab", "prop:robust_nonresponse_viab", nm, len(X), len(prem), bad,
            "U_rob(x) empty => x not in Viab and not in any stage nu>=1")
    # P10 lem:sd_viab
    prem = [(x, e) for x in X for e in ES if x in K and e in Ereq[x] and A[(x, e)] and mu[(x, e)] == 1 and weak[(x, e)]]
    bad = [(x, e) for (x, e) in prem if Urob[x] or x in core]
    R.check("P10_sd_viab", "lem:sd_viab", nm, len(X) * len(ES), len(prem), bad,
            "x in K, e in E_req, A nonempty, mu_eff=1, weak point => U_rob empty, x not in Viab")
    # P11/P12 nondegeneracy
    a_nd = any(A[(x, e)] != A[(x, e2)] for x in X for e in ES for e2 in ES if e != e2)
    f_nd = any(J.f(x, u, e) != J.f(x, u, e2) for x in X for u in U for e in ES for e2 in ES if e != e2)
    R.check("P11_nondegeneracy_implication", ["prop:nondegeneracy_implication", "ass:env_viable_nondegeneracy",
            "ass:env_input_nondegeneracy"], nm, 1, int(a_nd), [] if (not a_nd or f_nd) else ["A-level without f-level"],
            f"env_viable_nondegeneracy={a_nd}, env_input_nondegeneracy={f_nd}")
    R.check("P12_feasibility_sensitivity_scope", "prop:feasibility_sensitivity_scope", nm, 1, int(a_nd),
            [] if (not a_nd or (K and set(X) - K)) else ["K or X\\K empty"], f"|K|={len(K)}, |X\\K|={len(X) - len(K)}")
    # P13 prop:robust_noninclusion (examples)
    resp = J.viab_resp()
    px = {x for (x, o) in resp}
    w1, w2 = sorted(core - px, key=repr), sorted(px - core, key=repr)
    R.add("P13_robust_noninclusion", "prop:robust_noninclusion", nm, "EXAMPLE_ONLY" if (w1 or w2) else "NOT_APPLICABLE",
          1, None, f"(i) Viab \\ pi_X(resp): {len(w1)}  (ii) pi_X(resp) \\ Viab: {len(w2)}",
          {"i": w1[:3], "ii": w2[:3]}, "example")
    # P14 prop:pi_violation_profile
    th = THETA[nm]
    if th is None:
        R.add("P14_pi_violation_profile", "prop:pi_violation_profile", nm, "NOT_APPLICABLE", None, None,
              "Pi is not of the form min_k(x_k - theta_k) in this domain")
    else:
        bad = []
        for x in X:
            pim = min(getattr(x, k) - t for k, t in th.items())
            Vm = {k for k, t in th.items() if getattr(x, k) < t}
            dm = tuple(max(0, t - getattr(x, k)) for k, t in th.items())
            if pim != D.Pi(x) or ((pim >= 0) != (not Vm)) or ((not Vm) != all(v == 0 for v in dm)) or ((pim < 0) != bool(Vm)):
                bad.append(x)
        R.check("P14_pi_violation_profile", "prop:pi_violation_profile", nm, len(X), len(X), bad,
                f"theta={th}: Pi>=0 <=> V-=empty <=> d-=0 ; Pi<0 <=> V- nonempty")

    # ---------------- G3: strong assumption and the sd chain on the product graph (x, o)
    B = backgrounds(D)
    nodes = [(x, o) for x in X for o in D.OS]
    trans = {}
    for (x, o) in nodes:
        lst = []
        for b in B:
            e = D.make_e(b, o)
            for u in U:
                lst.append((b, e, u, (J.f(x, u, e), D.g_O(o, x, u, b))))
        trans[(x, o)] = lst

    def succ_of(allowed_edge):
        return lambda n: {nx for (b, e, u, nx) in trans[n] if allowed_edge(n, e, u)}

    # P15 ass:theta_exterior_blockage : no infinite path outside Viab without blockage
    out_nodes = [n for n in nodes if n[0] not in core]
    S_ass = greatest_infinite(out_nodes, succ_of(lambda n, e, u: len(A[(n[0], e)]) > 0))
    holds = not S_ass
    wit = None
    if not holds:
        n = sorted(S_ass, key=repr)[0]
        wit = [(n, e, u, nx) for (b, e, u, nx) in trans[n] if A[(n[0], e)] and nx in S_ass][:2]
    R.add("P15_theta_exterior_blockage", "ass:theta_exterior_blockage", nm,
          "PASS_NONVACUOUS" if holds else "BLOCKED_ASSUMPTION", len(out_nodes), len(out_nodes),
          "holds on the domain for every action/environment sequence" if holds else
          f"does NOT hold: {len(S_ass)} (x,o) outside Viab admit an infinite non-blocked path", wit, "graph")
    # P18 prop:exterior_blockage (under the assumption)
    kout = [n for n in nodes if n[0] not in K]
    S_ext = greatest_infinite(kout, succ_of(lambda n, e, u: len(A[(n[0], e)]) > 0))
    if holds:
        R.check("P18_exterior_blockage", "prop:exterior_blockage", nm, len(kout), len(kout),
                sorted(S_ext, key=repr)[:3], "under the assumption: persistence outside K reaches a blockage", "graph")
    else:
        R.add("P18_exterior_blockage", "prop:exterior_blockage", nm, "BLOCKED_ASSUMPTION", len(kout), None,
              f"assumption fails here; infinite non-blocked paths outside K: {len(S_ext)} (x,o)", None, "graph")

    # constraints (a)(b) of prop:sd_robust_nonresponse at the current node
    def ab(n, e, u):
        x = n[0]
        if x in K and e not in Ereq[x]:
            return False
        if x in K and A[(x, e)] and not (mu[(x, e)] == 1 and weak[(x, e)]):
            return False
        return True
    S_ab = greatest_infinite(nodes, succ_of(ab))
    # P16 main proposition
    bad = [n for n in S_ab if n[0] in core or (n[0] in K and Urob[n[0]])]
    R.check("P16_sd_robust_nonresponse", "prop:sd_robust_nonresponse", nm, len(nodes), len(S_ab), bad,
            f"(x,o) admitting an infinite path satisfying (a)(b): {len(S_ab)}; all outside Viab, U_rob empty in K", "graph")
    # P17 corollary prop:sd_necessity
    S_ab_nb = greatest_infinite(S_ab, succ_of(lambda n, e, u: ab(n, e, u) and len(A[(n[0], e)]) > 0))
    if holds:
        R.check("P17_sd_necessity", "prop:sd_necessity", nm, len(S_ab), len(S_ab), sorted(S_ab_nb, key=repr)[:3],
                "under the assumption every (a)(b)-path reaches A=empty in finite time", "graph")
    else:
        ex = None
        if S_ab_nb:
            n = sorted(S_ab_nb, key=repr)[0]
            ex = {"node": n, "edges": [(e, u, nx) for (b, e, u, nx) in trans[n]
                                       if ab(n, e, u) and A[(n[0], e)] and nx in S_ab_nb][:3],
                  "mu_eff": [mu[(n[0], e)] for (b, e, u, nx) in trans[n] if ab(n, e, u) and A[(n[0], e)] and nx in S_ab_nb][:3],
                  "U_rob": sorted(Urob[n[0]]), "in_K": n[0] in K, "in_Viab": n[0] in core}
        R.add("P17_sd_necessity", "prop:sd_necessity", nm, "BLOCKED_ASSUMPTION", len(S_ab), len(S_ab),
              f"assumption fails; (a)(b) hold forever WITHOUT blockage from {len(S_ab_nb)} (x,o) "
              "(the main proposition still holds there; this is not a counterexample to the corollary)", ex, "graph")
    # P19 prop:sd_necessity_fr: classification of every blockage allowed by (a)
    bl = [(x, e) for x in X for e in ES if not A[(x, e)] and (x not in K or e in Ereq[x])]
    bad, ni, nii = [], 0, 0
    for (x, e) in bl:
        b1 = any(J.ETA[n](x, e) == 0 for n in Crit[x])
        b2 = DFR[(x, e)]
        SM, EU = x in K, DFR[(x, e)]
        FR = (len(A[(x, e)]) > 0) if EU else None
        if x not in K:
            ni += 1
            if not ((b1 or b2) and (not SM) and ((not EU) != (EU and FR is False))):
                bad.append((x, e))
        else:
            nii += 1
            if not (b2 and EU and FR is False):
                bad.append((x, e))
    R.check("P19_sd_necessity_fr", "prop:sd_necessity_fr", nm, len(bl), len(bl), bad,
            f"blockages with (a): case (i) x not in K: {ni}, case (ii) x in K: {nii}")
    return J


def main():
    R = Report("principles")
    for D in (DM, DF, DT):
        print(f"--- {D.NAME}")
        run_domain(R, D)
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
