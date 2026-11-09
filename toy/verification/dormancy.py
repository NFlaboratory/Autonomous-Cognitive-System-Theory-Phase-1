# -*- coding: utf-8 -*-
"""G5 Dormancy ("moss spore", toy convention): (SC-1) and (FT-1) can hold TEMPORARILY, so that
CS / FTS (which include non-recoverability (SC-2) / (FT-2)) differ from (SC-1) / (FT-1).

PARTIAL MODEL with a fixed policy (absorb when it rains and the body is active).  The judgement rules
below are toy conventions fixed before running; the paper leaves them to each target system.

  X   w water {0..3}, c organisation {2 active, 1 dormant (tun), 0 dissociated}, d dry count {0..5}
  U   wait (u_emptyset), absorb
  E   rain {0,1} (background); O single point
  f   w' = min(3, w + 1 + [absorb and c=2]) if rain else max(0, w - 1)
      wet (w' >= 1): c=2 -> 2 ; c=1 -> 2 (revives) ; c=0 -> 1 if d <= D_LIM (reassembles) else 0 ; d' = 0
                     (a dissociated body with d > D_LIM stays dissociated and d stays)
      dry (w' = 0) : d' = min(5, d + 1) ; c=2 -> 1 ; c=1 -> 0 if d' >= D_DISS else 1 ; c=0 -> 0
  Pi  min(c - 2, w - 1)          K = {c = 2, w >= 1}
  eta_moist(x, e) = 1 iff rain = 1 or w >= 2
  Upsilon_adm = {mist}: at one chosen time the step is taken as if it rained (w' >= 1)
Judgement rules (fixed in advance):
  (SC-1)_t : c_t = 0                         (FT-1)_t : c_t <= 1   (all basic and base functions stopped)
  (SC-2)_t : no continuation from t (realised background, own policy; or the same with one mist at
             some time s >= t) has c_s >= 1 for some s > t
  (FT-2)_t : no such continuation has c_s = 2 for some s > t
  CS = (SC-1) and (SC-2); Col = history of CS; T_FT = times up to the first CS;
  FTS = (FT-1) and (FT-2) on T_FT; FT = history of FTS; T_P = {t : FT_t = 0};
  WF_t = 1 iff Col_t = 0 and c_t >= 1.
python3 verification/dormancy.py
"""
import itertools
import os
import sys
from collections import namedtuple, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report  # noqa: E402
from acsjudge.judge import Judge  # noqa: E402

D_DISS, D_LIM, D_CAP = 2, 4, 5
X_ = namedtuple("X", "w c d")
E_ = namedtuple("E", "rain o")
XS = [X_(w, c, d) for w in range(4) for c in range(3) for d in range(D_CAP + 1)]
ES = [E_(r, 0) for r in (0, 1)]
U = ("wait", "absorb")


def step(x, u, rain, mist=False):
    if x.c == 0 and x.d > D_LIM:
        w1 = min(3, x.w + 1) if rain else max(0, x.w - 1)
        return X_(w1, 0, x.d)
    w1 = min(3, x.w + 1 + (1 if (u == "absorb" and x.c == 2) else 0)) if rain else max(0, x.w - 1)
    if mist:
        w1 = max(1, w1)
    if w1 >= 1:
        c1 = {2: 2, 1: 2, 0: 1}[x.c]
        return X_(w1, c1, 0)
    d1 = min(D_CAP, x.d + 1)
    c1 = 1 if x.c == 2 else (0 if (x.c == 1 and d1 >= D_DISS) or x.c == 0 else 1)
    return X_(w1, c1, d1)


def f(x, u, e):
    return step(x, u, e.rain)


def policy(x, rain):
    return "absorb" if (rain and x.c == 2) else "wait"


class _D:
    NAME = "Dormancy"


D = _D()
D.XS, D.U, D.U_EMPTY, D.ES, D.OS, D.I_E = XS, U, "wait", ES, (0,), ("w",)
D.f = f
D.Pi = lambda x: min(x.c - 2, x.w - 1)
D.ETA = {"moist": lambda x, e: 1 if (e.rain == 1 or x.w >= 2) else 0}


def future_c(x, t, pat, mist_at=None):
    """c values at times s > t of the continuation from x_t (exact: stops when (state, phase) repeats)."""
    p = len(pat)
    seen = set()
    out = set()
    s = t
    while True:
        key = (x, s % p, mist_at is not None and s < mist_at)
        if key in seen:
            return out
        seen.add(key)
        r = pat[s % p]
        x = step(x, policy(x, r), r, mist=(mist_at == s))
        s += 1
        out.add(x.c)


def mist_times(x, t, pat):
    """every time s >= t at which the realised continuation visits a new (state, phase): a mist at a later
    time with the same (state, phase) gives the same continuation, so these cover all one-mist continuations."""
    p = len(pat)
    seen = set()
    s = t
    out = []
    while (x, s % p) not in seen:
        seen.add((x, s % p))
        out.append(s)
        r = pat[s % p]
        x = step(x, policy(x, r), r)
        s += 1
    return out


def judge_run(x0, pat, T, use_mist=True):
    p = len(pat)
    xs = [x0]
    for t in range(T):
        r = pat[t % p]
        xs.append(step(xs[-1], policy(xs[-1], r), r))
    rows = []
    col = ft = 0
    first_cs = None
    for t in range(T):
        x = xs[t]
        conts = [future_c(x, t, pat)]
        if use_mist:
            conts += [future_c(x, t, pat, mist_at=s) for s in mist_times(x, t, pat)]
        sc1 = x.c == 0
        sc2 = sc1 and not any(any(c >= 1 for c in fc) for fc in conts)
        cs = int(sc1 and sc2)
        in_TFT = first_cs is None
        ft1 = x.c <= 1
        ft2 = ft1 and not any(2 in fc for fc in conts)
        fts = int(ft1 and ft2) if in_TFT else None
        if cs and first_cs is None:
            first_cs = t
        col = 1 if (col or cs) else 0
        ft = 1 if (ft or fts == 1) else 0
        rows.append({"t": t, "x": x, "SC1": sc1, "CS": cs, "Col": col, "T_FT": in_TFT, "FT1": ft1, "FTS": fts,
                     "FT": ft, "T_P": ft == 0, "WF": int(col == 0 and x.c >= 1),
                     "real_c": {xs[s].c for s in range(t + 1, T + 1)}, "rain": pat[t % p]})
    return rows


def main():
    R = Report("dormancy")
    J = Judge(D)
    pats = [pat for p in range(1, 7) for pat in itertools.product((0, 1), repeat=p)]
    starts = [X_(w, 2, 0) for w in (1, 2, 3)] + [X_(0, 1, 1), X_(0, 0, 3), X_(0, 0, D_LIM), X_(0, 0, D_LIM + 1)]
    T = 30
    C = Counter()
    bad = {k: [] for k in ("reest_CS", "reest_FTS", "order", "tp_down", "undef", "hist")}
    for x0 in starts:
        for pat in pats:
            rows = judge_run(x0, pat, T)
            rows_nomist = judge_run(x0, pat, T, use_mist=False)
            for a, b in zip(rows, rows_nomist):
                if a["CS"] != b["CS"]:
                    C["CS_differs_without_Upsilon"] += 1
            for i, r in enumerate(rows):
                C["times"] += 1
                # realized re-establishment
                if r["SC1"] and any(c >= 1 for c in r["real_c"]):
                    C["prem_reest_CS"] += 1
                    if r["CS"]:
                        bad["reest_CS"].append((x0, pat, r["t"]))
                if r["T_FT"] and r["FT1"] and 2 in r["real_c"]:
                    C["prem_reest_FTS"] += 1
                    if r["FTS"]:
                        bad["reest_FTS"].append((x0, pat, r["t"]))
                if r["FT1"] and r["FTS"] == 0:
                    C["FT1_but_FTS0"] += 1
                if r["SC1"] and not r["CS"]:
                    C["SC1_but_CS0"] += 1
                    if not any(c >= 1 for c in r["real_c"]):
                        C["SC1_CS0_recoverable_only_with_mist"] += 1
                if r["x"].c == 0 and r["x"].d == D_LIM:
                    C["boundary_d_eq_DLIM"] += 1
                # T_P downward closed and Col=0 on T_P ; principle predicates only on T_P
                if r["T_P"] and (r["Col"] or not all(q["T_P"] for q in rows[:i])):
                    bad["tp_down"].append((x0, pat, r["t"]))
                # histories never revert
                if i and (rows[i - 1]["Col"] > r["Col"] or rows[i - 1]["FT"] > r["FT"]):
                    bad["hist"].append((x0, pat, r["t"]))
                if r["T_P"]:
                    C["defined_principle_times"] += 1
                else:
                    C["undefined_principle_times"] += 1
            # termination order
            if rows[-1]["Col"]:
                C["runs_with_Col"] += 1
                tc = min(r["t"] for r in rows if r["CS"])
                for r in rows:
                    if not r["Col"]:
                        continue
                    t = r["t"]
                    ok = rows[tc]["T_FT"] and rows[tc]["FTS"] == 1 and r["FT"] == 1 and \
                        ((t <= tc) or not r["T_FT"]) and r["WF"] == 0
                    if not ok:
                        bad["order"].append((x0, pat, t))
            if any(r["FT"] and not r["Col"] for r in rows):
                C["runs_FT_before_or_without_Col"] += 1
            if any(r["FT1"] and r["FTS"] == 0 for r in rows) and any(r["x"].c == 2 for r in rows[1:]):
                C["runs_temporary_stop_then_revival"] += 1
    R.check("D1_realized_reestablishment_CS", "prop:realized_reestablishment", "Dormancy", C["times"],
            C["prem_reest_CS"], bad["reest_CS"], "(SC-1) at t and re-established later on the realised path => CS_t = 0")
    R.check("D1_realized_reestablishment_FTS", "prop:realized_reestablishment", "Dormancy", C["times"],
            C["prem_reest_FTS"], bad["reest_FTS"], "(FT-1) at t in T_FT and revival later on the realised path => FTS_t = 0")
    R.check("D2_termination_order", "prop:termination_order", "Dormancy", C["runs_with_Col"], C["runs_with_Col"],
            bad["order"], "(i) FTS=1 at t_C, (ii) FT=1, (iii) no new FT judgement after t_C, (iv) WF=0 when Col=1")
    R.check("D3_principle_time_domain_down", ["lem:principle_time_domain_down", "def:principle_time_domain"], "Dormancy",
            C["times"], C["defined_principle_times"], bad["tp_down"], "T_P is downward closed and Col=0 on T_P")
    R.check("D4_histories", ["def:collapse", "def:functional_termination"], "Dormancy", C["times"], C["times"], bad["hist"],
            "Col and FT never revert")
    R.add("D5_census", ["def:collapse", "def:functional_termination", "def:wf_realization"], "Dormancy", "EXAMPLE_ONLY",
          C["times"], None, "temporary (SC-1)/(FT-1), Upsilon-dependence and threshold cases (counts)", dict(C), "census")
    print(dict(C))
    # sec.3 sets of the domain (as a partial model)
    core = J.viab_core()
    R.add("D6_domain_sets", ["def:viab_core", "def:eu_critical_domain"], "Dormancy", "EXAMPLE_ONLY", len(XS), None,
          f"|K|={sum(1 for x in XS if D.Pi(x) >= 0)}, |Viab|={len(core)}", None, "census")
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
