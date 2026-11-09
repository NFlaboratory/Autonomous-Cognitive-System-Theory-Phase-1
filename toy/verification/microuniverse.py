# -*- coding: utf-8 -*-
"""G2 + G4: MicroUniverse -- every candidate model on tiny sets, with an implementation that does not
use acsjudge (direct set definitions; maximal invariant sets also by brute force over all subsets).

A candidate model is a PARTIAL MODEL (X, U, E_ext = E_bg x O, f, Pi, eta, g_O).  No mechanism is
attached: CR-2 is not judged and no candidate is called an ACS.  Only sec.3 statements that refer to
these components alone are checked.  A statement is judged only on candidates satisfying its premise;
candidates where the premise never holds are counted separately (vacuous).

Families (fixed before running):
  A2  |X|=2, |U|=2, |E_bg|=2, |O|=1 : all f (2^8), all K (2^2), one factor eta, all eta (2^4) -> 16,384
  A3  |X|=3, |U|=2, |E_bg|=2, |O|=1 : all f (3^12), K = {0,1}, eta in {eta(x,e)=1 iff e=0}     -> 531,441
  B2  |X|=2, |U|=2, |E_bg|=1, |O|=2 : f, g_O, K, eta enumerated until both witnesses of
      prop:robust_noninclusion are found (existence search only)
Pi(x) = 0 on K, -1 outside (a feasibility function whose zero super-level set is K).
python3 verification/microuniverse.py [A2|A3|B2 ...]
"""
import itertools
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report  # noqa: E402


def subsets(s):
    s = sorted(s)
    for r in range(len(s) + 1):
        for c in itertools.combinations(s, r):
            yield frozenset(c)


def analyse(n, nU, nE, F, K, ETA, C, stats, brute=True):
    """F[x][u][e] -> x' ; K frozenset ; ETA[x][e] in {0,1}.  Updates counters C (violations/premises)."""
    X, U, E = range(n), range(nU), range(nE)
    inK = [x in K for x in X]
    Ereq = [tuple(e for e in E if ETA[x][e]) for x in X]
    A = [[tuple(u for u in U if inK[F[x][u][e]]) for e in E] for x in X]
    # Crit (single factor): (i) exists eta=0, (ii) eta=0 => A empty, (iii) exists eta=1 with A nonempty
    crit = [any(ETA[x][e] == 0 for e in E) and all(not A[x][e] for e in E if ETA[x][e] == 0)
            and any(A[x][e] for e in E if ETA[x][e] == 1) for x in X]
    DFR = [[(not crit[x]) or ETA[x][e] == 1 for e in E] for x in X]
    Kreq = frozenset(x for x in X if inK[x] and Ereq[x])

    def inv(S, cond):   # exists u for all e in cond(x)
        return all(any(all(F[x][u][e] in S for e in cond(x)) for u in U) for x in S)

    def gfp(start, cond):
        S = set(start)
        ch = True
        while ch:
            ch = False
            for x in list(S):
                if not any(all(F[x][u][e] in S for e in cond(x)) for u in U):
                    S.discard(x)
                    ch = True
        return frozenset(S)
    core = gfp(Kreq, lambda x: Ereq[x])
    if brute:
        union = frozenset().union(*[S for S in subsets(Kreq) if inv(S, lambda x: Ereq[x])])
        C["viab_core_max"][0] += 1
        C["viab_core_max"][1] += 1
        if union != core or not inv(core, lambda x: Ereq[x]):
            C["viab_core_max"][2].append((F, K, ETA))
    # stages
    V = [Kreq]
    while True:
        nxt = frozenset(x for x in Kreq if any(all(F[x][u][e] in V[-1] for e in Ereq[x]) for u in U))
        V.append(nxt)
        if nxt == V[-2]:
            break
    nu = len(V) - 2
    C["viab_stage_finite"][0] += 1
    C["viab_stage_finite"][1] += 1
    if not (nu <= len(Kreq) and V[-1] == core and all(V[k + 1] <= V[k] for k in range(len(V) - 1))):
        C["viab_stage_finite"][2].append((F, K, ETA))
    stats["nu_star"][nu] += 1
    # all/any kernels
    Vall = gfp(K, lambda x: tuple(E))
    S = set(K)
    ch = True
    while ch:
        ch = False
        for x in list(S):
            if not any(F[x][u][e] in S for u in U for e in E):
                S.discard(x)
                ch = True
    Vany = frozenset(S)
    Dreq = frozenset(x for x in X if Ereq[x])
    c = C["kernel_standard_comparison"]
    c[0] += 1
    if Vall:
        c[1] += 1
    ok = inv(Vall, lambda x: tuple(E)) and all(any(F[x][u][e] in Vany for u in U for e in E) for x in Vany) \
        and core <= Vany and ((Vall <= core) == (Vall <= Dreq))
    if not ok:
        c[2].append((F, K, ETA))
    if Vall and not (Vall <= Dreq):
        stats["Vall_not_in_Dreq"] += 1
    # per (x,e)
    N = [[tuple(e for e in Ereq[x] if not inK[F[x][u][e]]) for u in U] for x in X]
    Urob = [tuple(u for u in U if not N[x][u]) for x in X]
    mu = [[len({tuple(inK[F[x][u][e2]] for e2 in Ereq[x]) for u in A[x][e]}) for e in E] for x in X]
    weak = [[any(N[x][u] for u in A[x][e]) for e in E] for x in X]
    for x in X:
        if not Ereq[x]:
            stats["Ereq_empty_states"] += 1
            if set(Urob[x]) == set(U):
                stats["Ereq_empty_Urob_eq_U"] += 1
        if not crit[x]:
            stats["Crit_empty_states"] += 1
        # forall e exists u vs exists u forall e (in Ereq), one step into K
        if Ereq[x] and all(A[x][e] for e in Ereq[x]) and not Urob[x]:
            stats["forall_e_exists_u_but_no_common_u"] += 1
        c = C["robust_nonresponse_viab"]
        c[0] += 1
        if not Urob[x]:
            c[1] += 1
            if x in core or any(x in V[k] for k in range(1, len(V))):
                c[2].append((F, K, ETA, x))
        for e in E:
            blocked = not A[x][e]
            c = C["blockage_dichotomy"]
            c[0] += 1
            if blocked:
                c[1] += 1
                b1 = crit[x] and ETA[x][e] == 0
                if b1 == DFR[x][e]:
                    c[2].append((F, K, ETA, x, e))
            c = C["fr_next_sm"]
            c[0] += 1
            if DFR[x][e] and blocked:
                c[1] += 1
                if any(inK[F[x][u][e]] for u in U):
                    c[2].append((F, K, ETA, x, e))
            c = C["sd_viab"]
            c[0] += 1
            if inK[x] and e in Ereq[x] and A[x][e] and mu[x][e] == 1 and weak[x][e]:
                c[1] += 1
                if Urob[x] or x in core:
                    c[2].append((F, K, ETA, x, e))
            if A[x][e] and not Urob[x] and inK[x]:
                stats["Urob_empty_with_A_nonempty"] += 1
    # nondegeneracy
    a_nd = any(A[x][e] != A[x][e2] for x in X for e in E for e2 in E if e != e2)
    f_nd = any(F[x][u][e] != F[x][u][e2] for x in X for u in U for e in E for e2 in E if e != e2)
    c = C["nondegeneracy_implication"]
    c[0] += 1
    if a_nd:
        c[1] += 1
        if not f_nd:
            c[2].append((F, K, ETA))
    c = C["feasibility_sensitivity_scope"]
    c[0] += 1
    if a_nd:
        c[1] += 1
        if not (K and len(K) < n):
            c[2].append((F, K, ETA))
    if not K:
        stats["K_empty"] += 1
    if len(K) == n:
        stats["K_eq_X"] += 1
    # lem:finite_exit -- every state-feedback policy pi : K_req -> U
    out = [x for x in Kreq if x not in core]
    c = C["finite_exit"]
    for pi_vals in itertools.product(U, repeat=len(Kreq)):
        pi = dict(zip(sorted(Kreq), pi_vals))
        c[0] += 1
        if not out:
            continue
        c[1] += 1
        attr = set(X) - set(Kreq)        # from here: already outside K_req
        ch = True
        while ch:
            ch = False
            for x in Kreq:
                if x not in attr and any(F[x][pi[x]][e] in attr for e in Ereq[x]):
                    attr.add(x)
                    ch = True
        if any(x not in attr for x in out):
            c[2].append((F, K, ETA, pi))
    # strong assumption and sd chain (O is a single point here)
    def gip(nodes, ok_edge):
        S = set(nodes)
        ch = True
        while ch:
            ch = False
            for x in list(S):
                if not any(F[x][u][e] in S for u in U for e in E if ok_edge(x, e, u)):
                    S.discard(x)
                    ch = True
        return S
    S_ass = gip([x for x in X if x not in core], lambda x, e, u: bool(A[x][e]))
    holds = not S_ass
    stats["assumption_holds" if holds else "assumption_fails"] += 1

    def ab(x, e, u):
        if inK[x] and e not in Ereq[x]:
            return False
        if inK[x] and A[x][e] and not (mu[x][e] == 1 and weak[x][e]):
            return False
        return True
    S_ab = gip(list(X), ab)
    c = C["sd_robust_nonresponse"]
    c[0] += 1
    if S_ab:
        c[1] += 1
        if any(x in core or (inK[x] and Urob[x]) for x in S_ab):
            c[2].append((F, K, ETA))
    S_nb = gip(S_ab, lambda x, e, u: ab(x, e, u) and bool(A[x][e]))
    if holds:
        c = C["sd_necessity"]
        c[0] += 1
        if S_ab:
            c[1] += 1
            if S_nb:
                c[2].append((F, K, ETA))
        c = C["exterior_blockage"]
        c[0] += 1
        kout = [x for x in X if not inK[x]]
        if kout:
            c[1] += 1
            if gip(kout, lambda x, e, u: bool(A[x][e])):
                c[2].append((F, K, ETA))
    elif S_nb:
        stats["assumption_fails_and_ab_forever_without_blockage"] += 1
    # sd_necessity_fr classification of blockages allowed by (a)
    c = C["sd_necessity_fr"]
    for x in X:
        for e in E:
            if A[x][e] or (inK[x] and e not in Ereq[x]):
                continue
            c[0] += 1
            c[1] += 1
            b1 = crit[x] and ETA[x][e] == 0
            b2 = DFR[x][e]
            EU = DFR[x][e]
            if not inK[x]:
                ok = (b1 or b2) and ((not EU) != (EU and True))
            else:
                ok = b2 and EU
            if not ok:
                c[2].append((F, K, ETA, x, e))


def family(name, R):
    C = {k: [0, 0, []] for k in ("viab_core_max", "viab_stage_finite", "kernel_standard_comparison",
                                 "robust_nonresponse_viab", "blockage_dichotomy", "fr_next_sm", "sd_viab",
                                 "nondegeneracy_implication", "feasibility_sensitivity_scope", "finite_exit",
                                 "sd_robust_nonresponse", "sd_necessity", "exterior_blockage", "sd_necessity_fr")}
    stats = Counter()
    stats["nu_star"] = Counter()
    if name == "A2":
        n, nU, nE = 2, 2, 2
        Klist = list(subsets(range(n)))
        etas = [tuple(tuple(bits[x * nE:(x + 1) * nE]) for x in range(n)) for bits in itertools.product((0, 1), repeat=n * nE)]
    else:
        n, nU, nE = 3, 2, 2
        Klist = [frozenset({0, 1})]
        etas = [tuple(tuple(1 if e == 0 else 0 for e in range(nE)) for x in range(n))]
    cells = n * nU * nE
    count = 0
    for vals in itertools.product(range(n), repeat=cells):
        F = [[[vals[(x * nU + u) * nE + e] for e in range(nE)] for u in range(nU)] for x in range(n)]
        for K in Klist:
            for ETA in etas:
                analyse(n, nU, nE, F, K, ETA, C, stats, brute=True)
                count += 1
    labels = {"viab_core_max": "prop:viab_core_max", "viab_stage_finite": "prop:viab_stage_finite",
              "kernel_standard_comparison": "prop:kernel_standard_comparison",
              "robust_nonresponse_viab": "prop:robust_nonresponse_viab", "blockage_dichotomy": "prop:blockage_dichotomy",
              "fr_next_sm": "prop:fr_next_sm", "sd_viab": "lem:sd_viab",
              "nondegeneracy_implication": "prop:nondegeneracy_implication",
              "feasibility_sensitivity_scope": "prop:feasibility_sensitivity_scope", "finite_exit": "lem:finite_exit",
              "sd_robust_nonresponse": "prop:sd_robust_nonresponse", "sd_necessity": "prop:sd_necessity",
              "exterior_blockage": "prop:exterior_blockage", "sd_necessity_fr": "prop:sd_necessity_fr"}
    for k, (cases, prem, bad) in C.items():
        R.check(f"MU_{k}", labels[k], f"MU-{name}", cases, prem, [repr(b)[:300] for b in bad[:3]] if bad else [],
                f"{count} candidate models" + ("; cases = (model, policy) pairs" if k == "finite_exit" else ""),
                "all-models")
    st = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in stats.items()}
    R.add(f"MU_boundary_{name}", ["def:viab_core", "def:robust_response", "def:kernel_all_any", "def:eu_critical_domain"],
          f"MU-{name}", "EXAMPLE_ONLY", count, None, "boundary cases present in the family (counts)", st, "census")
    return count


def family_B(R):
    """existence search for both directions of prop:robust_noninclusion (|E_bg|=1, |O|=2)."""
    n, nU = 2, 2
    found = {}
    tried = 0
    inv_bad = 0
    for vals in itertools.product(range(n), repeat=n * nU * 2):
        F = [[[vals[(x * nU + u) * 2 + o] for o in range(2)] for u in range(nU)] for x in range(n)]
        for gv in itertools.product((0, 1), repeat=2 * n * nU):
            G = [[[gv[(o * n + x) * nU + u] for u in range(nU)] for x in range(n)] for o in range(2)]
            for K in subsets(range(n)):
                for etab in itertools.product((0, 1), repeat=n * 2):
                    ETA = [[etab[x * 2 + o] for o in range(2)] for x in range(n)]
                    tried += 1
                    Ereq = [tuple(o for o in range(2) if ETA[x][o]) for x in range(n)]
                    Kreq = {x for x in K if Ereq[x]}
                    S = set(Kreq)
                    ch = True
                    while ch:
                        ch = False
                        for x in list(S):
                            if not any(all(F[x][u][o] in S for o in Ereq[x]) for u in range(nU)):
                                S.discard(x)
                                ch = True
                    core = S
                    T = {(x, o) for x in K for o in range(2) if ETA[x][o]}
                    ch = True
                    while ch:
                        ch = False
                        for (x, o) in list(T):
                            if not any((F[x][u][o], G[o][x][u]) in T for u in range(nU)):
                                T.discard((x, o))
                                ch = True
                    if not all(any((F[x][u][o], G[o][x][u]) in T for u in range(nU)) for (x, o) in T):
                        inv_bad += 1
                    px = {x for (x, o) in T}
                    if "i" not in found and core - px:
                        found["i"] = {"F": F, "g_O": G, "K": sorted(K), "eta": ETA, "Viab": sorted(core), "piX_resp": sorted(px)}
                    if "ii" not in found and px - core:
                        found["ii"] = {"F": F, "g_O": G, "K": sorted(K), "eta": ETA, "Viab": sorted(core), "piX_resp": sorted(px)}
                    if len(found) == 2:
                        R.add("MU_robust_noninclusion", "prop:robust_noninclusion", "MU-B2", "EXAMPLE_ONLY", tried, None,
                              "witnesses for (i) and (ii) found (existence search; E_bg single point, so b is omitted)",
                              found, "example")
                        R.check("MU_viab_resp_max", "prop:viab_resp_max", "MU-B2", tried, tried, [] if inv_bad == 0 else ["not invariant"],
                                "response kernel invariant on every candidate visited by the search", "all-models (visited)")
                        return
    R.add("MU_robust_noninclusion", "prop:robust_noninclusion", "MU-B2", "NOT_RUN", tried, None,
          f"witnesses not both found: {sorted(found)}")


def main(argv):
    fams = argv or ["A2", "A3", "B2"]
    R = Report("microuniverse")
    for fm in fams:
        print(f"--- family {fm}")
        if fm == "B2":
            family_B(R)
        else:
            family(fm, R)
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
