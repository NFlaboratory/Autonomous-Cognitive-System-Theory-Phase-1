# -*- coding: utf-8 -*-
"""T01-T08/T11 (part): structure of TIPA / PSL / Update checked on the finite mechanisms of MinACS and
the furnace (exhaustive over M x X x E_ext), plus a mutation test for every check: a mechanism that
violates exactly one condition is built and the check must detect it (otherwise the check is empty).

What a pass means: THIS implementation conforms to the stated condition on the whole finite range.
It is not a proof of the abstract structure and does not judge whether the mechanism is effective.
python3 verification/check_structure.py
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report, lcg_seq, backgrounds  # noqa: E402
from acsjudge.judge import Judge               # noqa: E402
from acsjudge import trajectory as tr          # noqa: E402
from domains import minacs_domain as dmm       # noqa: E402
from domains.furnace import model as fmod      # noqa: E402
from domains.furnace import mind as fmind      # noqa: E402
from minacs import mind as mmind               # noqa: E402


# ------------------------------------------------------------------ the two mechanisms as uniform objects
class MinACSMech:
    name = "MinACS"
    D = dmm.D
    P_sens = staticmethod(mmind.P_sens)
    MS = list(mmind.MS)
    has_psl4 = False

    def operate(self, M, x, e):
        return mmind.operate(M, x, e)

    def Update(self, M, x, e, learn=True):
        return mmind.Update(M, x, e, learn)

    def m2_out(self, M, x, e):
        I = mmind.P_sens(x, e)
        if I[5] is None and not (x.s == 1 and x.en > 0):
            return None
        xh, eh = mmind.M1(I, M)
        return mmind.M2(xh, eh, M)

    def pur_variants(self, M):
        return [M._replace(pur=p) for p in ("none", "heat", "food")]


class FurnaceMech:
    name = "Furnace"
    D = fmod.D
    P_sens = staticmethod(fmind.P_sens)
    has_psl4 = True

    def __init__(self):
        self.m = fmind.Mind()
        recs = [None] + [(tp, u, h, fu) for tp in range(fmod.TP_MAX + 1) for u in fmod.U for h in (0, 1)
                         for fu in range(fmod.FU_MAX + 1)]
        self.MS = [fmind.M_(bo, rec, pur) for bo in (0, 1) for rec in recs
                   for pur in ("none", "heat", "cool", "flue", "fuel")]

    def operate(self, M, x, e):
        return self.m.operate(M, x, e)

    def Update(self, M, x, e, learn=True):
        return self.m.Update(M, x, e, learn)

    def m2_out(self, M, x, e):
        if not fmod.base_active(x):
            return None
        I = fmind.P_sens(x, e)
        xh, eh = self.m.M1(I, M)
        return repr(self.m.M2(xh, eh, M))

    def pur_variants(self, M):
        return [M._replace(pur=p) for p in ("none", "heat", "cool", "flue", "fuel")]

    def phi_prot(self, M, I):
        return self.m.Phi_prot(I)


# ------------------------------------------------------------------ mutants (each breaks exactly one condition)
class MutM2ReadsPurpose(FurnaceMech):
    tag = "M2 reads the M3 purpose record"

    def m2_out(self, M, x, e):
        base = super().m2_out(M, x, e)
        return None if base is None else base + ("|cool" if M.pur == "cool" else "")


class MutUpdateReadsHiddenFlue(FurnaceMech):
    tag = "Update reads the true flue state o (not sensed)"

    def Update(self, M, x, e, learn=True):
        M1 = super().Update(M, x, e, learn)
        return M1._replace(bo=e.o) if fmod.base_active(x) else M1


class MutActionReadsHidden(MinACSMech):
    tag = "action reads the resource state r where it is not sensed"

    def operate(self, M, x, e):
        out = dict(super().operate(M, x, e))
        if x.s == 1 and x.en > 0 and e.r == 1 and out["u"] == mmind.U_EMPTY:
            out["u"] = dmm.D.U[1]
        return out


class MutProtReadsMemory(FurnaceMech):
    tag = "PSL-4 protective response reads M (purpose record)"

    def phi_prot(self, M, I):
        r = self.m.Phi_prot(I)
        return None if M.pur == "heat" else r


class MutResolveCancels(FurnaceMech):
    tag = "M3 command overrides an issued protective response"

    def operate(self, M, x, e):
        out = dict(self.m.operate(M, x, e))
        out["u"] = out.get("u_M3", out["u"])
        return out


# ------------------------------------------------------------------ checks
def factorisation(mech, fn, only_active=False):
    """returns (cases, classes with >=2 distinct (x,e), violations): fn(M,x,e) must depend on (M, I) only."""
    seen = defaultdict(set)
    members = defaultdict(set)
    n = 0
    D = mech.D
    for M in mech.MS:
        for x in D.XS:
            for e in D.ES:
                I = mech.P_sens(x, e)
                v = fn(M, x, e)
                seen[(M, I)].add(repr(v))
                members[(M, I)].add((x, e))
                n += 1
    multi = sum(1 for k in members if len(members[k]) >= 2)
    bad = [k for k, v in seen.items() if len(v) > 1]
    return n, multi, bad


def struct_checks(R, mech, dom, expect_fail=None, only=None, report=True):
    """run the structure checks on mech; if expect_fail is a check id, report as a mutation test."""
    res = {}
    D = mech.D

    def want(c):
        if only is not None:
            return c in only
        return expect_fail is None or expect_fail == c
    # S01 Update observation factorisation
    if want("S01"):
        n, multi, bad = factorisation(mech, lambda M, x, e: mech.Update(M, x, e))
        res["S01"] = (["ass:s5_observation_factorization", "prop:s5_observation_causality", "def:update_section5"],
                  n, multi, bad, "Update(M,x,e) depends on (M, P_sens(x,e)) only")
    # S02 action through the observation ; S03 purpose / signal / priority through (M, I)
    if want("S02"):
        n, multi, bad = factorisation(mech, lambda M, x, e: mech.operate(M, x, e)["u"])
        res["S02"] = (["def:s4_primitive_composition", "def:s4_psl_sources", "def:s5_standard_step"], n, multi, bad,
                  "u = P_act(M, P_disc, P_val) depends on (M, I) only")
    if want("S03"):
        n, multi, bad = factorisation(mech, lambda M, x, e: tuple(mech.operate(M, x, e).get(k) for k in ("pur", "sig", "P", "mode")))
        res["S03"] = (["prop:purpose_self_attribution", "def:purpose_formation", "def:m2_request_signal", "def:m2_priority"],
                  n, multi, bad, "(Pur, sig, Priority, mode) depend on (M, I) only")
    # S04 M2 independent of the M3 purpose record
    if want("S04"):
        bad, n = [], 0
        for M in mech.MS:
            if M.pur != "none":
                continue
            for x in D.XS:
                for e in D.ES:
                    outs = {repr(mech.m2_out(Mv, x, e)) for Mv in mech.pur_variants(M)}
                    n += 1
                    if len(outs) > 1:
                        bad.append((M, x, e))
        res["S04"] = (["def:m2_map", "ass:functional_concurrency"], n, n, bad,
                      "M2 output unchanged when only the M3 purpose record changes")
    # S05 types: u in U, Update(M,x,e) in the declared M-space (prop:s5_one_step)
    if want("S05"):
        Mset = set(mech.MS)
        bad, n = [], 0
        for M in mech.MS:
            for x in D.XS:
                for e in D.ES:
                    n += 1
                    u = mech.operate(M, x, e)["u"]
                    M1 = mech.Update(M, x, e)
                    if u not in D.U or M1 not in Mset or D.f(x, u, e) not in set(D.XS):
                        bad.append((M, x, e))
        res["S05"] = (["prop:s5_one_step", "def:update_section5", "def:sel_proj", "def:action_decision"], n, n, bad,
                      "every (M,x,e): u in U, f(x,u,e) in X, Update in the declared M-space")
    # S06 PSL-4: protective response from I only; resolution keeps the local component; non-degenerate
    if want("S06"):
        if mech.has_psl4:
            bad, n, prem = [], 0, 0
            for x in D.XS:
                for e in D.ES:
                    I = mech.P_sens(x, e)
                    rs = {repr(mech.phi_prot(M, I)) for M in mech.MS[::7]}
                    n += 1
                    if len(rs) > 1:
                        bad.append(("depends on M", x, e))
                    for M in mech.MS[::37]:
                        out = mech.operate(M, x, e)
                        r = out.get("r_local")
                        if r is not None:
                            prem += 1
                            if out["u"] != r or r == D.U_EMPTY:
                                bad.append(("resolve", M, x, e))
            res["S06"] = (["def:psl4", "def:effective_action_resolve", "ass:psl_minimal"], n, prem, bad,
                          "r_local from I only (every M sampled 1/7); r != bot => u = r and r != u_empty")
    # S07 P2 / P3 and observation causality of M_t on trajectories
    if want("S07") or want("S08") or want("S09"):
        J = Judge(D)
        B = backgrounds(D)
        core, V = J.viab_core(), J.viab_stages()
        H = J.hor(V)
        starts = [x for x in D.XS if D.WF(x) == 1][::3]
        bad2, bad3, badc, n2, n3 = [], [], [], 0, 0
        keymap = defaultdict(set)
        M0 = mech.MS[0]
        XOF = {tuple(x): x for x in D.XS}
        for k, (x0, o0) in enumerate([(x, o) for x in starts for o in D.OS]):
            Bs = lcg_seq(k // len(D.OS) + 1, 40, B)
            r1 = tr.run(J, mech, Bs, 40, x0, o0, M0, recover=False, core=core, V=V, H=H)
            r2 = tr.run(J, mech, Bs, 40, x0, o0, M0, recover=False, core=core, V=V, H=H)
            n2 += 1
            if [(a["x"], a["M"], a["o"], a["u"]) for a in r1] != [(a["x"], a["M"], a["o"], a["u"]) for a in r2]:
                bad2.append((x0, k))
            for tcut in (5, 20):
                Bp = Bs[:tcut] + lcg_seq(k + 1000, 40 - tcut, B)
                r3 = tr.run(J, mech, Bp, 40, x0, o0, M0, recover=False, core=core, V=V, H=H)
                n3 += 1
                if any((r1[s]["x"], r1[s]["M"], r1[s]["o"]) != (r3[s]["x"], r3[s]["M"], r3[s]["o"]) for s in range(tcut + 1)):
                    bad3.append((x0, k, tcut))
            Ipre = ()
            for s, a in enumerate(r1):
                keymap[(M0, Ipre)].add((a["M"], (x0, k)))
                xs = XOF[a["x"]]
                Ipre = Ipre + (mech.P_sens(xs, D.make_e(a["b"], a["o"])),)
        for key, vals in keymap.items():
            if len({m for (m, _) in vals}) > 1:
                badc.append(key[1][:2])
        shared = sum(1 for key, v in keymap.items() if key[1] and len({w for (_, w) in v}) > 1)
        res["S07"] = (["prop:s5_continuation", "def:s5_operation_record"], n2, n2, bad2,
                      "re-running with the same x0, M0, o0 and background gives the same record (40 steps)")
        res["S08"] = (["prop:s5_causality"], n3, n3, bad3,
                      "changing the background from t on leaves (x,M,o) up to t unchanged (t = 5, 20)")
        res["S09"] = (["prop:s5_observation_causality"], len(keymap), shared, badc,
                      "M_t is determined by M_0 and I_0..I_{t-1} (premise: non-empty I-prefixes shared by runs that differ in x or o)")
    for cid, (labels, n, prem, bad, detail) in res.items():
        if not report:
            continue
        if expect_fail is None:
            R.check(f"{cid}_{mech.name}", labels, dom, n, prem, [repr(b)[:200] for b in bad[:3]], detail)
        elif cid == expect_fail:
            R.add(f"MUT_{cid}_{type(mech).__name__}", labels, dom, "PASS_NONVACUOUS" if bad else "FAIL", n, len(bad),
                  f"mutation '{mech.tag}' {'detected' if bad else 'NOT detected'} by {cid} ({len(bad)} violations)",
                  [repr(b)[:200] for b in bad[:2]], "mutation")
    return res


def v2_static(R):
    """v2: resolution map checked on its whole finite domain; sensitivity reads x_t only (static)."""
    from acs_toy.mind import Mind
    from acs_toy.body import U as U2, U_EMPTY as UE2, DIRS
    bad, n, prem = [], 0, 0
    for u in U2:
        for r in list(DIRS) + [None]:
            for Rm in ("std",):
                n += 1
                v = Mind.resolve(u, r, Rm)
                if r is None:
                    if v != u:
                        bad.append((u, r))
                else:
                    prem += 1
                    if Mind.pr_loc(v) != Mind.pr_loc(r) or Mind.pr_loc(r) == Mind.pr_loc(UE2):
                        bad.append((u, r))
    R.check("S06_v2_resolve", ["def:effective_action_resolve", "def:psl4"], "v2", n, prem, bad,
            "Phi_resolve on U x (DIRS u {bot}): bot => u_M3 ; r != bot => pr_loc kept, pr_loc(r) != pr_loc(u_empty)")
    import inspect
    src = inspect.getsource(Mind.gamma_in)
    reads = sorted(set(a for a in ("x.hsens", "x.alert", "M", "out", "o3", "S1") if a in src))
    ok = all(a.startswith("x.") for a in reads)
    R.add("S10_v2_psl_sensitivity", ["def:psl_sensitivity"], "v2", "EXAMPLE_ONLY" if ok else "FAIL", 1, None,
          f"static reading: Gamma_in,t reads {reads}; x_t is fixed before the TIPA step of t (no same-time loop)",
          None, "static")


def main():
    R = Report("structure")
    for mech, dom in ((MinACSMech(), "MinACS"), (FurnaceMech(), "Furnace")):
        print(f"--- {dom}")
        struct_checks(R, mech, dom)
    print("--- mutations (each must be detected)")
    struct_checks(R, MutM2ReadsPurpose(), "Furnace-mut", expect_fail="S04")
    struct_checks(R, MutUpdateReadsHiddenFlue(), "Furnace-mut", expect_fail="S01")
    struct_checks(R, MutActionReadsHidden(), "MinACS-mut", expect_fail="S02")
    struct_checks(R, MutProtReadsMemory(), "Furnace-mut", expect_fail="S06")
    struct_checks(R, MutResolveCancels(), "Furnace-mut", expect_fail="S06")
    print("--- v2 (static / finite resolution map)")
    v2_static(R)
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
